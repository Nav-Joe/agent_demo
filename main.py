import logging
import time
import warnings
from collections.abc import Generator
from datetime import datetime

import gradio as gr

from agents.llm import get_llm
from agents.outing import OutingAgent
from agents.proactive import ProactiveAgent
from agents.router import IntentRouter
from agents.suntime import SunTimeAgent
from agents.weather import WeatherAgent
from config import settings
from logging_config import setup_logging
from ollama_health import check_ollama_connection

warnings.filterwarnings("ignore", category=ResourceWarning)

logger = logging.getLogger(__name__)


class HomeAI:
    def __init__(self):
        self.router = IntentRouter()
        self.agents = {
            "weather": WeatherAgent(),
            "outing": OutingAgent(),
            "suntime": SunTimeAgent(),
            "proactive": ProactiveAgent(),
        }
        self.history: list[dict[str, str]] = []
        self.last_user_time = time.time()

    def chat_stream(self, user_input: str) -> Generator[str, None, None]:
        """流式生成回复并更新对话历史。"""
        self.last_user_time = time.time()
        intent = self.router.route(user_input)
        logger.info("意图识别: %s -> %s", user_input, intent)

        full_response = ""

        if intent in self.agents:
            full_response = self.agents[intent].run(user_input)
            yield full_response
        else:
            llm = get_llm(temperature=0.5)
            for chunk in llm.stream(user_input):
                if chunk.content:
                    full_response += chunk.content
                    yield chunk.content

        self._append_history(user_input, full_response)

    def _append_history(self, user_input: str, response: str) -> None:
        self.history.append({"role": "user", "content": user_input})
        self.history.append({"role": "assistant", "content": response})
        if len(self.history) > 20:
            self.history = self.history[-10:]

    def check_proactive(self, force: bool = False) -> str:
        silence_minutes = int((time.time() - self.last_user_time) / 60)

        if not force and silence_minutes < settings.proactive_silence_minutes:
            return f"用户活跃中（沉默{silence_minutes}分钟）"

        current_time = datetime.now().strftime("%H:%M")
        check_minutes = 999 if force else silence_minutes
        result = self.agents["proactive"].check(self.history, current_time, check_minutes)

        if result.get("should_proactive"):
            topic = result.get("topic", "有什么可以帮您的吗？")
            proactive_msg = f"💡 主动提醒：{topic}"
            self.history.append({"role": "assistant", "content": proactive_msg})
            return f"✅ 已触发主动对话：{topic}（原因：{result.get('reason', '')}）"

        return f"主动对话检查完成，暂无需发起（{result.get('reason', '')}）"


def create_ui() -> gr.Blocks:
    home_ai = HomeAI()

    def respond(message: str, chat_history: list):
        if not message.strip():
            return "", chat_history

        chat_history = chat_history + [
            {"role": "user", "content": message},
            {"role": "assistant", "content": ""},
        ]

        for chunk in home_ai.chat_stream(message):
            chat_history[-1]["content"] += chunk
            yield "", chat_history

    def clear_history():
        home_ai.history.clear()
        home_ai.last_user_time = time.time()
        return []

    def refresh_proactive():
        return home_ai.check_proactive(force=False)

    def test_proactive():
        status = home_ai.check_proactive(force=True)
        return status, home_ai.history[-6:]

    with gr.Blocks(title="本地家居AI助手") as demo:
        gr.Markdown("# 🏠 本地家居AI助手")
        gr.Markdown(
            f"模型：`{settings.ollama_model}` · "
            "支持：天气查询 | 出行建议 | 日出日落 | 主动对话提醒 | 闲聊流式输出"
        )

        chatbot = gr.Chatbot(height=420)
        msg = gr.Textbox(
            label="输入消息",
            placeholder="今天福州天气怎么样？适合出门跑步吗？",
            lines=2,
        )

        with gr.Row():
            clear = gr.Button("清空对话", scale=1)
            test_btn = gr.Button("🧪 测试主动对话", scale=1)

        msg.submit(respond, [msg, chatbot], [msg, chatbot])
        clear.click(clear_history, None, chatbot, queue=False)

        proactive_status = gr.Textbox(
            label="主动对话状态",
            value="等待中...",
            interactive=False,
        )
        test_btn.click(fn=test_proactive, outputs=[proactive_status, chatbot])

        timer = gr.Timer(value=30, active=True)
        timer.tick(fn=refresh_proactive, outputs=proactive_status)

    return demo


if __name__ == "__main__":
    setup_logging()
    if not check_ollama_connection():
        raise SystemExit(1)
    demo = create_ui()
    demo.launch(
        server_name=settings.gradio_server_name,
        server_port=settings.port,
        show_error=True,
        theme=gr.themes.Soft(),
    )

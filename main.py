import gradio as gr
from agents.router import IntentRouter
from agents.weather import WeatherAgent
from agents.outing import OutingAgent
from agents.suntime import SunTimeAgent
from agents.proactive import ProactiveAgent
from datetime import datetime
import time
import warnings
import os

warnings.filterwarnings("ignore", category=ResourceWarning)

class HomeAI:
    def __init__(self):
        self.router = IntentRouter()
        self.agents = {
            "weather": WeatherAgent(),
            "outing": OutingAgent(),
            "suntime": SunTimeAgent(),
            "chat": None,
            "proactive": ProactiveAgent()
        }
        self.history = []
        self.last_user_time = time.time()
    
    def chat(self, user_input: str) -> str:
        self.last_user_time = time.time()
        
        intent = self.router.route(user_input)
        print(f"[意图识别] {user_input} -> {intent}")
        
        if intent in self.agents and self.agents[intent] and intent != "chat":
            response = self.agents[intent].run(user_input)
        else:
            response = self._base_chat(user_input)
        
        self.history.append({"role": "user", "content": user_input})
        self.history.append({"role": "assistant", "content": response})
        
        if len(self.history) > 20:
            self.history = self.history[-10:]
        
        return response
    
    def check_proactive(self) -> str:
        silence_minutes = int((time.time() - self.last_user_time) / 60)
        
        if silence_minutes < 3:
            return f"用户活跃中（沉默{silence_minutes}分钟）"
        
        current_time = datetime.now().strftime("%H:%M")
        result = self.agents["proactive"].check(self.history, current_time, silence_minutes)
        
        if result.get("should_proactive"):
            topic = result.get("topic", "有什么可以帮您的吗？")
            return f"💡 建议主动发起：{topic}（原因：{result.get('reason', '')}）"
        else:
            return f"沉默{silence_minutes}分钟，无需主动（{result.get('reason', '')}）"
    
    def _base_chat(self, query: str) -> str:
        from langchain_ollama import ChatOllama
        llm = ChatOllama(model="qwen2.5:3b")
        return llm.invoke(query).content
    def check_proactive(self, force: bool = False) -> str:
        silence_minutes = int((time.time() - self.last_user_time) / 60)
        
        # 强制测试模式：绕过3分钟限制
        if not force and silence_minutes < 3:
            return f"用户活跃中（沉默{silence_minutes}分钟）"
        
        current_time = datetime.now().strftime("%H:%M")
        # 强制模式给一个大沉默时间，让Agent必须做判断
        check_minutes = 999 if force else silence_minutes
        result = self.agents["proactive"].check(self.history, current_time, check_minutes)
        
        if result.get("should_proactive"):
            topic = result.get("topic", "有什么可以帮您的吗？")
            # 把主动消息写进历史，这样下次刷新聊天框能看到
            proactive_msg = f"💡 主动提醒：{topic}"
            self.history.append({"role": "assistant", "content": proactive_msg})
            return f"✅ 已触发主动对话：{topic}（原因：{result.get('reason', '')}）"
        else:
            return f"主动对话检查完成，暂无需发起（{result.get('reason', '')}）"

def create_ui():
    home_ai = HomeAI()
    
    def respond(message, chat_history):
        if not message.strip():
            return "", chat_history
        bot_message = home_ai.chat(message)
        chat_history.append({"role": "user", "content": message})
        chat_history.append({"role": "assistant", "content": bot_message})
        return "", chat_history
    
    def clear_history():
        home_ai.history.clear()
        home_ai.last_user_time = time.time()
        return []
    
    def refresh_proactive():
        return home_ai.check_proactive(force=False)
    
    def test_proactive():
        # 强制触发，并把主动消息刷到聊天框
        status = home_ai.check_proactive(force=True)
        # 返回状态和当前历史（让聊天框更新）
        return status, home_ai.history[-6:]  # 只显示最近几条避免太长
    
    with gr.Blocks(title="本地家居AI助手") as demo:
        gr.Markdown("# 🏠 本地家居AI助手（Ollama qwen2.5:3b）")
        gr.Markdown("支持：天气查询 | 出行建议 | 日出日落 | 主动对话提醒")
        
        chatbot = gr.Chatbot(height=400)
        msg = gr.Textbox(label="输入消息", placeholder="今天福州天气怎么样？")
        
        with gr.Row():
            clear = gr.Button("清空对话")
            test_btn = gr.Button("🧪 测试主动对话（立即触发）")
        
        msg.submit(respond, [msg, chatbot], [msg, chatbot])
        clear.click(clear_history, None, chatbot, queue=False)
        
        proactive_status = gr.Textbox(
            label="主动对话状态", 
            value="等待中...", 
            interactive=False
        )
        test_btn.click(
            fn=test_proactive,
            outputs=[proactive_status, chatbot]
        )
        
        # 自动定时器（每30秒后台检查）
        timer = gr.Timer(value=30, active=True)
        timer.tick(fn=refresh_proactive, outputs=proactive_status)
    
    return demo

if __name__ == "__main__":
    demo = create_ui()
    server_name = os.getenv("GRADIO_SERVER_NAME", "0.0.0.0")
    server_port = int(os.getenv("PORT", "7860"))
    demo.launch(
        server_name=server_name,
        server_port=server_port,
        show_error=True
    )

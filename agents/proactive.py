# agents/proactive.py
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
import json
from datetime import datetime

class ProactiveAgent:
    def __init__(self):
        self.llm = ChatOllama(model="qwen2.5:3b", temperature=0.3)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """分析对话上下文，判断AI是否需要主动发起对话。
考虑因素：
1. 用户沉默时长（如果超过合理时间，主动提醒或问候）
2. 上次对话是否有未解决问题
3. 时间敏感性（如天气突变、日程提醒）
4. 用户是否表现出需要陪伴或帮助的意图但未明确说出

输出严格的JSON格式，不要有任何其他文字：
{{"should_proactive": true/false, "delay_minutes": 数字(0-60), "topic": "主动发起的话题", "reason": "判断原因"}}"""),
            ("human", "对话历史（最近5轮）：{history}\n当前时间：{current_time}\n用户已沉默时间：{silence_minutes}分钟")
        ])
    
    def run(self, query: str) -> str:
        """统一接口：把用户关于主动对话的询问，转成一次即时检查"""
        current_time = datetime.now().strftime("%H:%M")
        result = self.check([], current_time, 999)  # 强制检查，无视沉默时间
        
        if result.get("should_proactive"):
            return f"💡 主动对话建议：{result.get('topic', '')}（原因：{result.get('reason', '')}）"
        else:
            return f"🤔 暂无需主动发起对话（{result.get('reason', '')}）"
    
    def check(self, history: list, current_time: str, silence_minutes: int = 5) -> dict:
        history_str = str(history[-5:]) if history else "无对话历史"
        
        chain = self.prompt | self.llm
        result = chain.invoke({
            "history": history_str,
            "current_time": current_time,
            "silence_minutes": str(silence_minutes)
        })
        
        try:
            content = result.content.strip()
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()
            return json.loads(content)
        except Exception as e:
            return {
                "should_proactive": False,
                "delay_minutes": 0,
                "topic": "",
                "reason": f"解析失败: {str(e)}"
            }

# test
if __name__ == "__main__":
    agent = ProactiveAgent()
    print(agent.run("你什么时候会主动说话"))

import os
from tavily import TavilyClient
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from config import config

class WeatherAgent:
    def __init__(self):
        self.llm = ChatOllama(model="qwen2.5:3b", temperature=0.1)
        # 从环境变量读取 API key
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            raise ValueError("请设置环境变量 TAVILY_API_KEY，获取地址：https://tavily.com")
        self.client = TavilyClient(api_key=config.TAVILY_API_KEY)
    
    def run(self, query: str) -> str:
        city = self._extract_city(query)
        search_results = self._search_weather(city)
        #print(search_results)
        
        # 兜底处理
        if not search_results:
            return f"⚠️ 暂时无法获取{city}的实时天气信息，建议查看天气APP。"
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"""你是{city}的天气助手。严格基于以下搜索结果回答，禁止编造。
必须包含：温度、天气状况、穿衣建议。如果信息不足，如实说明。"""),
            ("human", f"用户问题：{query}\n\n搜索结果：{search_results}")
        ])
        
        chain = prompt | self.llm
        return chain.invoke({}).content
    
    def _search_weather(self, city: str) -> str:
        try:
            response = self.client.search(
                query=f"{city} 今天天气 温度 穿衣",
                search_depth="basic",  # "basic" 或 "advanced"
                max_results=3,
                include_answer=True  # 让 Tavily 直接生成摘要
            )
            # 拼接结果
            results = []
            for r in response.get("results", []):
                title = r.get("title", "")
                content = r.get("content", "")
                if title and content:
                    results.append(f"[{title}] {content}")
            
            # 如果 Tavily 生成了 answer，也加上
            answer = response.get("answer", "")
            if answer:
                results.insert(0, f"[Tavily智能摘要] {answer}")
            
            return "\n\n".join(results)
        except Exception as e:
            print(f"Tavily搜索失败: {e}")
            return ""
    
    def _extract_city(self, query: str) -> str:
        cities = ["福州", "厦门", "漳州", "泉州", "北京", "上海", "安溪", "连江"]
        for c in cities:
            if c in query:
                return c
        return "福州"
# test
if __name__ == "__main__":
    agent = WeatherAgent()
    print(agent.run("福州今天天气怎么样"))

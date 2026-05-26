from agents.weather import WeatherAgent
from agents.suntime import SunTimeAgent
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

class OutingAgent:
    def __init__(self):
        self.weather = WeatherAgent()
        self.sun = SunTimeAgent()
        self.llm = ChatOllama(model="qwen2.5:3b", temperature=0.3)
    
    def run(self, query: str) -> str:
        weather_info = self.weather._search_weather(self.weather._extract_city(query))
        sun_info = self.sun.run(query)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是出行顾问。基于天气和日出日落信息，给出今日出行建议。
考虑：温度适宜度、降雨概率、紫外线强度、时间段选择。
语气亲切，给出具体建议（如"建议上午9-11点去公园"）。
如果天气信息获取失败，请诚实告知，并基于常识给出一般性建议。"""),
            ("human", f"用户问题：{query}\n天气信息：{weather_info}\n光照信息：{sun_info}")
        ])
        
        chain = prompt | self.llm
        return chain.invoke({}).content

# test
if __name__ == "__main__":
    agent = OutingAgent()
    print(agent.run("今天适合去海边吗"))

import logging
from concurrent.futures import ThreadPoolExecutor

from langchain_core.prompts import ChatPromptTemplate

from agents.cities import extract_city
from agents.llm import get_llm
from agents.suntime import SunTimeAgent
from agents.weather import WeatherAgent

logger = logging.getLogger(__name__)


class OutingAgent:
    def __init__(self):
        self.weather = WeatherAgent()
        self.sun = SunTimeAgent()
        self.llm = get_llm(temperature=0.3)

    def run(self, query: str) -> str:
        city = extract_city(query)

        with ThreadPoolExecutor(max_workers=2) as executor:
            weather_future = executor.submit(self.weather._search_weather, city)
            sun_future = executor.submit(self.sun.run, query)
            weather_info = weather_future.result()
            sun_info = sun_future.result()

        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是出行顾问。基于天气和日出日落信息，给出今日出行建议。
考虑：温度适宜度、降雨概率、紫外线强度、时间段选择。
语气亲切，给出具体建议（如"建议上午9-11点去公园"）。
如果天气信息获取失败，请诚实告知，并基于常识给出一般性建议。"""),
            ("human", "用户问题：{query}\n天气信息：{weather_info}\n光照信息：{sun_info}"),
        ])

        chain = prompt | self.llm
        return chain.invoke({
            "query": query,
            "weather_info": weather_info or "（天气数据暂不可用）",
            "sun_info": sun_info,
        }).content


if __name__ == "__main__":
    from logging_config import setup_logging

    setup_logging()
    agent = OutingAgent()
    print(agent.run("今天适合去海边吗"))

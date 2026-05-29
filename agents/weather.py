import logging

from langchain_core.prompts import ChatPromptTemplate
from tavily import TavilyClient

from agents.cities import extract_city
from agents.llm import get_llm
from config import settings

logger = logging.getLogger(__name__)


class WeatherAgent:
    def __init__(self):
        self.llm = get_llm(temperature=0.1)
        self.client = TavilyClient(api_key=settings.tavily_api_key)

    def run(self, query: str) -> str:
        city = extract_city(query)
        search_results = self._search_weather(city)

        if not search_results:
            return f"⚠️ 暂时无法获取{city}的实时天气信息，建议查看天气APP。"

        if not self._validate_city_in_results(city, search_results):
            logger.warning("搜索结果未包含目标城市 %s，拒绝回答以防幻觉", city)
            return (
                f"⚠️ 未能检索到 {city} 的可靠天气数据（搜索结果与城市不匹配），"
                "请稍后重试或查看官方天气应用。"
            )

        prompt = ChatPromptTemplate.from_messages([
            ("system", f"""你是{city}的天气助手。严格基于以下搜索结果回答，禁止编造。
必须包含：温度、天气状况、穿衣建议。如果信息不足，如实说明。"""),
            ("human", "用户问题：{query}\n\n搜索结果：{search_results}"),
        ])

        chain = prompt | self.llm
        return chain.invoke({"query": query, "search_results": search_results}).content

    def _search_weather(self, city: str) -> str:
        try:
            response = self.client.search(
                query=f"{city} 今天天气 温度 穿衣",
                search_depth="basic",
                max_results=3,
                include_answer=True,
            )
            results = []
            for r in response.get("results", []):
                title = r.get("title", "")
                content = r.get("content", "")
                if title and content:
                    results.append(f"[{title}] {content}")

            answer = response.get("answer", "")
            if answer:
                results.insert(0, f"[Tavily智能摘要] {answer}")

            return "\n\n".join(results)
        except Exception as e:
            logger.error("Tavily 搜索失败: %s", e)
            return ""

    @staticmethod
    def _validate_city_in_results(city: str, results: str) -> bool:
        return city in results


if __name__ == "__main__":
    from logging_config import setup_logging

    setup_logging()
    agent = WeatherAgent()
    print(agent.run("福州今天天气怎么样"))

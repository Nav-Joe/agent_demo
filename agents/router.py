from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

class IntentRouter:
    def __init__(self):
        self.llm = ChatOllama(model="qwen2.5:3b", temperature=0.1)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """你是意图识别专家。分析用户query，判断属于以下哪类：
- weather: 询问天气、温度、降雨、气候
- outing: 询问是否适合出门、运动、旅游建议、去哪玩
- suntime: 询问日出日落时间、昼夜长短、几点天黑
- proactive: 询问AI什么时候会主动说话、主动提醒
- chat: 闲聊、其他问题
只输出一个单词，不要解释。"""),
            ("human", "{query}")
        ])
    
    def route(self, query: str) -> str:
        chain = self.prompt | self.llm
        result = chain.invoke({"query": query})
        return result.content.strip().lower()

if __name__ == "__main__":
    router = IntentRouter()
    print(router.route("今天适合去爬山吗"))

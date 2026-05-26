import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
    if not TAVILY_API_KEY:
        raise ValueError("TAVILY_API_KEY 未设置，请检查 .env 文件")
    
    OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    PORT = int(os.getenv("PORT", "7860"))
    GRADIO_SERVER_NAME = os.getenv("GRADIO_SERVER_NAME", "0.0.0.0")

config = Config()
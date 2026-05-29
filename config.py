from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    tavily_api_key: str
    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:3b"
    port: int = 7860
    gradio_server_name: str = "0.0.0.0"
    proactive_silence_minutes: int = Field(default=3, ge=1, le=60)
    log_level: str = "INFO"


settings = Settings()

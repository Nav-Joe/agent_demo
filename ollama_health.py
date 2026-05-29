import logging

import requests

from config import settings

logger = logging.getLogger(__name__)


def check_ollama_connection() -> bool:
    """启动前检查 Ollama 是否可达，并确认目标模型已安装。"""
    tags_url = f"{settings.ollama_host.rstrip('/')}/api/tags"
    try:
        response = requests.get(tags_url, timeout=5)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(
            "无法连接 Ollama（%s）。本地运行请设置 OLLAMA_HOST=http://localhost:11434；"
            "Docker 内运行请设置 OLLAMA_HOST=http://host.docker.internal:11434。错误：%s",
            settings.ollama_host,
            e,
        )
        return False

    models = [m.get("name", "") for m in response.json().get("models", [])]
    model = settings.ollama_model
    if not any(m == model or m.startswith(f"{model}:") for m in models):
        logger.error(
            "Ollama 中未找到模型 %s，已安装：%s。请执行：ollama pull %s",
            model,
            models or "（无）",
            model,
        )
        return False

    logger.info("Ollama 连接正常：%s，模型 %s 可用", settings.ollama_host, model)
    return True

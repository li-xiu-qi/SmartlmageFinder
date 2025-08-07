"""
服务初始化模块
只负责初始化和获取 OpenAI 客户端。
"""

from openai import OpenAI
from .config import settings

_openai_client = None

def get_openai_client():
    global _openai_client
    if _openai_client is not None:
        return _openai_client
    config = settings.get_config()
    if not config or not config.OPENAI_API_KEY:
        print("警告: OPENAI_API_KEY 未配置，OpenAI 客户端初始化失败")
        return None
    client_kwargs = {"api_key": config.OPENAI_API_KEY}
    if config.OPENAI_API_BASE:
        client_kwargs["base_url"] = config.OPENAI_API_BASE
    _openai_client = OpenAI(**client_kwargs)
    print(f"OpenAI 客户端初始化成功，API Key: {config.OPENAI_API_KEY[:6]}***，API Base: {config.OPENAI_API_BASE or 'default'}")
    return _openai_client



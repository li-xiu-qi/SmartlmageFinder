import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # OpenAI配置
    openai_api_key: Optional[str] = None
    openai_api_base: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-3.5-turbo"
    
    # 后端服务配置 - 基于实际项目结构
    backend_base_url: str = "http://localhost:10050"
    static_images_url: str = "http://localhost:10050/static/images"
    
    # 服务配置
    host: str = "0.0.0.0"
    port: int = 10051
    
    # 搜索配置
    default_search_limit: int = 10
    max_search_limit: int = 20
    
    class Config:
        env_file = ".env"

settings = Settings()
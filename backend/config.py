from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
import os
import dotenv
import pathlib

# 加载环境变量
dotenv.load_dotenv()

def ensure_directories_exist(file_paths=None, dir_paths=None):
    """确保所有必要的目录存在，如果不存在则创建它们"""
    if file_paths:
        for file_path in file_paths:
            dir_name = os.path.dirname(file_path)
            if (dir_name and not os.path.exists(dir_name)):
                os.makedirs(dir_name, exist_ok=True)
                print(f"已创建目录: {dir_name}")
    
    if dir_paths:
        for dir_path in dir_paths:
            if dir_path and not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)
                print(f"已创建目录: {dir_path}")

class Settings(BaseSettings):
    # 模型路径设置
    MODEL_PATH: str = Field(
        default=r"C:\Users\k\Desktop\BaiduSyncdisk\baidu_sync_documents\hf_models\jina-clip-v2",
        description="用于向量编码的模型路径"
    )
     
    # 图片存储路径
    UPLOAD_DIR:str = "./data/images"
    
    # 向量设置
    VECTOR_DIM: int = 1024

    # 索引文件路径
    # FAISS索引文件路径
    TITLE_INDEX_PATH: str = "./data/faiss/title_vectors.faiss"
    DESCRIPTION_INDEX_PATH: str = "./data/faiss/description_vectors.faiss"
    IMAGE_INDEX_PATH: str = "./data/faiss/image_vectors.faiss"
    UUID_MAP_PATH: str = "./data/faiss/uuid_map.pickle"
    
    # 数据库地址
    DB_PATH: str = "./data/db/smartimagefinder.db"
    
    # 缓存设置
    TEXT_VECTOR_CACHE_DIR: str = Field(
        default="./data/caches/text_vector_cache",
        description="文本向量缓存目录"
    )
    IMAGE_VECTOR_CACHE_DIR: str = Field(
        default="./data/caches/image_vector_cache",
        description="图像向量缓存目录"
    )
    USE_CACHE: bool = Field(
        default=True,
        description="是否使用向量缓存"
    )
    
    # AI功能设置
    AI_ENABLED: bool = Field(
        default=True,
        description="是否启用AI功能（向量搜索、图像分析等）"
    )
    TRUST_REMOTE_CODE: bool = Field(
        default=True,
        description="是否信任远程代码（加载模型时使用）"
    )
    
    # OpenAI API设置
    OPENAI_API_KEY: str = os.environ.get("OPENAI_API_KEY", "")
    # 从环境变量加载API基础URL，如果不存在则使用默认值
    OPENAI_API_BASE: str = os.environ.get("OPENAI_BASE_URL","https://api.siliconflow.cn/v1")
    
    VISION_MODEL: str = Field(
        default="Qwen/Qwen2.5-VL-32B-Instruct",
        description="用于图像分析的视觉模型"
    )
    AVAILABLE_VISION_MODELS: list = Field(
        default= [ # 可用的视觉模型列表
        "Qwen/Qwen2.5-VL-32B-Instruct",
        "Pro/Qwen/Qwen2.5-VL-7B-Instruct"
    ],
        description="可用的视觉模型列表"
    )
    
    # 服务设置
    HOST: str = Field(
        default="0.0.0.0",
        description="服务主机地址"
    )
    PORT: int = Field(
        default=1000, 
        description="服务端口"
    )

# 创建全局设置实例
settings: Settings = Settings()

# 确保所有必要的目录结构存在
ensure_directories_exist(
    file_paths=[
        settings.DB_PATH,
        settings.TITLE_INDEX_PATH,
        settings.DESCRIPTION_INDEX_PATH, 
        settings.IMAGE_INDEX_PATH,
        settings.UUID_MAP_PATH
    ],
    dir_paths=[
        settings.TEXT_VECTOR_CACHE_DIR,
        settings.IMAGE_VECTOR_CACHE_DIR,
        settings.UPLOAD_DIR,
    ]
)

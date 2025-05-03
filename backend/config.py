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

class Settings:
    """应用配置类"""
    def __init__(self):
        # 模型路径设置
        self.MODEL_PATH = r"C:\Users\k\Desktop\BaiduSyncdisk\baidu_sync_documents\hf_models\jina-clip-v2"  # 用于向量编码的模型路径
        
        # 图片存储路径
        self.UPLOAD_DIR = "./data/images"
        
        # 向量设置
        self.VECTOR_DIM = 1024
        
        # 索引文件路径
        # FAISS索引文件路径
        self.TITLE_INDEX_PATH = "./data/faiss/title_vectors.faiss"
        self.DESCRIPTION_INDEX_PATH = "./data/faiss/description_vectors.faiss"
        self.IMAGE_INDEX_PATH = "./data/faiss/image_vectors.faiss"
        self.UUID_MAP_PATH = "./data/faiss/uuid_map.pickle"
        
        # 数据库地址
        self.DB_PATH = "./data/db/smartimagefinder.db"
        
        # 缓存设置
        self.TEXT_VECTOR_CACHE_DIR = "./data/caches/text_vector_cache"  # 文本向量缓存目录
        self.IMAGE_VECTOR_CACHE_DIR = "./data/caches/image_vector_cache"  # 图像向量缓存目录
        self.USE_CACHE = True  # 是否使用向量缓存
        
        # AI功能设置
        self.AI_ENABLED = True  # 是否启用AI功能（向量搜索、图像分析等）
        
        # OpenAI API设置
        self.OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
        # 从环境变量加载API基础URL，如果不存在则使用默认值
        self.OPENAI_API_BASE = os.environ.get("OPENAI_BASE_URL","https://api.siliconflow.cn/v1")
        
        self.VISION_MODEL = "Qwen/Qwen2.5-VL-32B-Instruct"  # 用于图像分析的视觉模型
        self.AVAILABLE_VISION_MODELS = [  # 可用的视觉模型列表
            "Qwen/Qwen2.5-VL-32B-Instruct",
            "Pro/Qwen/Qwen2.5-VL-7B-Instruct"
        ]
        
        # 服务设置
        self.HOST = "0.0.0.0"  # 服务主机地址
        self.PORT = 1000  # 服务端口

# 创建全局设置实例
settings = Settings()

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

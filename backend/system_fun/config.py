import os
from typing import Dict, Any, Tuple, Optional
from pydantic import BaseModel, Field, HttpUrl
from ..config import settings, ensure_directories_exist


class ApiConfig(BaseModel):
    """API配置模型"""

    apiKey: str = Field(..., description="OpenAI API密钥")
    baseUrl: str = Field(..., description="OpenAI API基础URL")


class StorageConfig(BaseModel):
    """存储配置模型"""

    rootDirectory: str = Field(..., description="上传根目录")
    cacheDirectory: str = Field(..., description="缓存目录")
    maxCacheSize: float = Field(..., description="最大缓存大小(GB)")


class ModelConfig(BaseModel):
    """模型配置"""

    vectorModel: str = Field(..., description="向量模型名称")
    visionModel: str = Field(..., description="视觉模型名称")


class VectorDbConfig(BaseModel):
    """向量数据库配置"""

    driverPath: str = Field(..., description="向量数据库驱动路径")


class FrontendConfig(BaseModel):
    """前端所需的系统配置模型"""

    api: ApiConfig
    storage: StorageConfig
    model: ModelConfig
    vectorDb: VectorDbConfig


class ConfigUpdateResult(BaseModel):
    """配置更新结果"""

    success: bool = Field(..., description="更新是否成功")
    message: str = Field(..., description="结果消息")


def get_frontend_config() -> FrontendConfig:
    """获取前端需要的系统配置信息"""
    config = settings.get_config()

    return FrontendConfig(
        api=ApiConfig(apiKey=config.OPENAI_API_KEY, baseUrl=config.OPENAI_API_BASE), 
        storage=StorageConfig(
            rootDirectory=config.UPLOAD_DIR, 
            cacheDirectory=config.TEXT_VECTOR_CACHE_DIR, 
            maxCacheSize=config.MAX_CACHE_SIZE_GB, 
        ),
        model=ModelConfig(
            vectorModel=os.path.basename(config.MODEL_PATH), 
            visionModel=config.VISION_MODEL, 
        ),
        vectorDb=VectorDbConfig(driverPath=config.VECTOR_DB_DRIVER), 
    )


def update_system_config(config_data: Dict[str, Any]) -> ConfigUpdateResult:
    """更新系统配置

    Args:
        config_data: 包含配置数据的字典

    Returns:
        ConfigUpdateResult: 更新结果
    """
    # 提取配置数据
    storage_config = config_data.get("storage", {})
    api_config = config_data.get("api", {})
    model_config = config_data.get("model", {})
    vector_db_config = config_data.get("vectorDb", {})

    # 准备要更新的配置字典
    config_updates = {}

    # 处理存储配置
    if "rootDirectory" in storage_config:
        config_updates["UPLOAD_DIR"] = storage_config["rootDirectory"]
    if "cacheDirectory" in storage_config:
        # 更新两个缓存目录的基础路径
        cache_base = os.path.dirname(storage_config["cacheDirectory"])
        config_updates["TEXT_VECTOR_CACHE_DIR"] = os.path.join(
            cache_base, "text_vector_cache"
        )
        config_updates["IMAGE_VECTOR_CACHE_DIR"] = os.path.join(
            cache_base, "image_vector_cache"
        )

    if "maxCacheSize" in storage_config:
        config_updates["MAX_CACHE_SIZE_GB"] = float(storage_config["maxCacheSize"])

    # 处理API配置
    if "apiKey" in api_config:
        config_updates["OPENAI_API_KEY"] = api_config["apiKey"]
    if "baseUrl" in api_config:
        config_updates["OPENAI_API_BASE"] = api_config["baseUrl"]

    # 处理模型配置
    if "visionModel" in model_config:
        config_updates["VISION_MODEL"] = model_config["visionModel"]
    if "vectorModel" in model_config and model_config["vectorModel"]:
        config_updates["MODEL_PATH"] = model_config["vectorModel"]

    # 处理向量数据库配置
    if "driverPath" in vector_db_config:
        config_updates["VECTOR_DB_DRIVER"] = vector_db_config["driverPath"]

    # 更新并保存配置
    success = settings.update_config(config_updates, auto_save=True)

    if success:
        # 确保必要的目录存在
        updated_config = settings.get_config()
        ensure_directories_exist(
            file_paths=[updated_config.DB_PATH],
            dir_paths=[
                updated_config.TEXT_VECTOR_CACHE_DIR,
                updated_config.IMAGE_VECTOR_CACHE_DIR,
                updated_config.UPLOAD_DIR,
                os.path.dirname(updated_config.VECTOR_DB_DRIVER),
            ],
        )
        return ConfigUpdateResult(success=True, message="配置已更新并保存到文件")
    else:
        return ConfigUpdateResult(
            success=False, message="配置更新失败，无法写入配置文件"
        )

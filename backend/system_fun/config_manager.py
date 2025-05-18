"""
配置管理模块 - 负责系统配置的获取和更新
"""

import os
from typing import Dict, Any

from ..config import settings, ensure_directories_exist


def get_frontend_config() -> Dict[str, Any]:
    """获取前端需要的系统配置信息
    
    Returns:
        Dict[str, Any]: 前端配置信息字典
    """
    config = settings.get_config()

    return {
        "api": {
            "apiKey": config.OPENAI_API_KEY,
            "baseUrl": config.OPENAI_API_BASE,
        },
        "storage": {
            "rootDirectory": config.UPLOAD_DIR,
            "cacheDirectory": config.TEXT_VECTOR_CACHE_DIR,
            "maxCacheSize": config.MAX_CACHE_SIZE_GB,
        },
        "model": {
            "vectorModel": os.path.basename(config.MODEL_PATH) if config.MODEL_PATH else "",
            "visionModel": config.VISION_MODEL,
        },
        "vectorDb": {
            "driverPath": config.VECTOR_DB_DRIVER
        },
    }


def update_system_config(config_data: Dict[str, Any]) -> Dict[str, Any]:
    """更新系统配置
    
    Args:
        config_data: 包含配置数据的字典
        
    Returns:
        Dict[str, Any]: 更新结果
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
                # 确保VECTOR_DB_DRIVER的父目录存在（如果是文件路径）
                os.path.dirname(updated_config.VECTOR_DB_DRIVER) if updated_config.VECTOR_DB_DRIVER else None,
            ],
        )
        return {"success": True, "message": "配置已更新并保存到文件"}
    else:
        return {
            "success": False,
            "message": "配置更新失败，无法写入配置文件",
        }


def check_vector_db_driver_status() -> Dict[str, Any]:
    """检查向量数据库驱动状态
    
    Returns:
        Dict[str, Any]: 驱动状态信息
    """
    config = settings.get_config()
    driver_path = config.VECTOR_DB_DRIVER

    if driver_path and os.path.exists(driver_path):
        return {
            "status": "available",
            "path": driver_path,
            "error": None
        }
    elif not driver_path:
        return {
            "status": "missing",
            "path": "Not configured",
            "error": "Vector DB driver path is not configured."
        }
    else:
        return {
            "status": "missing",
            "path": driver_path,
            "error": f"Driver not found at {driver_path}"
        }

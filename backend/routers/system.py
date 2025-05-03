from fastapi import APIRouter, Query, Path, Body
from typing import List, Dict, Any, Set, Optional
from ..schemas import ResponseModel
from .. import db
from ..config import settings
import os
import time
import sqlite3
import platform
import psutil
import sys

router = APIRouter(prefix="/system", tags=["system"])

# 获取实际的缓存统计信息
def get_cache_stats():
    """获取缓存统计信息"""
    text_cache_stats = {
        "entries": 0,
        "size_mb": 0
    }
    image_cache_stats = {
        "entries": 0,
        "size_mb": 0
    }
    
    # 尝试获取文本向量缓存统计
    if os.path.exists(settings.TEXT_VECTOR_CACHE_DIR):
        try:
            cache_db_path = os.path.join(settings.TEXT_VECTOR_CACHE_DIR, "cache.db")
            if os.path.exists(cache_db_path):
                conn = sqlite3.connect(cache_db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM cache")
                text_cache_stats["entries"] = cursor.fetchone()[0]
                # 计算大小
                text_cache_stats["size_mb"] = round(os.path.getsize(cache_db_path) / (1024 * 1024), 2)
                conn.close()
        except Exception:
            pass
    
    # 尝试获取图像向量缓存统计
    if os.path.exists(settings.IMAGE_VECTOR_CACHE_DIR):
        try:
            cache_db_path = os.path.join(settings.IMAGE_VECTOR_CACHE_DIR, "cache.db")
            if os.path.exists(cache_db_path):
                conn = sqlite3.connect(cache_db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM cache")
                image_cache_stats["entries"] = cursor.fetchone()[0]
                # 计算大小
                image_cache_stats["size_mb"] = round(os.path.getsize(cache_db_path) / (1024 * 1024), 2)
                conn.close()
        except Exception:
            pass
    
    return {
        "text_vector_cache": text_cache_stats,
        "image_vector_cache": image_cache_stats
    }

@router.get("/status", response_model=ResponseModel)
async def get_system_status():
    """获取系统当前状态，包括数据库连接状态和存储信息"""
    # 获取系统运行信息
    uptime = time.time() - psutil.boot_time()
    
    # 获取数据库信息
    try:
        conn = db.get_db_connection()
        cursor = conn.cursor()
        
        # 检查images表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='images'")
        has_images_table = cursor.fetchone() is not None
        
        if has_images_table:
            cursor.execute("SELECT COUNT(*) FROM images")
            image_count = cursor.fetchone()[0]
            cursor.execute("SELECT SUM(file_size) FROM images")
            total_size = cursor.fetchone()[0] or 0
        else:
            image_count = 0
            total_size = 0
        
        # 获取标签总数 - 使用与tags.py相同的方式
        tags = db.get_popular_tags()
        tag_count = len(tags)
            
        db_status = "connected"
        conn.close()
    except Exception as e:
        print(f"数据库连接错误: {e}")
        image_count = 0
        total_size = 0
        tag_count = 0
        db_status = "error"
    
    # 获取缓存统计
    cache_info = get_cache_stats()
    
    # 构建响应数据
    system_status = {
        "system": {
            "version": "1.0.0",
            "uptime": int(uptime),
            "status": "healthy",
            "platform": platform.system(),
            "python_version": sys.version.split()[0]
        },
        "components": {
            "database": {
                "status": db_status,
                "type": "sqlite",
                "path": settings.DB_PATH
            },
            "multimodal_api": {
                "status": "enabled" if settings.AI_ENABLED else "disabled",
                "model": settings.VISION_MODEL,
                "available_models": settings.AVAILABLE_VISION_MODELS,
                "api_base": settings.OPENAI_API_BASE
            }
        },
        "storage": {
            "total_images": image_count,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "total_tags": tag_count,
            "upload_dir": settings.UPLOAD_DIR,
            "index_paths": {
                "image": settings.IMAGE_INDEX_PATH,
                "title": settings.TITLE_INDEX_PATH,
                "description": settings.DESCRIPTION_INDEX_PATH,
                "uuid_map": settings.UUID_MAP_PATH
            }
        },
        "cache": {
            "enabled": settings.USE_CACHE,
            "text_vector_cache": {
                "path": settings.TEXT_VECTOR_CACHE_DIR,
                "entries": cache_info["text_vector_cache"]["entries"],
                "size_mb": cache_info["text_vector_cache"]["size_mb"]
            },
            "image_vector_cache": {
                "path": settings.IMAGE_VECTOR_CACHE_DIR,
                "entries": cache_info["image_vector_cache"]["entries"],
                "size_mb": cache_info["image_vector_cache"]["size_mb"]
            }
        },
        "server": {
            "host": settings.HOST,
            "port": settings.PORT
        }
    }
    
    return ResponseModel.success(data=system_status)

@router.post("/clear-cache", response_model=ResponseModel)
async def clear_cache(cache_types: Set[str]):
    """清除系统缓存"""
    # 获取当前缓存状态
    cache_info = get_cache_stats()
    
    # 验证缓存类型
    valid_cache_types = {"text_vector", "image_vector", "all"}
    invalid_types = cache_types - valid_cache_types
    
    if invalid_types:
        return ResponseModel.error(
            code="INVALID_REQUEST",
            message=f"无效的缓存类型: {', '.join(invalid_types)}"
        )
    
    # 使用"all"包含所有类型
    if "all" in cache_types:
        cache_types = {"text_vector", "image_vector"}
    
    # 处理结果
    result = {
        "message": "缓存已清除",
        "details": {}
    }
    
    if "text_vector" in cache_types:
        # 清理文本向量缓存
        cache_db_path = os.path.join(settings.TEXT_VECTOR_CACHE_DIR, "cache.db")
        if os.path.exists(cache_db_path):
            try:
                entries = cache_info["text_vector_cache"]["entries"]
                size_mb = cache_info["text_vector_cache"]["size_mb"]
                
                conn = sqlite3.connect(cache_db_path)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM cache")
                conn.commit()
                conn.close()
                
                result["details"]["text_vector_cache"] = {
                    "cleared": True,
                    "entries_removed": entries,
                    "size_freed_mb": size_mb
                }
            except Exception as e:
                result["details"]["text_vector_cache"] = {
                    "cleared": False,
                    "error": str(e)
                }
        else:
            result["details"]["text_vector_cache"] = {
                "cleared": False,
                "error": "缓存数据库不存在"
            }
    
    if "image_vector" in cache_types:
        # 清理图像向量缓存
        cache_db_path = os.path.join(settings.IMAGE_VECTOR_CACHE_DIR, "cache.db")
        if os.path.exists(cache_db_path):
            try:
                entries = cache_info["image_vector_cache"]["entries"]
                size_mb = cache_info["image_vector_cache"]["size_mb"]
                
                conn = sqlite3.connect(cache_db_path)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM cache")
                conn.commit()
                conn.close()
                
                result["details"]["image_vector_cache"] = {
                    "cleared": True,
                    "entries_removed": entries,
                    "size_freed_mb": size_mb
                }
            except Exception as e:
                result["details"]["image_vector_cache"] = {
                    "cleared": False,
                    "error": str(e)
                }
        else:
            result["details"]["image_vector_cache"] = {
                "cleared": False,
                "error": "缓存数据库不存在"
            }
    
    return ResponseModel.success(data=result)

@router.get("/config", response_model=ResponseModel)
async def get_system_config():
    """获取系统配置信息"""
    config = {
        "api": {
            "apiKey": settings.OPENAI_API_KEY,
            "baseUrl": settings.OPENAI_API_BASE,
            "timeout": 30000  # 默认超时时间
        },
        "storage": {
            "rootDirectory": settings.UPLOAD_DIR,
            "cacheDirectory": settings.TEXT_VECTOR_CACHE_DIR,
            "maxCacheSize": settings.MAX_CACHE_SIZE_GB / (2 ** 30)  # 转换为GB单位
        },
        "model": {
            "vectorModel": os.path.basename(settings.MODEL_PATH),
            "visionModel": settings.VISION_MODEL
        }
    }
    
    return ResponseModel.success(data=config)

@router.post("/update-config", response_model=ResponseModel)
async def update_system_config(config: Dict[str, Any] = Body(...)):
    """更新系统配置"""
    try:
        # 提取配置数据
        storage_config = config.get("storage", {})
        api_config = config.get("api", {})
        model_config = config.get("model", {})
        
        # 更新存储配置
        if "rootDirectory" in storage_config:
            settings.UPLOAD_DIR = storage_config["rootDirectory"]
        if "cacheDirectory" in storage_config:
            # 更新两个缓存目录的基础路径
            cache_base = os.path.dirname(storage_config["cacheDirectory"])
            settings.TEXT_VECTOR_CACHE_DIR = os.path.join(cache_base, "text_vector_cache")
            settings.IMAGE_VECTOR_CACHE_DIR = os.path.join(cache_base, "image_vector_cache")

        if "maxCacheSize" in storage_config:
            settings.MAX_CACHE_SIZE_GB = float(storage_config["maxCacheSize"])
        
        # 更新API配置
        if "apiKey" in api_config:
            settings.OPENAI_API_KEY = api_config["apiKey"]
        if "baseUrl" in api_config:
            settings.OPENAI_API_BASE = api_config["baseUrl"]
        
        # 更新模型配置
        if "visionModel" in model_config:
            settings.VISION_MODEL = model_config["visionModel"]
        
        # 保存配置到文件
        success = settings.save()
        
        if success:
            # 确保目录存在
            settings._ensure_directories()
            return ResponseModel.success(data={"message": "配置已更新并保存到文件"})
        else:
            return ResponseModel.error(
                code="CONFIG_SAVE_FAILED",
                message="配置更新失败，无法写入配置文件"
            )
    except Exception as e:
        return ResponseModel.error(
            code="UPDATE_CONFIG_ERROR",
            message=f"更新配置时出错: {str(e)}"
        )
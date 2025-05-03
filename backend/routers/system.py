from fastapi import APIRouter, Query, Path
from typing import List, Dict, Any, Set
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
    """获取系统当前状态，包括模型加载状态和数据库连接状态"""
    # 获取系统运行信息
    uptime = time.time() - psutil.boot_time()
    
    # 获取数据库信息
    try:
        conn = db.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM images")
        image_count = cursor.fetchone()[0]
        cursor.execute("SELECT SUM(file_size) FROM images")
        total_size = cursor.fetchone()[0] or 0
        db_status = "connected"
        conn.close()
    except Exception:
        image_count = 0
        total_size = 0
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
            "model": {
                "status": "loaded" if settings.AI_ENABLED else "disabled",
                "name": os.path.basename(settings.MODEL_PATH),
                "path": settings.MODEL_PATH,
                "vector_dimension": settings.VECTOR_DIM,
                "load_time": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(time.time() - 3600))  # 模拟1小时前加载
            },
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
        "ai_enabled": settings.AI_ENABLED,
        "model_path": settings.MODEL_PATH,
        "upload_dir": settings.UPLOAD_DIR,
        "vector_dimension": settings.VECTOR_DIM,
        "use_cache": settings.USE_CACHE,
        "vision_model": settings.VISION_MODEL,
        "available_vision_models": settings.AVAILABLE_VISION_MODELS,
        "host": settings.HOST,
        "port": settings.PORT
    }
    
    return ResponseModel.success(data=config)
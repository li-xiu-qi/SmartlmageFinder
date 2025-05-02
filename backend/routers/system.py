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

# 简单的缓存模拟
cache_stats = {
    "vector_cache": {
        "entries": 1250,
        "size_mb": 450
    },
    "image_analysis_cache": {
        "entries": 780,
        "size_mb": 15
    }
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
                "status": "simulated",  # 这里模拟模型状态
                "name": "jina-clip-v2",
                "load_time": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(time.time() - 3600))  # 模拟1小时前加载
            },
            "database": {
                "status": db_status,
                "type": "sqlite",
                "path": settings.DB_PATH
            },
            "multimodal_api": {
                "status": "simulated",  # 这里模拟API状态
                "model": "gpt-4-vision-preview"
            }
        },
        "storage": {
            "total_images": image_count,
            "total_size_mb": round(total_size / (1024 * 1024), 2)
        }
    }
    
    return ResponseModel.success(data=system_status)

@router.post("/clear-cache", response_model=ResponseModel)
async def clear_cache(cache_types: Set[str]):
    """清除系统缓存"""
    # 验证缓存类型
    valid_cache_types = {"vector", "image_analysis", "all"}
    invalid_types = cache_types - valid_cache_types
    
    if invalid_types:
        return ResponseModel.error(
            code="INVALID_REQUEST",
            message=f"无效的缓存类型: {', '.join(invalid_types)}"
        )
    
    # 使用"all"包含所有类型
    if "all" in cache_types:
        cache_types = {"vector", "image_analysis"}
    
    # 处理结果
    result = {
        "message": "缓存已清除",
        "details": {}
    }
    
    if "vector" in cache_types:
        # 模拟向量缓存清理
        result["details"]["vector_cache"] = {
            "cleared": True,
            "entries_removed": cache_stats["vector_cache"]["entries"],
            "size_freed_mb": cache_stats["vector_cache"]["size_mb"]
        }
    
    if "image_analysis" in cache_types:
        # 模拟图像分析缓存清理
        result["details"]["image_analysis_cache"] = {
            "cleared": True,
            "entries_removed": cache_stats["image_analysis_cache"]["entries"],
            "size_freed_mb": cache_stats["image_analysis_cache"]["size_mb"]
        }
    
    return ResponseModel.success(data=result)
from fastapi import APIRouter, Body, Depends
from typing import List, Dict, Any
import sqlite3
from ..global_schemas import ResponseModel
import os
from ..config import settings
from ..db_func.core import get_db

# 导入重构后的函数
from ..system_fun.status import get_system_status_data
from ..system_fun.config import get_frontend_config, update_system_config
from ..system_fun.clear_cache import clear_cache
from ..system_fun.cache_info import get_cache_stats, CacheClearResult

router = APIRouter(prefix="/system", tags=["system"])


@router.get("/status", response_model=ResponseModel)
async def get_system_status(db: sqlite3.Connection = Depends(get_db)):
    """获取系统当前状态，包括数据库连接状态和存储信息"""
    system_status = get_system_status_data(db)
    return ResponseModel.success(data=system_status)


@router.post("/clear-cache", response_model=ResponseModel)
async def api_clear_system_cache(db: sqlite3.Connection = Depends(get_db)):
    """清除系统缓存"""
    config = settings.get_config()

    # 获取缓存清除前的统计信息
    before_stats = get_cache_stats()
    
    # 清除文本和图像向量缓存
    text_vector_count = clear_cache(config.TEXT_VECTOR_CACHE_DIR)
    image_cache_count = clear_cache(config.IMAGE_VECTOR_CACHE_DIR)
    
    # 构建结果
    result = {
        "text_vector_cache": CacheClearResult(
            cleared=True,
            entries_removed=text_vector_count,
            size_freed_mb=before_stats.text_vector_cache.size_mb
        ).model_dump(),
        "image_vector_cache": CacheClearResult(
            cleared=True,
            entries_removed=image_cache_count,
            size_freed_mb=before_stats.image_vector_cache.size_mb
        ).model_dump()
    }
    
    return ResponseModel.success(data=result)


@router.get("/config", response_model=ResponseModel)
async def get_system_config(db: sqlite3.Connection = Depends(get_db)):
    """获取系统配置信息"""
    frontend_config = get_frontend_config()
    return ResponseModel.success(data=frontend_config)


@router.post("/update-config", response_model=ResponseModel)
async def api_update_system_config(config: Dict[str, Any] = Body(...), db: sqlite3.Connection = Depends(get_db)):
    """更新系统配置"""
    result = update_system_config(config)
    if result.success:
        return ResponseModel.success(data={"message": result.message})
    else:
        return ResponseModel.error(code="CONFIG_UPDATE_ERROR", message=result.message)


@router.get("/cache-stats", response_model=ResponseModel)
async def get_cache_statistics(db: sqlite3.Connection = Depends(get_db)):
    """获取缓存统计信息"""
    cache_stats = get_cache_stats()
    return ResponseModel.success(data=cache_stats.model_dump())

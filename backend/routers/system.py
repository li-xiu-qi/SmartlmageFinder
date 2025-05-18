"""
系统相关的API路由 - 包含所有系统状态、配置和管理的接口
"""

from fastapi import APIRouter, Body, Depends, Query
from typing import Dict, Any, Optional
import sqlite3

from ..global_schemas import ResponseModel
from ..db_func.core import get_db

# 导入重构后的功能模块
from ..system_fun.cache_manager import get_complete_cache_stats, clear_all_caches
from ..system_fun.config_manager import get_frontend_config, update_system_config
from ..system_fun.db_manager import get_database_info, get_storage_info
from ..system_fun.runtime_manager import get_runtime_info, get_system_info

# 创建主路由
router = APIRouter(prefix="/api/v1/system", tags=["system"])




@router.get("/info", response_model=ResponseModel)
async def get_basic_system_info():
    """获取基本系统信息，不包括数据库和缓存等详细信息"""
    system_info = get_system_info()
    return ResponseModel.success(data=system_info)




@router.get("/runtime", response_model=ResponseModel)
async def get_system_runtime_info():
    """获取系统运行时间信息"""
    runtime_info = get_runtime_info()
    return ResponseModel.success(data=runtime_info)


# ------------------ 数据库状态相关路由 ------------------
@router.get("/database", response_model=ResponseModel)
async def get_database_status(db: sqlite3.Connection = Depends(get_db)):
    """获取数据库状态信息"""
    db_info = get_database_info(db)
    return ResponseModel.success(data=db_info)


@router.get("/storage", response_model=ResponseModel)
async def get_storage_status(db: sqlite3.Connection = Depends(get_db)):
    """获取存储状态信息，包括图像和标签统计"""
    storage_info = get_storage_info(db)
    return ResponseModel.success(data=storage_info)


# ------------------ 缓存相关路由 ------------------
@router.get("/cache", response_model=ResponseModel)
async def get_cache_status():
    """获取缓存统计信息"""
    cache_stats = get_complete_cache_stats()
    return ResponseModel.success(data=cache_stats)


@router.post("/cache/clear", response_model=ResponseModel)
async def clear_system_cache(
    text_cache: bool = Query(True, description="是否清除文本缓存"),
    image_cache: bool = Query(True, description="是否清除图像缓存")
):
    """清除系统缓存
    
    Args:
        text_cache: 是否清除文本缓存，默认为True
        image_cache: 是否清除图像缓存，默认为True
    """
    text_cache_count, image_cache_count, total_freed_mb = clear_all_caches()
    
    result = {
        "cleared": True,
        "text_cache_entries_removed": text_cache_count if text_cache else 0,
        "image_cache_entries_removed": image_cache_count if image_cache else 0,
        "total_size_freed_mb": total_freed_mb
    }
    
    return ResponseModel.success(data=result)


# ------------------ 配置相关路由 ------------------
@router.get("/config", response_model=ResponseModel)
async def get_system_config():
    """获取系统配置信息"""
    frontend_config = get_frontend_config()
    return ResponseModel.success(data=frontend_config)


@router.post("/config/update", response_model=ResponseModel)
async def update_system_configuration(config_payload: Dict[str, Any] = Body(...)):
    """更新系统配置
    
    Args:
        config_payload: 包含要更新的配置字段的字典
    """
    result = update_system_config(config_payload)
    if result['success']:
        return ResponseModel.success(data={"message": result['message']})
    else:
        return ResponseModel.error(code="CONFIG_UPDATE_ERROR", message=result['message'])

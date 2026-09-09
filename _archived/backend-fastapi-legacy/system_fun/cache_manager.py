"""
缓存管理模块 - 负责系统缓存的查询和管理
"""

import os
import sqlite3
import diskcache
import time
from typing import Dict, Any, Tuple

from ..config import settings


def _dir_size_mb(path: str) -> float:
    """计算目录真实占用（所有文件累加），避免只统计 cache.db 导致的偏差"""
    total = 0
    for root, _, files in os.walk(path):
        for f in files:
            fp = os.path.join(root, f)
            try:
                total += os.path.getsize(fp)
            except OSError:
                pass
    return round(total / (1024 * 1024), 2)


def get_cache_stats() -> Dict[str, Any]:
    """获取缓存统计信息（改进版）

    改动:
      1. size_mb 由原先单纯统计 cache.db 文件大小改为统计整个缓存目录大小，更贴近真实占用。
      2. 新增 last_scan 时间戳，便于前端判断是否需要刷新（例如清除缓存后快速刷新）。
    Returns:
        Dict[str, Any]: 包含文本和图像向量缓存统计的字典
    """
    # 仅统计大小，不再统计条目数
    text_cache_stats: Dict[str, Any] = {"size_mb": 0.0, "db_file_size_mb": 0.0}
    image_cache_stats: Dict[str, Any] = {"size_mb": 0.0, "db_file_size_mb": 0.0}

    config = settings.get_config()

    # 获取文本向量缓存统计
    if os.path.exists(config.TEXT_VECTOR_CACHE_DIR):
        cache_db_path = os.path.join(config.TEXT_VECTOR_CACHE_DIR, "cache.db")
        if os.path.exists(cache_db_path):
            # 仅记录 DB 文件大小
            try:
                text_cache_stats["db_file_size_mb"] = round(os.path.getsize(cache_db_path) / (1024 * 1024), 2)
            except OSError:
                pass
        # 目录整体大小
        text_cache_stats["size_mb"] = _dir_size_mb(config.TEXT_VECTOR_CACHE_DIR)

    # 获取图像向量缓存统计
    if os.path.exists(config.IMAGE_VECTOR_CACHE_DIR):
        cache_db_path = os.path.join(config.IMAGE_VECTOR_CACHE_DIR, "cache.db")
        if os.path.exists(cache_db_path):
            try:
                image_cache_stats["db_file_size_mb"] = round(os.path.getsize(cache_db_path) / (1024 * 1024), 2)
            except OSError:
                pass
        image_cache_stats["size_mb"] = _dir_size_mb(config.IMAGE_VECTOR_CACHE_DIR)

    return {
        "text_vector_cache": text_cache_stats,
        "image_vector_cache": image_cache_stats,
        "last_scan": int(time.time())
    }


def clear_cache(cache_dir: str) -> int:
    """清除特定目录下的向量缓存

    Args:
        cache_dir: 缓存目录路径

    Returns:
        int: 清除的缓存条目数量
    """
    if not os.path.exists(cache_dir):
        print(f"Cache directory {cache_dir} does not exist. Nothing to clear.")
        return 0

    try:
        cache = diskcache.Cache(directory=cache_dir)
        # 确保目录正确初始化
        cache.create()
        clear_count = cache.clear()
        cache.close()
        print(f"清除缓存成功，清除条目数: {clear_count} from {cache_dir}")
        return clear_count
    except Exception as e:
        print(f"Error clearing cache at {cache_dir}: {e}")
        return 0


def clear_all_caches() -> Tuple[int, int, float]:
    """清除所有系统缓存
    
    Returns:
        Tuple[int, int, float]: 清除的文本缓存条目数，图像缓存条目数，释放的总空间（MB）
    """
    config = settings.get_config()
    
    # 获取缓存清除前的统计信息
    before_stats = get_cache_stats()
    
    # 清除文本和图像向量缓存
    text_cache_count = clear_cache(config.TEXT_VECTOR_CACHE_DIR)
    image_cache_count = clear_cache(config.IMAGE_VECTOR_CACHE_DIR)
    
    # 计算释放的空间
    total_freed_mb = round(
        before_stats['text_vector_cache']['size_mb'] + 
        before_stats['image_vector_cache']['size_mb'], 
        2
    )
    
    return text_cache_count, image_cache_count, total_freed_mb


def get_complete_cache_stats() -> Dict[str, Any]:
    """获取完整的缓存统计信息
    
    Returns:
        Dict[str, Any]: 包含所有缓存相关统计的字典
    """
    config = settings.get_config()
    cache_stats = get_cache_stats()
    
    # 计算总缓存条目和大小
    # 不再统计 total_entries
    total_size_mb = round(
        cache_stats['text_vector_cache']['size_mb'] + 
        cache_stats['image_vector_cache']['size_mb'],
        2
    )
    
    return {
        "max_size_gb": config.MAX_CACHE_SIZE_GB,
        "total_size_mb": total_size_mb,
        "text_vector_cache": {
            "path": config.TEXT_VECTOR_CACHE_DIR,
            "size_mb": cache_stats['text_vector_cache']['size_mb'],
            "db_file_size_mb": cache_stats['text_vector_cache']['db_file_size_mb']
        },
        "image_vector_cache": {
            "path": config.IMAGE_VECTOR_CACHE_DIR,
            "size_mb": cache_stats['image_vector_cache']['size_mb'],
            "db_file_size_mb": cache_stats['image_vector_cache']['db_file_size_mb']
        },
        # 透出扫描时间戳，前端可用于乐观刷新
        "last_scan": cache_stats.get("last_scan")
    }


def get_cache_brief_stats() -> Dict[str, Any]:
    """提供精简缓存统计（仅大小）"""
    full = get_complete_cache_stats()
    return {
        "total_size_mb": full["total_size_mb"],
        "last_scan": full.get("last_scan")
    }

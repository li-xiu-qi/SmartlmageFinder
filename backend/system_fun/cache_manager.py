"""
缓存管理模块 - 负责系统缓存的查询和管理
"""

import os
import sqlite3
import diskcache
from typing import Dict, Any, Tuple

from ..config import settings


def get_cache_stats() -> Dict[str, Any]:
    """获取缓存统计信息
    
    Returns:
        Dict[str, Any]: 包含文本和图像向量缓存统计的字典
    """
    text_cache_stats: Dict[str, Any] = {"entries": 0, "size_mb": 0.0}
    image_cache_stats: Dict[str, Any] = {"entries": 0, "size_mb": 0.0}

    config = settings.get_config()
    
    # 尝试获取文本向量缓存统计
    if os.path.exists(config.TEXT_VECTOR_CACHE_DIR):
        cache_db_path = os.path.join(config.TEXT_VECTOR_CACHE_DIR, "cache.db")
        if os.path.exists(cache_db_path):
            try:
                conn = sqlite3.connect(cache_db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM cache")
                result = cursor.fetchone()
                if result:
                    text_cache_stats["entries"] = result[0]
                text_cache_stats["size_mb"] = round(
                    os.path.getsize(cache_db_path) / (1024 * 1024), 2
                )
                conn.close()
            except sqlite3.Error as e:
                print(f"Error accessing text cache DB: {e}")

    # 尝试获取图像向量缓存统计
    if os.path.exists(config.IMAGE_VECTOR_CACHE_DIR):
        cache_db_path = os.path.join(config.IMAGE_VECTOR_CACHE_DIR, "cache.db")
        if os.path.exists(cache_db_path):
            try:
                conn = sqlite3.connect(cache_db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM cache")
                result = cursor.fetchone()
                if result:
                    image_cache_stats["entries"] = result[0]
                image_cache_stats["size_mb"] = round(
                    os.path.getsize(cache_db_path) / (1024 * 1024), 2
                )
                conn.close()
            except sqlite3.Error as e:
                print(f"Error accessing image cache DB: {e}")

    return {
        "text_vector_cache": text_cache_stats,
        "image_vector_cache": image_cache_stats,
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
    total_entries = (
        cache_stats['text_vector_cache']['entries'] + 
        cache_stats['image_vector_cache']['entries']
    )
    total_size_mb = round(
        cache_stats['text_vector_cache']['size_mb'] + 
        cache_stats['image_vector_cache']['size_mb'],
        2
    )
    
    return {
        "enabled": config.USE_CACHE,
        "max_size_gb": config.MAX_CACHE_SIZE_GB,
        "total_entries": total_entries,
        "total_size_mb": total_size_mb,
        "text_vector_cache": {
            "path": config.TEXT_VECTOR_CACHE_DIR,
            "entries": cache_stats['text_vector_cache']['entries'],
            "size_mb": cache_stats['text_vector_cache']['size_mb']
        },
        "image_vector_cache": {
            "path": config.IMAGE_VECTOR_CACHE_DIR,
            "entries": cache_stats['image_vector_cache']['entries'],
            "size_mb": cache_stats['image_vector_cache']['size_mb']
        }
    }

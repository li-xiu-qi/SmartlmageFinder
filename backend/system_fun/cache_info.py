import os
import sqlite3
from pydantic import BaseModel, Field
from typing import Dict, Optional
from ..config import settings
from ..utils.generate_vector import clear_cache as utils_clear_cache


class CacheStats(BaseModel):
    """缓存统计信息模型"""

    entries: int = Field(default=0, description="缓存条目数量")
    size_mb: float = Field(default=0.0, description="缓存大小(MB)")


class CacheClearResult(BaseModel):
    """缓存清除结果模型"""

    cleared: bool = Field(..., description="是否成功清除")
    entries_removed: Optional[int] = Field(default=None, description="移除的条目数")
    size_freed_mb: Optional[float] = Field(
        default=None, description="释放的空间大小(MB)"
    )
    error: Optional[str] = Field(default=None, description="错误信息(如果有)")


class SystemCacheStats(BaseModel):
    """系统所有缓存统计模型"""

    text_vector_cache: CacheStats = Field(default_factory=CacheStats)
    image_vector_cache: CacheStats = Field(default_factory=CacheStats)


def get_cache_stats() -> SystemCacheStats:
    """获取缓存统计信息"""
    text_cache_stats = CacheStats()
    image_cache_stats = CacheStats()

    config = settings.get_config()
    # 尝试获取文本向量缓存统计
    if os.path.exists(config.TEXT_VECTOR_CACHE_DIR):
        cache_db_path = os.path.join(config.TEXT_VECTOR_CACHE_DIR, "cache.db")
        if os.path.exists(cache_db_path):
            conn = sqlite3.connect(cache_db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM cache")
            text_cache_stats.entries = cursor.fetchone()[0]
            # 计算大小
            text_cache_stats.size_mb = round(
                os.path.getsize(cache_db_path) / (1024 * 1024), 2
            )
            conn.close()

    # 尝试获取图像向量缓存统计
    if os.path.exists(config.IMAGE_VECTOR_CACHE_DIR):
        cache_db_path = os.path.join(config.IMAGE_VECTOR_CACHE_DIR, "cache.db")
        if os.path.exists(cache_db_path):
            conn = sqlite3.connect(cache_db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM cache")
            image_cache_stats.entries = cursor.fetchone()[0]
            # 计算大小
            image_cache_stats.size_mb = round(
                os.path.getsize(cache_db_path) / (1024 * 1024), 2
            )
            conn.close()

    return SystemCacheStats(
        text_vector_cache=text_cache_stats, image_vector_cache=image_cache_stats
    )

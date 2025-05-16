import diskcache
import os

def clear_cache(cache_dir: str) -> int:
    """清除特定目录下的向量缓存

    Args:
        cache_dir: 缓存目录路径

    Returns:
        清除的缓存条目数量
    """
    if not os.path.exists(cache_dir):
        return 0

    cache = diskcache.Cache(directory=cache_dir)
    clear_count = cache.clear()
    print(f"清除缓存成功，清除条目数: {clear_count}")
    return clear_count

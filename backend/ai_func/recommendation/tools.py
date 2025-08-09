from typing import List, Dict, Any, Optional
from ...db_func.repositories.search import SearchRepository

# 注意：此文件位于 backend/ai_func/recommendation/tools.py 下
# 作为“工具层”，被 Agent 调用


def tool_search_images(query: str, targets: List[str], filters: Optional[Dict[str, Any]] = None, limit: int = 20) -> List[Dict[str, Any]]:
    repo = SearchRepository()
    return repo.unified_search(
        query_type="text",
        query_content=query,
        search_targets=targets or ["title", "description", "image"],
        filters=filters or {},
        limit=limit,
        offset=0,
    ) or []


def tool_recommend_images(images: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """示例推荐工具：当前简单直返；可按得分、标签匹配等二次排序。"""
    return images

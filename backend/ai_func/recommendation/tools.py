from typing import List, Dict, Any, Optional
from ...db_func.repositories.search import SearchRepository

# 注意：此文件位于 backend/ai_func/recommendation/tools.py 下
# 作为“工具层”，被 Agent 调用


def tool_search_images(query: str, targets: List[str], filters: Optional[Dict[str, Any]] = None, limit: int = 20) -> List[Dict[str, Any]]:
    """图片检索工具

    增加向量目标白名单过滤，防止将标签/风格等中文字段误当成向量表名导致
    sqlite 报错: no such table: XXX_vectors
    """
    repo = SearchRepository()
    allowed = {"title", "description", "image"}
    norm_targets = [t for t in (targets or []) if isinstance(t, str) and t in allowed]
    if not norm_targets:
        norm_targets = ["title", "description", "image"]
    return repo.unified_search(
        query_type="text",
        query_content=query,
        search_targets=norm_targets,
        filters=filters or {},
        limit=limit,
        offset=0,
    ) or []


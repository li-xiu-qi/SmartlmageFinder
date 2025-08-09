import json
from typing import List, Dict, Any, Optional, Iterable
import uuid
from ...db_func.repositories.search import SearchRepository
from .agent import RecommendAgent


class RecommendationService:
    def __init__(self):
        # 仅保留 Agent；数据库会话记录交由路由层处理
        self.agent = RecommendAgent()

    def rewrite_search_query(self, user_query: str) -> Dict[str, Any]:
        # 简化：当前直接透传查询作为“优化后查询”。后续可接入真实重写。
        optimized = (user_query or "").strip()
        return {
            "original_query": user_query,
            "optimized_query": optimized,
            "rewrite_success": False,
            "error": None if optimized else "empty"
        }


    def stream_core(self, messages: List[Dict[str, str]], state: Optional[Dict[str, Any]] = None,
                     vector_targets: Optional[List[str]] = None, limit: int = 20,
                     filters: Optional[Dict[str, Any]] = None) -> Iterable[str]:
        """纯流式核心：不做任何DB记录，也不封装SSE，只透传 agent.run_stream 产生的 JSON 行。"""
        vt = vector_targets or (state.get("vector_targets") if state else None) or ["title","description","image"]
        for line in self.agent.run_stream(messages, vector_targets=vt, filters=filters or (state.get("filters") if state else {}), limit=limit):
            yield line


# 全局实例
recommendation_service = RecommendationService()

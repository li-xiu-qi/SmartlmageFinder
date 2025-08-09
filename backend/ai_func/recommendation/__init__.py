"""Recommendation package exports.
Directly expose a lightweight recommendation_service built on RecommendAgent
to satisfy existing imports (chat + streaming).
"""
from .agent import RecommendAgent
from typing import List, Dict, Any, Optional, Iterable


class _RecommendationService:
	def __init__(self):
		self._agent = RecommendAgent()

	def stream_core(
		self,
		messages: List[Dict[str, str]],
		state: Optional[Dict[str, Any]] = None,
		vector_targets: Optional[List[str]] = None,
		limit: int = 20,
		filters: Optional[Dict[str, Any]] = None,
	) -> Iterable[str]:
		return self._agent.run_stream(
			messages=messages,
			vector_targets=vector_targets,
			filters=filters,
			limit=limit,
		)

	def chat_recommend(
		self,
		messages: List[Dict[str, str]],
		state: Optional[Dict[str, Any]] = None,
		vector_targets: Optional[List[str]] = None,
		limit: int = 20,
		filters: Optional[Dict[str, Any]] = None,
		request_id: Optional[str] = None,
		conversation_id: Optional[str] = None,
		user_id: Optional[str] = None,
	) -> Dict[str, Any]:
		# 简单消费一次 stream 拿到最终 selection
		import json
		images: List[Dict[str, Any]] = []
		ordered_ids: List[int] = []
		for raw in self.stream_core(messages, state, vector_targets, limit, filters):
			try:
				obj = json.loads(raw)
			except Exception:
				continue
			if obj.get("event") == "selection":
				images = obj.get("images") or []
				ordered_ids = obj.get("ids") or []
		return {
			"success": True,
			"images": images,
			"image_ids": ordered_ids,
			"limit": limit,
		}


recommendation_service = _RecommendationService()

__all__ = ["recommendation_service", "_RecommendationService", "RecommendAgent"]

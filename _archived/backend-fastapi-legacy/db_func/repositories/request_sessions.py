"""
请求/会话记录仓库：用于创建与更新请求会话记录，以便前后端通过 request_id 维护对话上下文
"""
from typing import Dict, Any, Optional, List
from .base import BaseRepository
from ..utils.common import row_to_dict, rows_to_dicts
import json
from datetime import datetime

ISO = "%Y-%m-%dT%H:%M:%S.%fZ"

class RequestSessionRepository(BaseRepository):
    def create(self, data: Dict[str, Any]) -> int:
        now = datetime.utcnow().strftime(ISO)
        q = (
            "INSERT INTO request_sessions (request_id, conversation_id, user_id, endpoint, messages, state, "
            "vector_targets, filters, selected_ids, status, error, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        )
        params = (
            data.get("request_id"),
            data.get("conversation_id"),
            data.get("user_id"),
            data.get("endpoint"),
            json.dumps(data.get("messages")) if data.get("messages") is not None else None,
            json.dumps(data.get("state")) if data.get("state") is not None else None,
            json.dumps(data.get("vector_targets")) if data.get("vector_targets") is not None else None,
            json.dumps(data.get("filters")) if data.get("filters") is not None else None,
            json.dumps(data.get("selected_ids")) if data.get("selected_ids") is not None else None,
            data.get("status", "pending"),
            data.get("error"),
            now,
            now,
        )
        return self.execute_insert(q, params)

    def update_by_request_id(self, request_id: str, updates: Dict[str, Any]) -> int:
        now = datetime.utcnow().strftime(ISO)
        fields = []
        params: List[Any] = []
        for k, v in updates.items():
            if k in ("messages", "state", "vector_targets", "filters", "selected_ids"):
                fields.append(f"{k} = ?")
                params.append(json.dumps(v) if v is not None else None)
            elif k in ("status", "error", "conversation_id", "user_id", "endpoint"):
                fields.append(f"{k} = ?")
                params.append(v)
            else:
                # 忽略未知字段，避免 SQL 注入
                continue
        fields.append("updated_at = ?")
        params.append(now)
        params.append(request_id)
        if not fields:
            return 0
        q = f"UPDATE request_sessions SET {', '.join(fields)} WHERE request_id = ?"
        return self.execute_update(q, tuple(params))

    def get_by_request_id(self, request_id: str) -> Optional[Dict[str, Any]]:
        q = "SELECT * FROM request_sessions WHERE request_id = ?"
        return self.execute_query_one(q, (request_id,))

    def list_by_conversation(self, conversation_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        q = "SELECT * FROM request_sessions WHERE conversation_id = ? ORDER BY created_at DESC LIMIT ?"
        return self.execute_query(q, (conversation_id, limit))

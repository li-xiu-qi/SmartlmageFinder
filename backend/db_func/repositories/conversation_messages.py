"""对话消息仓库：仅存储对话消息（user/assistant/system），及引用图片ID列表。"""
from typing import Dict, Any, List, Optional
from .base import BaseRepository
import json
from datetime import datetime

ISO = "%Y-%m-%dT%H:%M:%S.%fZ"

class ConversationMessageRepository(BaseRepository):
    def add_message(self, conversation_id: str, role: str, content: str = "", image_ids: Optional[List[int]] = None, metadata: Optional[Dict[str, Any]] = None) -> int:
        now = datetime.utcnow().strftime(ISO)
        q = (
            "INSERT INTO conversation_messages (conversation_id, role, content, image_ids, metadata, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?)"
        )
        params = (
            conversation_id,
            role,
            content,
            json.dumps(image_ids) if image_ids else None,
            json.dumps(metadata) if metadata else None,
            now,
        )
        return self.execute_insert(q, params)

    def list_messages(self, conversation_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        q = "SELECT * FROM conversation_messages WHERE conversation_id = ? ORDER BY created_at DESC LIMIT ?"
        rows = self.execute_query(q, (conversation_id, limit))
        # 反转为时间正序
        rows.reverse()
        # 解析 json 字段
        for r in rows:
            if r.get("image_ids"):
                try:
                    r["image_ids"] = json.loads(r["image_ids"])
                except Exception:
                    r["image_ids"] = []
            if r.get("metadata"):
                try:
                    r["metadata"] = json.loads(r["metadata"])
                except Exception:
                    r["metadata"] = None
        return rows

    def list_messages_openai(self, conversation_id: str, limit: int = 50) -> List[Dict[str, str]]:
        """以 OpenAI chat 格式返回最近 N 条消息 (正序)。

        仅包含 role 与 content 字段，过滤掉 content 为空的记录（但保留 system 空串）。
        limit: 返回的最大条数（会先按 created_at DESC 截取后再反转）。
        """
        rows = self.list_messages(conversation_id, limit=limit)
        result: List[Dict[str, str]] = []
        for r in rows:
            role = r.get("role") or "user"
            content = r.get("content") or ""
            # role 仅允许标准三类，其他可忽略或映射
            if role not in ("user", "assistant", "system"):
                continue
            # 通常如果是空内容的 assistant/user 可跳过，system 允许空（占位）
            if not content and role in ("user", "assistant"):
                continue
            result.append({"role": role, "content": content})
        return result

    # ---- 会话管理相关 ----
    def list_conversations(self, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """列出最近活跃的会话（按最后消息时间倒序）。"""
        q = (
            "SELECT conversation_id, MIN(created_at) AS first_at, MAX(created_at) AS last_at, "
            "COUNT(*) AS message_count "
            "FROM conversation_messages "
            "GROUP BY conversation_id "
            "ORDER BY last_at DESC "
            "LIMIT ? OFFSET ?"
        )
        rows = self.execute_query(q, (limit, offset))
        # 获取最后一条 assistant / user 摘要（可选）
        for r in rows:
            cid = r["conversation_id"]
            last_msg = self.execute_query(
                "SELECT role, content FROM conversation_messages WHERE conversation_id = ? ORDER BY created_at DESC LIMIT 1",
                (cid,)
            )
            if last_msg:
                r["last_role"] = last_msg[0]["role"]
                # 取前 80 字符用于列表摘要
                r["last_content_preview"] = (last_msg[0]["content"] or "")[:80]
        return rows

    def delete_conversation(self, conversation_id: str) -> int:
        """删除某个会话的所有消息，返回删除行数。"""
        q = "DELETE FROM conversation_messages WHERE conversation_id = ?"
        return self.execute_non_query(q, (conversation_id,))

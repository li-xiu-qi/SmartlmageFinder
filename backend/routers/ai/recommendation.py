from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

from ...ai_func.recommendation import recommendation_service 
from ...db_func.repositories.request_sessions import RequestSessionRepository
from ...db_func.repositories.conversation_messages import ConversationMessageRepository
from ...global_schemas import ResponseModel  

router = APIRouter()



class ChatRecommendRequest(BaseModel):
    messages: List[Dict[str, str]] = []  # 兼容旧格式，可忽略改为服务端聚合
    state: Optional[Dict[str, Any]] = None  # 未来可移除
    vector_targets: Optional[List[str]] = None
    limit: int = 20
    filters: Optional[Dict[str, Any]] = None
    request_id: Optional[str] = None
    conversation_id: Optional[str] = None
    user_id: Optional[str] = None
    query: Optional[str] = None  # 新增：只需传本次用户输入


@router.post("/recommend/chat")
async def ai_chat_recommend(req: ChatRecommendRequest):
    try:
        result = recommendation_service.chat_recommend(
            messages=req.messages,
            state=req.state,
            vector_targets=req.vector_targets,
            limit=req.limit,
            filters=req.filters,
            request_id=req.request_id,
            conversation_id=req.conversation_id,
            user_id=req.user_id,
        )
        if result.get("success"):
            return ResponseModel.success(
                data=result,
                message="AI对话式推荐成功"
            )
        else:
            return ResponseModel.error(
                code="AI_RECOMMENDATION_ERROR",
                message=result.get("error") or "对话式推荐失败",
                http_code=500
            )
    except Exception as e:
        return ResponseModel.error(
            code="AI_RECOMMENDATION_ERROR",
            message=f"对话式推荐暂时不可用: {str(e)}",
            http_code=500
        )


@router.post("/recommend/chat/stream")
async def ai_chat_recommend_stream(req: ChatRecommendRequest):
    import uuid, json as _json
    req_id = req.request_id or str(uuid.uuid4())
    conv_id = req.conversation_id or req_id
    msg_repo = ConversationMessageRepository()
    session_repo = RequestSessionRepository()

    # 拉取历史消息（只要最近若干条）
    history_records = []
    try:
        history_records = msg_repo.list_messages(conv_id, limit=40)
    except Exception:
        history_records = []

    # 组装成 agent messages
    history_messages = []
    for r in history_records:
        role = r.get("role")
        if role in ("user", "assistant", "system"):
            history_messages.append({"role": role, "content": r.get("content", "") or ""})

    # 当前用户输入（优先 query 字段，其次兼容 messages 最后一条 user）
    user_query = (req.query or "").strip()
    if not user_query and req.messages:
        last_user = next((m for m in reversed(req.messages) if m.get("role") == "user"), None)
        user_query = (last_user or {}).get("content", "").strip()
    if not user_query:
        return ResponseModel.error(code="NO_QUERY", message="缺少用户查询")

    # 写入当前 user 消息
    try:
        msg_repo.add_message(conv_id, "user", user_query, image_ids=None, metadata=None)
    except Exception:
        pass

    # 创建 request_sessions（可选审计）
    try:
        session_repo.create({
            "request_id": req_id,
            "conversation_id": conv_id,
            "user_id": req.user_id,
            "endpoint": "/api/v1/ai/recommend/chat/stream",
            "messages": history_messages + [{"role": "user", "content": user_query}],
            "state": None,
            "vector_targets": req.vector_targets,
            "filters": req.filters,
            "status": "pending",
        })
    except Exception:
        pass

    # 合并传入旧式 messages 与规范化 user_query
    final_messages = history_messages + [{"role": "user", "content": user_query}]

    def event_generator():
        yield 'event: rewrite_start\n' + 'data: ' + _json.dumps({"message": "start", "request_id": req_id, "conversation_id": conv_id}, ensure_ascii=False) + '\n\n'
        assistant_text_parts: List[str] = []
        try:
            core_iter = recommendation_service.stream_core(
                messages=final_messages,
                state=None,
                vector_targets=req.vector_targets,
                limit=req.limit,
                filters=req.filters,
            )
            for raw in core_iter:
                try:
                    obj = _json.loads(raw)
                except Exception:
                    continue
                ev = obj.get("event")
                if ev == "assistant_delta":
                    delta = obj.get("delta", "")
                    if delta:
                        assistant_text_parts.append(delta)
                    yield 'event: assistant_delta\n' + 'data: ' + _json.dumps({"delta": delta}, ensure_ascii=False) + '\n\n'
                elif ev == "selection":
                    images = obj.get("images") or []
                    ordered_ids = obj.get("ids") or [img.get("id") for img in images if isinstance(img, dict)]
                    # 构建精简列表
                    brief = []
                    for img in images:
                        brief.append({
                            "id": img.get("id"),
                            "score": img.get("score"),
                            "title": (img.get("title") or "")[:60],
                            "tags": img.get("tags") if isinstance(img.get("tags"), list) else [],
                            "public_url": img.get("public_url"),
                        })
                    assistant_full_text = ''.join(assistant_text_parts).strip()
                    # 写入 assistant 消息
                    try:
                        msg_repo.add_message(conv_id, "assistant", assistant_full_text, image_ids=ordered_ids, metadata={"image_brief": brief})
                    except Exception:
                        pass
                    try:
                        session_repo.update_by_request_id(req_id, {"status": "done", "selected_ids": ordered_ids})
                    except Exception:
                        pass
                    yield 'event: complete\n' + _json.dumps({
                        "request_id": req_id,
                        "conversation_id": conv_id,
                        "image_ids": ordered_ids,
                        "images_brief": brief,
                        "assistant_text": assistant_full_text,
                        "total_found": len(images),
                    }, ensure_ascii=False) + '\n\n'
        except Exception as e:
            err_msg = str(e)
            try:
                session_repo.update_by_request_id(req_id, {"status": "error", "error": err_msg})
            except Exception:
                pass
            yield 'event: error\n' + 'data: ' + _json.dumps({"message": err_msg, "request_id": req_id}, ensure_ascii=False) + '\n\n'

    return StreamingResponse(event_generator(), media_type="text/event-stream")


class ConversationHistoryResponse(BaseModel):
    conversation_id: str
    messages: List[Dict[str, Any]]  # 原始存储行（已解析 image_ids/metadata）
    openai_messages: List[Dict[str, str]]  # 仅 role+content
    total: int


@router.get("/conversations/{conversation_id}/messages")
async def get_conversation_history(conversation_id: str, limit: int = 100, openai_only: bool = False):
    """获取指定会话的最近消息。

    limit: 最大返回条数（按时间从旧到新）。
    openai_only=true 时只返回 openai_messages 字段。
    """
    repo = ConversationMessageRepository()
    try:
        rows = repo.list_messages(conversation_id, limit=limit)
        openai_msgs = repo.list_messages_openai(conversation_id, limit=limit)
        data: Dict[str, Any] = {
            "conversation_id": conversation_id,
            "messages": [] if openai_only else rows,
            "openai_messages": openai_msgs,
            "total": len(rows),
        }
        return ResponseModel.success(data=data, message="获取会话消息成功")
    except Exception as e:
        return ResponseModel.error(code="CONVERSATION_HISTORY_ERROR", message=str(e), http_code=500)


class CreateConversationRequest(BaseModel):
    system_prompt: Optional[str] = None  # 若需要自定义第一条 system 消息
    conversation_id: Optional[str] = None  # 指定则使用指定值（若不存在）


@router.post("/conversations/create")
async def create_conversation(req: CreateConversationRequest):
    import uuid
    repo = ConversationMessageRepository()
    conv_id = req.conversation_id or str(uuid.uuid4())
    # 如果有自定义 system prompt 且当前会话还没有任何消息，则插入一条 system
    try:
        existing = repo.list_messages(conv_id, limit=1)
        if not existing and req.system_prompt:
            repo.add_message(conv_id, "system", req.system_prompt, image_ids=None, metadata=None)
        return ResponseModel.success(data={"conversation_id": conv_id}, message="创建会话成功")
    except Exception as e:
        return ResponseModel.error(code="CREATE_CONVERSATION_ERROR", message=str(e), http_code=500)


@router.get("/conversations")
async def list_conversations(limit: int = 20, offset: int = 0):
    repo = ConversationMessageRepository()
    try:
        rows = repo.list_conversations(limit=limit, offset=offset)
        return ResponseModel.success(data={"items": rows, "limit": limit, "offset": offset}, message="获取会话列表成功")
    except Exception as e:
        return ResponseModel.error(code="LIST_CONVERSATIONS_ERROR", message=str(e), http_code=500)


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    repo = ConversationMessageRepository()
    try:
        deleted = repo.delete_conversation(conversation_id)
        return ResponseModel.success(data={"conversation_id": conversation_id, "deleted": deleted}, message="删除会话成功")
    except Exception as e:
        return ResponseModel.error(code="DELETE_CONVERSATION_ERROR", message=str(e), http_code=500)

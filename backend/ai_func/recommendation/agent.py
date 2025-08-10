import json
from typing import List, Dict, Any, Optional, Iterable

from backend.ai_func.recommendation.prompts import SYS_PROMPT
from ...config.init_service import get_openai_client
from ...config import settings
from .tools import tool_search_images
from ...utils.image_utils import build_public_url



MAX_CONTEXT_CHARS = 64_000  # 64K 字符窗口上限

def _window_messages(messages: List[Dict[str, Any]], system_msg: Dict[str, str], limit: int) -> List[Dict[str, Any]]:
    """按字符总长度裁剪历史，保留系统提示 + 最近消息。
    limit 为粗粒度字符上限，不精确到 token。"""
    if not messages:
        raise ValueError("消息列表不能为空")
    total = len(system_msg.get("content", ""))
    kept: List[Dict[str, Any]] = []
    for msg in reversed(messages):  # 从最新往前
        content = (msg.get("content") or "")
        if total + len(content) > limit:
            break
        kept.insert(0, msg)  # 仍保持时间顺序
        total += len(content)
    return [system_msg] + kept

class RecommendAgent:
    def __init__(self):
        pass

    def run_stream(
        self,
        messages: List[Dict[str, str]],
        vector_targets: Optional[List[str]] = None,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 20,
    ) -> Iterable[str]:
        client = get_openai_client()
        config = settings.get_config()
        model = config.CHAT_MODEL if config else "Qwen/Qwen3-8B"

        tools = [
            {
                "type": "function",
                "function": {
                    "name": "search_images",
                    "description": "当且仅当用户提出明确图片检索需求时调用；根据用户 query 与可选向量字段/过滤条件检索图片，返回候选。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "用户的检索语句，必须是明确的主题/对象/场景/用途描述"},
                            "vector_targets": {"type": "array", "items": {"type": "string"}, "description": "需要使用的向量字段名称列表"},
                            "filters": {"type": "object", "description": "结构化过滤条件 (标签/尺寸/时间等)"},
                            "limit": {"type": "integer", "description": "返回候选上限，建议 5~50"},
                        },
                        "required": ["query"],
                        "additionalProperties": False,
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "choose_images",
                    "description": "在已有候选结果基础上给出最终推荐顺序，只能在已执行过 search_images 并看到候选后调用。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "selected_ids": {"type": "array", "items": {"type": "integer"}, "description": "按优先级排序的候选图片 ID"},
                        },
                        "required": ["selected_ids"],
                        "additionalProperties": False,
                    },
                },
            },
        ]

        def start_stream(msgs):
            return client.chat.completions.create(
                model=model,
                messages=msgs,
                tools=tools,
                temperature=0.3,
                stream=True,
            )
        system_msg = {"role": "system", "content": SYS_PROMPT}
        history = _window_messages(messages, system_msg, MAX_CONTEXT_CHARS)
        stream = start_stream(history)

        tool_calls: List[Optional[Dict[str, Any]]] = []
        for chunk in stream:
            delta = None
            try:
                delta = chunk.choices[0].delta
            except Exception:
                delta = None
            if not delta:
                continue
            if getattr(delta, "content", None):
                yield json.dumps({"event": "assistant_delta", "delta": delta.content}, ensure_ascii=False) + "\n\n"
            if getattr(delta, "tool_calls", None):
                print("[DEBUG] tool_calls 原始输出:", delta.tool_calls)
                for tc in delta.tool_calls:
                    idx = getattr(tc, "index", 0) or 0
                    while len(tool_calls) <= idx:
                        tool_calls.append(None)
                    if tool_calls[idx] is None:
                        tool_calls[idx] = {
                            "id": getattr(tc, "id", None),
                            "type": "function",
                            "function": {"name": None, "arguments": ""},
                        }
                    if getattr(tc, "function", None):
                        fn = tc.function
                        if getattr(fn, "name", None):
                            tool_calls[idx]["function"]["name"] = fn.name
                        if getattr(fn, "arguments", None):
                            tool_calls[idx]["function"]["arguments"] += fn.arguments

        candidates_full: List[Dict[str, Any]] = []
        assistant_msg = {"role": "assistant", "content": "", "tool_calls": tool_calls or []}
        tool_msgs: List[Dict[str, Any]] = []

        for call in tool_calls or []:
            fn = (call or {}).get("function") or {}
            if fn.get("name") != "search_images":
                continue
            try:
                args = json.loads(fn.get("arguments") or "{}")
            except Exception:
                args = {}
            query = (args.get("query") or "").strip()
            vt = args.get("vector_targets") or vector_targets or ["title", "description", "image"]
            flt = args.get("filters") or (filters or {})
            lim = int(args.get("limit") or limit or 20)
            if not query:
                continue
            candidates_full = tool_search_images(query, vt, flt, lim) or []
            compact = []
            for c in candidates_full[: lim * 2]:
                public_url = c.get("public_url") or build_public_url(c.get("filepath") or "")
                compact.append({
                    "id": c.get("id"),
                    "score": round(float(c.get("score", 0)), 4) if isinstance(c.get("score", 0), (int, float)) else 0,
                    "title": (c.get("title") or "")[:60],
                    "desc": (c.get("description") or "")[:80],
                    "tags": (c.get("tags") or [])[:8],
                    "public_url": public_url,
                })
            tool_msgs.append({
                "role": "tool",
                "tool_call_id": call.get("id"),
                "content": json.dumps({"candidates": compact}, ensure_ascii=False),
            })

        follow_messages = _window_messages(messages, system_msg, MAX_CONTEXT_CHARS)
        if tool_calls and candidates_full:  # 将本轮工具调用放在截断后的历史之后
            follow_messages = follow_messages + [assistant_msg] + tool_msgs

        stream2 = None
        if candidates_full:
            stream2 = start_stream(follow_messages)

        choose_calls: List[Optional[Dict[str, Any]]] = []
        if stream2 is not None:
            for chunk in stream2:
                delta = None
                try:
                    delta = chunk.choices[0].delta
                except Exception:
                    delta = None
                if not delta:
                    continue
                if getattr(delta, "content", None):
                    yield json.dumps({"event": "assistant_delta", "delta": delta.content}, ensure_ascii=False) + "\n\n"
                if getattr(delta, "tool_calls", None):
                    for tc in delta.tool_calls:
                        idx = getattr(tc, "index", 0) or 0
                        while len(choose_calls) <= idx:
                            choose_calls.append(None)
                        if choose_calls[idx] is None:
                            choose_calls[idx] = {
                                "id": getattr(tc, "id", None),
                                "type": "function",
                                "function": {"name": None, "arguments": ""},
                            }
                        if getattr(tc, "function", None):
                            fn = tc.function
                            if getattr(fn, "name", None):
                                choose_calls[idx]["function"]["name"] = fn.name
                            if getattr(fn, "arguments", None):
                                choose_calls[idx]["function"]["arguments"] += fn.arguments

        ordered_ids: List[int] = []
        final_images: List[Dict[str, Any]] = []
        if candidates_full:
            for call in choose_calls or []:
                fn = (call or {}).get("function") or {}
                if fn.get("name") != "choose_images":
                    continue
                try:
                    args = json.loads(fn.get("arguments") or "{}")
                    sel_ids = args.get("selected_ids") or []
                    if isinstance(sel_ids, list):
                        ordered_ids.extend([int(i) for i in sel_ids if isinstance(i, (int, float))])
                except Exception:
                    continue
            seen = set()
            ordered_ids = [i for i in ordered_ids if (i not in seen and not seen.add(i))]
            if not ordered_ids:
                ordered_ids = [c.get("id") for c in sorted(candidates_full, key=lambda x: x.get("score", 0), reverse=True)][:limit]
            id_map = {img.get("id"): img for img in candidates_full if isinstance(img, dict)}
            final_images = [id_map[i] for i in ordered_ids if i in id_map]

        if final_images:
            for img in final_images:
                if img and 'public_url' not in img:
                    img['public_url'] = build_public_url(img.get('filepath') or '')

        yield json.dumps({"event": "selection", "ids": ordered_ids, "images": final_images}, ensure_ascii=False) + "\n\n"

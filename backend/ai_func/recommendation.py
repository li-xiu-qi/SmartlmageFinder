"""
AI智能推荐功能模块
基于现有搜索结果，使用AI模型进行智能筛选和推荐
"""
import json
from typing import List, Dict, Any, Optional, Union, Iterable
from ..config import settings
from ..config.init_service import get_openai_client
from ..db_func.repositories.search import SearchRepository


class RecommendationService:
    """AI推荐服务类"""
    
    def __init__(self):
        # 初始化推荐服务
        pass
    
    def _chat_completion(self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: int = 1000) -> Dict[str, Any]:
        """
        简单的聊天完成函数，使用统一的 OpenAI 客户端
        """
        try:
            client = get_openai_client()
            if not client:
                return {"success": False, "error": "OpenAI 客户端未配置"}
            
            config = settings.get_config()
            model = config.CHAT_MODEL 
            
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            content = response.choices[0].message.content
            return {
                "success": True,
                "content": content,
                "usage": response.usage.model_dump() if response.usage else {}
            }
            
        except Exception as e:
            return {"success": False, "error": f"AI 调用失败: {str(e)}"}
    
    def rewrite_search_query(self, user_query: str) -> Dict[str, Any]:
        """
        使用AI改写用户查询，生成更适合搜索的关键词
        
        Args:
            user_query: 用户原始查询
            
        Returns:
            改写结果字典，包含original_query、optimized_query、rewrite_success和error字段
        """
        result = {
            "original_query": user_query,
            "optimized_query": user_query,
            "rewrite_success": False,
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            if system_prompt:
                messages = ([{"role": "system", "content": system_prompt}] + messages)

        }
        
        try:
            # 检查AI服务是否可用
            client = get_openai_client()
            if not client:
                print("⚠️ AI服务不可用，使用原始查询")
                result["error"] = "AI服务不可用"
                return result
            
            print(f"🤖 开始AI查询改写 - 原始查询: '{user_query}'")
            
            try:
                # 构建查询改写的提示词
                rewrite_prompt = f"""
请将用户的自然语言查询改写为更适合图片搜索的关键词。

用户查询："{user_query}"

请按以下规则改写：
1. 提取关键的视觉元素和主题
2. 去除口语化表述和无关词汇
3. 使用简洁准确的关键词
4. 保持原意不变

重要：只返回改写后的关键词，不要包含箭头、原查询或任何格式符号。

示例：
输入："我想看一些美丽的山水风景照片"
输出：山水风景 自然景观

输入："给我找点可爱的小动物图片" 
输出：可爱动物 萌宠

输入："有没有现代建筑的照片"
输出：现代建筑 建筑设计

输入："{user_query}"
输出："""
                
                # 调用AI进行查询改写
                print(f"📤 发送AI改写请求...")
                response = self._chat_completion(
                    messages=[{"role": "user", "content": rewrite_prompt}],
                    temperature=0.3,  # 使用较低的温度保证结果稳定
                    max_tokens=100
                )
                
                print(f"📥 AI改写响应: {response}")
                
                if response and response.get("success"):
                    optimized_query = response.get("content", "").strip()
                    print(f"🎯 AI返回改写结果: '{optimized_query}'")
                    if optimized_query and optimized_query != user_query:
                        result["optimized_query"] = optimized_query
                        result["rewrite_success"] = True
                        print(f"✅ 查询改写成功: '{user_query}' → '{optimized_query}'")
                        return result
                    else:
                        print(f"⚠️ AI改写结果与原查询相同或为空")
                else:
                    print(f"❌ AI改写响应失败: {response}")
                
                # 如果AI返回结果为空或与原查询相同
                result["error"] = "AI改写结果为空或无效"
                return result
                
            except Exception as e:
                print(f"AI查询改写调用失败: {e}")
                result["error"] = f"AI调用失败: {str(e)}"
                return result
                
        except Exception as e:
            print(f"查询改写服务错误: {e}")
            result["error"] = f"查询改写服务错误: {str(e)}"
            return result
    
    def get_ai_recommendations(
        self,
        query: str,
        search_type: str = "vector",
        vector_targets: List[str] = None,
        tags: List[str] = None,
        image_id: Optional[int] = None,
        limit: int = 20,
        filters: Dict[str, Any] = None
                response = self._chat_completion(
                    messages=[{"role": "user", "content": rewrite_prompt}],
        """
                    max_tokens=100,
                    system_prompt=self._build_rewrite_system_prompt(),
        
        Args:
            query: 搜索查询词
            search_type: 搜索类型 (text/vector/image)
            vector_targets: 向量搜索目标 ["title", "description", "image"]
            tags: 标签过滤
            image_id: 图片ID（用于相似图片推荐）
            limit: 结果数量限制
            filters: 其他过滤条件
            
        Returns:
            包含推荐结果和AI分析的字典
        """
        try:
            # 1. 使用AI改写查询（如果是文本查询）
            query_rewrite_info = None
            effective_query = query
            
            if search_type in ["text", "vector"] and query.strip():
                query_rewrite_info = self.rewrite_search_query(query)
                print(f"🔄 查询改写结果: {query_rewrite_info}")
                if query_rewrite_info["rewrite_success"]:
                    effective_query = query_rewrite_info["optimized_query"]
                    print(f"✅ 查询已优化: '{query}' → '{effective_query}'")
                else:
                    print(f"⚠️ 查询改写失败，使用原始查询: {query_rewrite_info.get('error', '未知错误')}")
            
            print(f"🔍 开始搜索 - 查询: '{effective_query}', 类型: {search_type}, 目标: {vector_targets}")
            
            # 2. 获取搜索结果
            search_results = self._get_search_results(
                effective_query, search_type, vector_targets, tags, image_id, limit * 2, filters
            )
            
            print(f"🔍 搜索完成 - 找到 {len(search_results) if search_results else 0} 个结果")
            
            if not search_results:
                print("❌ 未找到相关图片")
                return {
                    "images": [],
                    "query_rewrite": query_rewrite_info,
                    "total_found": 0,
                    "search_time_ms": 0,
                    "success": True
                }
            
            # 3. 使用AI进行智能筛选和推荐（如果需要）
            final_results = search_results[:limit]  # 简化版本，直接返回搜索结果
            
            print(f"📋 返回推荐结果 - 共 {len(final_results)} 张图片")
            for idx, img in enumerate(final_results[:3]):  # 只打印前3个结果的摘要
                print(f"  {idx+1}. ID:{img.get('id')} 标题:'{img.get('title', 'N/A')}' 得分:{img.get('score', 'N/A')}")
            
            # 4. 构建返回结果
            return {
                "images": final_results,
                "query_rewrite": query_rewrite_info,
                "total_found": len(search_results),
                "search_time_ms": 0,  # 可以后续添加时间统计
                "success": True
            }
            
        except Exception as e:
            print(f"AI推荐服务错误: {e}")
            return {
                "images": [],
                "query_rewrite": query_rewrite_info,
                "total_found": 0,
                "search_time_ms": 0,
                "success": False,
                "error": str(e)
            }
    
    def _get_search_results(
        self,
        query: str,
        search_type: str,
        vector_targets: List[str],
        tags: List[str],
        image_id: Optional[int],
        limit: int,
        filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """获取搜索结果"""
        filters = filters or {}
        # 只有当tags不为None且不为空时才添加到过滤条件
        if tags:
            filters["tags"] = tags
        
        if search_type == "image" and image_id:
            # 基于图片ID的相似搜索
            search_repo = SearchRepository()
            vector_type = vector_targets[0] if vector_targets else "image"
            return search_repo.search_by_image_id(
                image_id=image_id,
                vector_type=vector_type,
                k=limit,
                filters=filters,
                exclude_self=True
            )
        elif search_type == "vector":
            # 向量搜索 - 使用text_search需要先生成向量
            search_repo = SearchRepository()
            from ..ai_func.generate_vector import encode_text
            query_vector = encode_text(query).tolist()
            # 简化版本：只使用第一个向量类型
            vector_type = vector_targets[0] if vector_targets else "title"
            vector_results = search_repo.vector_search(vector_type, query_vector, limit)
            if vector_results:
                image_ids = [result[0] for result in vector_results]
                return search_repo._get_images_by_ids(image_ids)
            return []
        else:
            # 文本搜索
            search_repo = SearchRepository()
            return search_repo.basic_search(
                text=query,
                search_type="both",
                filters=filters,
                limit=limit
            )

    # =============== 对话式推荐 ===============
    def _merge_state(self, prev: Optional[Dict[str, Any]], new_part: Dict[str, Any]) -> Dict[str, Any]:
        prev = prev or {}
        merged = {**prev}
        for k, v in new_part.items():
            if v is None:
                continue
            if isinstance(v, dict) and isinstance(merged.get(k), dict):
                # 深度合并 filters 等
                merged[k] = {**merged[k], **{ik: iv for ik, iv in v.items() if iv is not None}}
            else:
                merged[k] = v
        return merged

    def chat_recommend(
        self,
        messages: List[Dict[str, str]],
        state: Optional[Dict[str, Any]] = None,
        vector_targets: Optional[List[str]] = None,
        limit: int = 20,
        filters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        对话式推荐：依据最近一条用户消息（可选经 AI 改写）进行搜索，并返回更新后的 state。

        state 约定（轻量）：
        - query: 当前有效查询
        - vector_targets: 使用的向量目标
        - filters: { tags: [], start_date, end_date, ... }
        - history_hint: 最近摘要（可用于前端展示）
        """
        try:
            if not messages or not isinstance(messages, list):
                return {"success": False, "error": "messages 不能为空"}

            # 取最后一条用户消息作为本轮意图
            last_user_msg = next((m for m in reversed(messages) if m.get("role") == "user"), None)
            if not last_user_msg or not last_user_msg.get("content", "").strip():
                return {"success": False, "error": "请输入有效的用户消息"}

            curr_query = last_user_msg["content"].strip()
            vt = vector_targets or state.get("vector_targets") if state else None
            if not vt:
                vt = ["title", "description", "image"]

            # 合并 filters：优先入参 filters，再合并 state.filters
            merged_filters = {}
            if state and isinstance(state.get("filters"), dict):
                merged_filters.update({k: v for k, v in state.get("filters").items() if v is not None})
            if filters:
                merged_filters.update({k: v for k, v in filters.items() if v is not None})

            # 可选：AI 改写
            effective_query = curr_query
            rewrite_info = self.rewrite_search_query(curr_query)
            if rewrite_info and rewrite_info.get("rewrite_success"):
                effective_query = rewrite_info.get("optimized_query", curr_query)

            # 执行搜索（向量搜索统一入口）
            search_repo = SearchRepository()
            results = search_repo.unified_search(
                query_type="text",
                query_content=effective_query,
                search_targets=vt,
                filters=merged_filters,
                limit=limit,
                offset=0,
            )

            # 组装新的 state
            new_state = self._merge_state(
                state,
                {
                    "query": effective_query,
                    "vector_targets": vt,
                    "filters": merged_filters,
                    "history_hint": f"Q: {curr_query} -> {effective_query}",
                },
            )

            return {
                "images": results or [],
                "query_rewrite": rewrite_info,
                "total_found": len(results) if isinstance(results, list) else 0,
                "search_time_ms": 0,
                "success": True,
                "state": new_state,
            }
        except Exception as e:
            return {
                "images": [],
                "query_rewrite": None,
                "total_found": 0,
                "search_time_ms": 0,
                "success": False,
                "error": str(e),
                "state": state or {},
            }

    # =============== 流式（SSE）对话式推荐 ===============
    def _sse_event(self, event: str, data: Any) -> str:
        try:
            payload = json.dumps(data, ensure_ascii=False)
        except Exception:
            payload = json.dumps({"message": str(data)}, ensure_ascii=False)
        return f"event: {event}\n" f"data: {payload}\n\n"

    def stream_chat_recommend(
        self,
        messages: List[Dict[str, str]],
        state: Optional[Dict[str, Any]] = None,
        vector_targets: Optional[List[str]] = None,
        limit: int = 20,
        filters: Optional[Dict[str, Any]] = None,
    ) -> Iterable[str]:
        """
        SSE 流式接口：
        - rewrite_start / rewrite_delta / rewrite_done：流式返回 AI 改写关键词
        - search_started：开始搜索（包含元信息）
        - result：逐条返回图片结果（或一次性返回）
        - complete：完成，包含最终 state 和统计
        - error：错误信息
        """
        try:
            if not messages or not isinstance(messages, list):
                yield self._sse_event("error", {"message": "messages 不能为空"})
                return

            # 最近一条用户输入
            last_user_msg = next((m for m in reversed(messages) if m.get("role") == "user"), None)
            if not last_user_msg or not last_user_msg.get("content", "").strip():
                yield self._sse_event("error", {"message": "请输入有效的用户消息"})
                return

            original_query = last_user_msg["content"].strip()
            vt = vector_targets or (state.get("vector_targets") if state else None) or ["title", "description", "image"]

            # 合并 filters
            merged_filters: Dict[str, Any] = {}
            if state and isinstance(state.get("filters"), dict):
                merged_filters.update({k: v for k, v in state.get("filters").items() if v is not None})
            if filters:
                merged_filters.update({k: v for k, v in filters.items() if v is not None})

            # 1) 流式改写
            client = get_openai_client()
            optimized_query = ""
            if client:
                try:
                    yield self._sse_event("rewrite_start", {"original": original_query})
                    config = settings.get_config()
                    model = config.CHAT_MODEL if config else "Qwen/Qwen3-8B"
                    system_prompt = self._build_rewrite_system_prompt()

                    # 组合对话：系统提示 + 原始上下文 + 收尾指令
                    chat_messages = [{"role": "system", "content": system_prompt}]
                    for m in messages[-20:]:  # 限最近 20 条
                        role = m.get("role") or "user"
                        content = (m.get("content") or "").strip()
                        if content:
                            chat_messages.append({"role": role, "content": content})
                    chat_messages.append({"role": "user", "content": "请只输出关键词。"})

                    stream = client.chat.completions.create(
                        model=model,
                        messages=chat_messages,
                        temperature=0.3,
                        max_tokens=100,
                        stream=True,
                    )

                    for chunk in stream:
                        try:
                            delta = chunk.choices[0].delta.content if chunk and chunk.choices else None
                        except Exception:
                            delta = None
                        if delta:
                            optimized_query += delta
                            yield self._sse_event("rewrite_delta", {"delta": delta})
                    optimized_query = (optimized_query or "").strip()
                    yield self._sse_event("rewrite_done", {"optimized": optimized_query or original_query})
                    if not optimized_query:
                        optimized_query = original_query
                except Exception as e:
                    # 改写失败，降级
                    yield self._sse_event("rewrite_skipped", {"reason": f"AI 改写失败: {str(e)}"})
                    optimized_query = original_query
            else:
                # 无 AI，直接使用原始查询
                yield self._sse_event("rewrite_skipped", {"reason": "AI 未配置，使用原始查询"})
                optimized_query = original_query

            # 2) 搜索阶段
            yield self._sse_event("search_started", {"query": optimized_query, "vector_targets": vt, "filters": merged_filters, "limit": limit})

            search_repo = SearchRepository()
            results = search_repo.unified_search(
                query_type="text",
                query_content=optimized_query,
                search_targets=vt,
                filters=merged_filters,
                limit=limit,
                offset=0,
            ) or []

            # 逐条推送结果（如需要也可一次性发送）
            for idx, img in enumerate(results):
                # 可裁剪字段以降低体积
                yield self._sse_event("result", {"index": idx, "image": img})

            # 3) 完成并返回新的 state
            new_state = self._merge_state(
                state,
                {
                    "query": optimized_query,
                    "vector_targets": vt,
                    "filters": merged_filters,
                    "history_hint": f"Q: {original_query} -> {optimized_query}",
                },
            )

            yield self._sse_event(
                "complete",
                {
                    "total_found": len(results),
                    "state": new_state,
                },
            )
        except Exception as e:
            yield self._sse_event("error", {"message": str(e)})

# 全局推荐服务实例
recommendation_service = RecommendationService()

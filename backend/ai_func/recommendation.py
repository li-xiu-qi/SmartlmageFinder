"""
AI智能推荐功能模块
基于现有搜索结果，使用AI模型进行智能筛选和推荐
"""
import sqlite3
import json
from typing import List, Dict, Any, Optional, Union
from ..config import settings
from ..db_func.search_func.text_search import search_by_text
from ..db_func.search_func.multi_vector_search import text_search
from ..db_func.search_func.search_by_image_id import search_by_image_id
from .ai_config import is_ai_available


class RecommendationService:
    """AI推荐服务类"""
    
    def __init__(self):
        # 初始化推荐服务
        pass
    
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
            "error": None
        }
        
        try:
            # 检查AI服务是否可用
            if not is_ai_available():
                print("⚠️ AI服务不可用，使用原始查询")
                result["error"] = "AI服务不可用"
                return result
            
            print(f"🤖 开始AI查询改写 - 原始查询: '{user_query}'")
            
            try:
                from .ai_client import ai_client
                
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
                response = ai_client.chat_completion(
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
                
            except ImportError:
                print("AI客户端模块导入失败")
                result["error"] = "AI客户端不可用"
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
        conn: sqlite3.Connection,
        query: str,
        search_type: str = "vector",
        vector_targets: List[str] = None,
        tags: List[str] = None,
        image_id: Optional[int] = None,
        limit: int = 20,
        filters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        获取AI智能推荐结果
        
        Args:
            conn: 数据库连接对象
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
                conn, effective_query, search_type, vector_targets, tags, image_id, limit * 2, filters
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
        conn: sqlite3.Connection,
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
            # 对于图片相似搜索，通常使用单一向量类型，取第一个目标类型
            vector_type = vector_targets[0] if vector_targets else "image"
            return search_by_image_id(
                conn=conn,
                image_id=image_id,
                vector_type=vector_type,
                k=limit,
                filters=filters,
                exclude_self=True
            )
        elif search_type == "vector":
            # 向量搜索
            return text_search(
                conn=conn,
                text_query=query,
                search_targets=vector_targets or ["title", "description", "image"],
                filters=filters,
                limit=limit
            )
        else:
            # 文本搜索
            return search_by_text(
                conn=conn,
                text=query,
                search_type="both",
                filters=filters,
                limit=limit
            )

# 全局推荐服务实例
recommendation_service = RecommendationService()

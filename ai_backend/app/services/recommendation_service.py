from typing import List, Dict, Any
from app.services.search_client import search_client
from app.services.ai_service import ai_service
from app.models.schemas import (
    AIRecommendationRequest, 
    AIRecommendationResponse, 
    AIRecommendation
)
import datetime

class RecommendationService:
    async def get_ai_recommendations(
        self, 
        request: AIRecommendationRequest
    ) -> AIRecommendationResponse:
        """获取AI智能推荐"""
        
        # 1. 执行搜索
        search_results = await search_client.search_images(
            query=request.query,
            search_type=request.search_type,
            vector_type=request.vector_type,
            limit=request.limit * 2,  # 获取更多结果供AI筛选
            tags=request.tags,
            image_id=request.image_id
        )
        
        if not search_results:
            return AIRecommendationResponse(
                query=request.query,
                recommendations=[],
                search_summary={
                    "total_found": 0,
                    "search_type": request.search_type,
                    "vector_type": request.vector_type
                },
                ai_analysis="未找到相关图片，请尝试其他关键词。",
                timestamp=datetime.datetime.now().isoformat()
            )
        
        # 2. 构建搜索上下文
        search_context = {
            "query": request.query,
            "search_type": request.search_type,
            "vector_type": request.vector_type,
            "total_found": len(search_results),
            "tags": request.tags or [],
            "image_id": request.image_id
        }
        
        # 3. 生成AI推荐
        if request.include_ai_reasoning:
            recommendations = await ai_service.generate_recommendations(
                query=request.query,
                search_results=search_results,
                search_context=search_context
            )
            
            # 按AI相关性排序并限制数量
            recommendations.sort(key=lambda x: x.relevance_score, reverse=True)
            recommendations = recommendations[:request.limit]
            
            # 生成AI分析
            ai_analysis = await ai_service.generate_search_analysis(
                query=request.query,
                search_results=[r.image for r in recommendations]
            )
        else:
            # 不使用AI，直接返回原始结果
            recommendations = [
                AIRecommendation(
                    image=result,
                    ai_reason=f"相似度: {result.score:.2f}" if result.score else "默认推荐",
                    relevance_score=result.score or 0.5,
                    search_context=search_context
                )
                for result in search_results[:request.limit]
            ]
            ai_analysis = f"找到{len(search_results)}张相关图片"
        
        # 4. 构建响应
        return AIRecommendationResponse(
            query=request.query,
            recommendations=recommendations,
            search_summary={
                "total_found": len(search_results),
                "displayed": len(recommendations),
                "search_type": request.search_type,
                "vector_type": request.vector_type,
                "used_ai": request.include_ai_reasoning
            },
            ai_analysis=ai_analysis,
            timestamp=datetime.datetime.now().isoformat()
        )
    
    async def get_simple_recommendations(
        self, 
        query: str, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """获取简化版推荐，用于快速查询"""
        
        results = await search_client.search_images(
            query=query,
            limit=limit
        )
        
        return [
            {
                "id": result.id,
                "filename": result.filename,
                "filepath": result.filepath,
                "title": result.title,
                "description": result.description,
                "score": result.score,
                "tags": result.tags
            }
            for result in results
        ]

recommendation_service = RecommendationService()
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from app.models.schemas import (
    AIRecommendationRequest, 
    AIRecommendationResponse, 
    ChatRequest, 
    ChatResponse
)
from app.services.recommendation_service import recommendation_service
from app.services.ai_service import ai_service

router = APIRouter(prefix="/api/v1/ai", tags=["ai-recommendations"])

@router.post("/recommend", response_model=AIRecommendationResponse)
async def get_ai_recommendations(request: AIRecommendationRequest):
    """获取AI智能图片推荐"""
    try:
        return await recommendation_service.get_ai_recommendations(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat", response_model=ChatResponse)
async def chat_with_images(request: ChatRequest):
    """基于图片内容进行对话"""
    try:
        # 获取相关图片信息
        from app.services.search_client import search_client
        context_images = []
        
        for image_id in request.context_images[:5]:  # 限制最多5张
            # 这里可以获取具体图片信息，简化处理
            context_images.append({
                "id": image_id,
                "title": f"图片_{image_id}",
                "description": f"图片ID: {image_id}的相关内容"
            })
        
        reply = await ai_service.chat_with_images(
            message=request.message,
            context_images=context_images
        )
        
        return ChatResponse(
            reply=reply,
            recommended_images=[],
            conversation_id=request.conversation_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/quick-search")
async def quick_search(query: str, limit: int = 10):
    """快速搜索接口"""
    try:
        results = await recommendation_service.get_simple_recommendations(query, limit)
        return {
            "status": "success",
            "data": results,
            "count": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
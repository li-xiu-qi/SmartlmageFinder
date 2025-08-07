"""
AI推荐路由模块
提供智能图片推荐功能的API接口
"""
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional, Dict, Any

# 导入AI推荐服务
from ..ai_func.recommendation import recommendation_service
# 导入响应模型
from ..global_schemas import ResponseModel
# 导入基础组件
from .search.base import CommonFilterParams, get_query_filter_params, search_handler

router = APIRouter()

@router.get("/recommend")
@search_handler(error_code="AI_RECOMMENDATION_ERROR")
async def ai_recommend_images(
    user_query: str = Query(..., description="用户查询，描述您想要找的图片内容"),
    vector_targets: List[str] = Query(["title", "description", "image"], alias="vector_targets[]", description="向量搜索目标"),
    filter_params: CommonFilterParams = Depends(get_query_filter_params)
):
    """
    AI智能图片推荐API
    基于用户的文本描述，使用AI分析和改写用户查询，然后进行向量搜索返回最相关的图片推荐
    
    使用方式：
    - 用文字描述您想要找的图片内容，例如："我想看一些山水风景"、"给我找点城市夜景"、"有没有可爱的动物照片"等
    - 系统会使用AI理解并改写您的需求，然后返回最匹配的图片推荐
    """
    print(f"🚀 AI推荐请求开始")
    print(f"📝 用户查询: {user_query}")
    print(f"🎯 向量目标: {vector_targets}")
    print(f"🏷️ 标签过滤: {filter_params.tags}")
    print(f"📊 结果限制: {filter_params.limit}")
    
    # 参数验证
    if not user_query.strip():
        raise HTTPException(status_code=400, detail="请提供查询内容，描述您想要找的图片")
    
    try:
        # 构建过滤条件
        filters = filter_params.build_filters()
        print(f"🔧 过滤条件: {filters}")
        
        # 使用AI推荐服务（包含查询改写）
        result = recommendation_service.get_ai_recommendations(
            query=user_query,
            search_type="vector",
            vector_targets=vector_targets,
            tags=filter_params.tags,
            image_id=None,
            limit=filter_params.limit,
            filters=filters
        )
        
        print(f"✅ AI推荐完成 - 成功: {result.get('success', False)}")
        return result
        
    except Exception as e:
        print(f"AI推荐服务错误: {e}")
        raise HTTPException(status_code=500, detail=f"推荐服务暂时不可用: {str(e)}")

" 注意：这个接口似乎没有用上"
from fastapi import APIRouter, Query, Depends
from typing import List, Optional, Literal

# 导入数据库连接函数
from ...db_func.core.connection import get_db

# 导入搜索功能模块
from ...db_func.repositories.search import SearchRepository
from ...ai_func.generate_vector import encode_text

# 导入基础组件
from .base import CommonFilterParams, get_query_filter_params, search_handler

router = APIRouter()

@router.get("/by-vector")
@search_handler(error_code="VECTOR_SEARCH_ERROR")
async def vector_search_api(
    q: str = Query(..., description="搜索文本，将转换为向量"),
    vector_type: Literal["title", "description", "image"] = Query("image", description="要搜索的向量类型"),
    filter_params: CommonFilterParams = Depends(get_query_filter_params),
    conn = Depends(get_db)
):
    """
    直接使用向量搜索，将输入文本转换为向量，然后在指定向量表中搜索
    """
    # 构建过滤条件
    filters = filter_params.build_filters()
        
    # 将查询文本转换为向量
    query_embedding = encode_text(q).tolist()
    
    # 创建搜索 repository
    search_repo = SearchRepository()
    
    # 使用vector_search方法进行向量搜索
    vector_results = search_repo.vector_search(
        vector_type=vector_type,
        query_vector=query_embedding,
        top_k=filter_params.limit
    )
    
    # 如果有向量搜索结果，获取完整的图片信息
    if vector_results:
        from ...db_func.repositories.images import ImageRepository
        image_repo = ImageRepository()
        
        # 获取图片ID列表
        image_ids = [result[0] for result in vector_results]
        
        # 批量获取图片信息
        images = image_repo.get_by_ids(image_ids)
        
        # 添加距离信息
        distance_map = {result[0]: result[1] for result in vector_results}
        for image in images:
            image['distance'] = distance_map.get(image['id'], 0.0)
            image['score'] = 1 - image['distance']
        
        return images
    
    return []

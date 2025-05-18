" 注意：这个接口似乎没有用上"
from fastapi import APIRouter, Query, Depends
from typing import List, Optional, Literal

# 导入数据库连接函数
from ...db_func.core import get_db

# 导入搜索功能模块
from ...db_func.search_func.vector_search import find_similar_images
from ...utils.generate_vector import encode_text

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
    
    # 使用vector_search模块的find_similar_images函数
    results = find_similar_images(
        conn=conn,
        query_embedding=query_embedding,
        vector_type=vector_type,
        k=filter_params.limit,
        filters=filters
    )
    
    return results

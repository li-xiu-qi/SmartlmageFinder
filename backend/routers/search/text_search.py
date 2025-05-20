from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional, Literal
import sqlite3

# 导入数据库连接函数
from ...db_func.core import get_db

# 导入搜索功能模块
from ...db_func.search_func.text_search import search_by_text
from ...db_func.search_func.multi_vector_search import text_search

# 导入基础组件
from .base import CommonFilterParams, get_query_filter_params, search_handler

router = APIRouter()

@router.get("/text")
@search_handler(error_code="TEXT_SEARCH_ERROR")
async def text_search_api(
    q: str = Query(..., description="搜索文本"),
    search_type: Literal["title", "description", "both", "vector"] = Query("both", description="搜索类型：title-仅标题文本匹配，description-仅描述文本匹配，both-标题和描述文本匹配，vector-向量搜索"),
    vector_targets: List[str] = Query(["title", "description", "image"],alias="vector_targets[]", description="向量搜索目标，仅在search_type为vector时有效"),
    filter_params: CommonFilterParams = Depends(get_query_filter_params),
    conn = Depends(get_db)
):
    """
    文本搜索API，支持多种搜索类型:
    - 文本匹配搜索（title、description或both）
    - 向量搜索（vector）
    """
    print(f"搜索文本: {q}, 搜索类型: {search_type}, 向量搜索目标: {vector_targets}")
    # 构建过滤条件
    filters = filter_params.build_filters()
    
    if search_type in ["title", "description", "both"]:            
        # 使用文本匹配搜索
        results = search_by_text(
            conn=conn,
            text=q,
            search_type=search_type,
            filters=filters,
            limit=filter_params.limit,
            offset=filter_params.offset
        )
        
        return results
        
    elif search_type == "vector":
        # 使用向量搜索
        results = text_search(
            conn=conn,
            text_query=q,
            search_targets=vector_targets,
            filters=filters,
            limit=filter_params.limit,
            offset=filter_params.offset
        )
        
        return results
    else:
        raise HTTPException(status_code=400, detail=f"不支持的搜索类型: {search_type}")

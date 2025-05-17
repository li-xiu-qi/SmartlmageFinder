from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional, Literal
import traceback
import sqlite3

# 导入数据库连接函数
from ...db_func.core import get_db
# 导入响应模型
from ...global_schemas import ResponseModel

# 导入搜索功能模块
from ...db_func.search_func.text_search import search_by_text
from ...db_func.search_func.multi_vector_search import text_search
# 导入共用工具函数
from .utils import build_filters, process_json_fields, create_paginated_response, handle_search_error

router = APIRouter()

@router.get("/text")
async def text_search_api(
    q: str = Query(..., description="搜索文本"),
    search_type: Literal["title", "description", "both", "vector"] = Query("both", description="搜索类型：title-仅标题文本匹配，description-仅描述文本匹配，both-标题和描述文本匹配，vector-向量搜索"),
    vector_targets: List[str] = Query(["title", "description", "image"], description="向量搜索目标，仅在search_type为vector时有效"),
    filename: Optional[str] = Query(None, description="按文件名过滤"),
    tags: Optional[List[str]] = Query(None, description="按标签过滤"),
    start_date: Optional[str] = Query(None, description="开始日期 (YYYY-MM-DD HH:MM:SS)"),
    end_date: Optional[str] = Query(None, description="结束日期 (YYYY-MM-DD HH:MM:SS)"),
    limit: int = Query(20, description="返回结果数量限制"),
    offset: int = Query(0, description="分页偏移"),
    conn = Depends(get_db)
):
    """
    文本搜索API，支持多种搜索类型:
    - 文本匹配搜索（title、description或both）
    - 向量搜索（vector）
    """
    # 构建过滤条件
    filters = build_filters(
        filename=filename,
        tags=tags,
        start_date=start_date,
        end_date=end_date
    )    
    try:
        if search_type in ["title", "description", "both"]:            
            # 使用文本匹配搜索
            results = search_by_text(
                conn=conn,
                text=q,
                search_type=search_type,
                filters=filters,
                limit=limit,
                offset=offset
            )
            
            # 获取总条目数（用于分页）
            # 如果结果少于limit，则总数就是offset+结果数
            # 否则，只能提供一个估计值
            total = offset + len(results)
            if len(results) >= limit:
                # 表示可能还有更多结果
                total += 1
            
            # 处理JSON字段
            results = process_json_fields(results)
            
            return create_paginated_response(
                results=results,
                limit=limit,
                offset=offset,
                total_items=total,
                message="文本搜索成功"
            )
        elif search_type == "vector":
            # 使用向量搜索
            results = text_search(
                conn=conn,
                text_query=q,
                search_targets=vector_targets,
                filters=filters,
                limit=limit,
                offset=offset
            )
            
            # 处理JSON字段
            results = process_json_fields(results)
            
            return create_paginated_response(
                results=results,
                limit=limit,
                offset=offset,
                total_items=len(results) + offset,
                message="向量搜索成功"
            )
        else:
            raise HTTPException(status_code=400, detail=f"不支持的搜索类型: {search_type}")
            
    except Exception as e:
        return handle_search_error(
            e=e, 
            limit=limit, 
            offset=offset, 
            error_code="SEARCH_ERROR"
        )

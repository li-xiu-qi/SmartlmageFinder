from fastapi import APIRouter, Query, Depends
from typing import List, Optional, Literal
import traceback

# 导入数据库连接函数
from ...db_func.core import get_db
# 导入响应模型
from ...global_schemas import ResponseModel

# 导入搜索功能模块
from ...db_func.search_func.vector_search import find_similar_images
from ...utils.generate_vector import encode_text
# 导入共用工具函数
from .utils import build_filters, process_json_fields, create_paginated_response, handle_search_error

router = APIRouter()

@router.get("/by-vector")
async def vector_search_api(
    q: str = Query(..., description="搜索文本，将转换为向量"),
    vector_type: Literal["title", "description", "image"] = Query("image", description="要搜索的向量类型"),
    filename: Optional[str] = Query(None, description="按文件名过滤"),
    tags: Optional[List[str]] = Query(None, description="按标签过滤"),
    start_date: Optional[str] = Query(None, description="开始日期 (YYYY-MM-DD HH:MM:SS)"),
    end_date: Optional[str] = Query(None, description="结束日期 (YYYY-MM-DD HH:MM:SS)"),
    limit: int = Query(20, description="返回结果数量限制"),
    offset: int = Query(0, description="分页偏移"),
    conn = Depends(get_db)
):
    """
    直接使用向量搜索，将输入文本转换为向量，然后在指定向量表中搜索
    """
    try:
        # 构建过滤条件
        filters = build_filters(
            filename=filename,
            tags=tags,
            start_date=start_date,
            end_date=end_date
        )
            
        # 将查询文本转换为向量
        query_embedding = encode_text(q).tolist()
        
        # 使用vector_search模块的find_similar_images函数
        results = find_similar_images(
            conn=conn,
            query_embedding=query_embedding,
            vector_type=vector_type,
            k=limit,
            filters=filters
        )
        
        # 处理JSON字段
        results = process_json_fields(results)
        
        return create_paginated_response(
            results=results,
            limit=limit,
            offset=offset,
            total_items=len(results) + offset,
            message=f"向量搜索成功"
        )
    except Exception as e:
        return handle_search_error(
            e=e, 
            limit=limit, 
            offset=offset, 
            error_code="VECTOR_SEARCH_ERROR"
        )

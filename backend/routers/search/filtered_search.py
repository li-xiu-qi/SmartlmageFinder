# filepath: c:\Users\k\Documents\project\programming_project\python_project\importance\SmartImageFinder\backend\routers\search\filtered_search.py
from fastapi import APIRouter, Query, Depends, HTTPException
from typing import List, Optional
import sqlite3

# 导入数据库连接函数
from ...db_func.core import get_db
# 导入响应模型
from ...global_schemas import ResponseModel

# 导入搜索功能模块
from ...db_func.search_func.basic_search import get_filtered_image_ids

# 导入基础组件
from .base import CommonFilterParams, get_query_filter_params, search_handler

router = APIRouter()

@router.get("/filtered")
@search_handler(error_code="FILTER_SEARCH_ERROR")
async def filtered_search(
    filter_params: CommonFilterParams = Depends(get_query_filter_params),
    conn = Depends(get_db)
):
    """
    根据各种过滤条件搜索图像
    """
    # 构建过滤条件
    filters = filter_params.build_filters()
        
    # 如果没有提供任何过滤条件，返回错误
    if not filters:
        return ResponseModel.error(
            code="NO_FILTERS",
            message="请提供至少一个过滤条件",
            http_code=400
        )
        
    # 获取符合条件的图像ID
    image_ids = get_filtered_image_ids(conn, filters)
    
    if not image_ids:
        return ResponseModel.paginated_response(
            data=[],
            page=1,
            page_size=filter_params.limit,
            total_items=0,
            message="未找到符合条件的图像"
        )
        
    # 应用分页
    paged_ids = image_ids[filter_params.offset:filter_params.offset+filter_params.limit]
    
    # 查询完整的图像信息
    # 保存原始的row_factory
    original_row_factory = conn.row_factory
    
    # 设置行工厂函数以返回字典格式结果
    def dict_factory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d
        
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    placeholders = ','.join(['?'] * len(paged_ids))
    cursor.execute(f"""
    SELECT * FROM images WHERE id IN ({placeholders})
    ORDER BY created_at DESC
    """, paged_ids)
    
    results = cursor.fetchall()
    
    # 恢复原始的row_factory
    conn.row_factory = original_row_factory
    
    return results

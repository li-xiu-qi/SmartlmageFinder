# filepath: c:\Users\k\Documents\project\programming_project\python_project\importance\SmartImageFinder\backend\routers\search\filtered_search.py
from fastapi import APIRouter, Query, Depends
from typing import List, Optional
import traceback
import json
import sqlite3

# 导入数据库连接函数
from ...db_func.core import get_db
# 导入响应模型
from ...global_schemas import ResponseModel

# 导入搜索功能模块
from ...db_func.search_func.basic_search import get_filtered_image_ids
# 导入共用工具函数
from .utils import build_filters, process_json_fields, create_paginated_response, handle_search_error

router = APIRouter()

@router.get("/filtered")
async def filtered_search(
    filename: Optional[str] = Query(None, description="按文件名过滤"),
    title: Optional[str] = Query(None, description="按标题过滤"),
    description: Optional[str] = Query(None, description="按描述过滤"),
    tags: Optional[List[str]] = Query(None, description="按标签过滤"),
    start_date: Optional[str] = Query(None, description="开始日期 (YYYY-MM-DD HH:MM:SS)"),
    end_date: Optional[str] = Query(None, description="结束日期 (YYYY-MM-DD HH:MM:SS)"),
    limit: int = Query(100, description="返回结果数量限制"),
    offset: int = Query(0, description="分页偏移"),
    conn = Depends(get_db)
):
    """
    根据各种过滤条件搜索图像
    """
    try:
        # 构建过滤条件
        filters = build_filters(
            filename=filename,
            title=title,
            description=description,
            tags=tags,
            start_date=start_date,
            end_date=end_date
        )
            
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
            return create_paginated_response(
                results=[],
                limit=limit,
                offset=offset,
                total_items=0,
                message="未找到符合条件的图像"
            )
            
        # 应用分页
        paged_ids = image_ids[offset:offset+limit]
        
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
        
        # 处理JSON字段
        results = process_json_fields(results)
        
        # 恢复原始的row_factory
        conn.row_factory = original_row_factory
        
        return create_paginated_response(
            results=results,
            limit=limit,
            offset=offset,
            total_items=len(image_ids),
            message="过滤搜索成功"
        )
        
    except Exception as e:
        return handle_search_error(
            e=e, 
            limit=limit, 
            offset=offset, 
            error_code="FILTER_SEARCH_ERROR"
        )

from fastapi import APIRouter, Path, Query, Depends, HTTPException
from typing import List, Optional
import sqlite3

# 导入数据库连接函数
from ...db_func.core import get_db
# 导入响应模型
from ...global_schemas import ResponseModel

# 导入搜索功能模块
from ...db_func.search_func.search_by_image_id import search_by_image_id

# 导入基础组件
from .base import CommonFilterParams, get_query_filter_params, search_handler

router = APIRouter()

@router.get("/similar/{image_id}")
@search_handler(error_code="SIMILAR_SEARCH_ERROR")
async def similar_image_search(
    image_id: int = Path(..., description="图像ID"),
    vector_type: str = Query("image", description="搜索目标向量类型，可选值：'image' (图像向量), 'title' (标题向量), 'description' (描述向量)"),
    filter_params: CommonFilterParams = Depends(get_query_filter_params),
    conn = Depends(get_db)
):
    """
    根据已有图像ID查找相似图像，使用指定的单一向量类型进行搜索。
    """
    # 构建过滤条件
    filters = filter_params.build_filters()
        
    # 首先获取指定ID的图像信息
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM images WHERE id = ?", (image_id,))
    image = cursor.fetchone()
    
    if not image:
        return ResponseModel.error(
            code="IMAGE_NOT_FOUND",
            message=f"未找到ID为{image_id}的图像",
            http_code=404
        )
    
    # 直接使用 search_by_image_id 进行搜索
    # 为了支持分页 (offset, limit)，我们需要从 search_by_image_id 获取 offset + limit 数量的结果
    # 然后在应用层进行切片。search_by_image_id 的 k 参数是获取 k 个最近邻。
    k_to_fetch = filter_params.offset + filter_params.limit
    
    fetched_results = search_by_image_id(
        conn=conn,
        image_id=image_id,
        vector_type=vector_type, # Use the new single vector_type parameter
        k=k_to_fetch, # Fetch enough items for pagination
        filters=filters,
        exclude_self=True
    )
    
    # search_by_image_id 返回的结果已经按 distance 排序 (相似度高在前，如果 distance 是距离的话)
    # 应用分页
    # 如果 fetched_results 的数量少于 offset，切片将返回空列表，这是正确的行为。
    paginated_results = fetched_results[filter_params.offset : filter_params.offset + filter_params.limit]
            
    return paginated_results

from fastapi import APIRouter, Path, Query, Depends, HTTPException
from typing import List, Optional, Literal
import sqlite3

# 导入数据库连接函数
from ...db_func.core import get_db
# 导入响应模型
from ...global_schemas import ResponseModel

# 导入搜索功能模块
from ...db_func.search_func.search_by_image_id import search_by_image_id
from ...db_func.search_func.multi_vector_search import image_id_search

# 导入基础组件
from .base import CommonFilterParams, get_query_filter_params, search_handler

router = APIRouter()

@router.get("/similar/{image_id}")
@search_handler(error_code="SIMILAR_SEARCH_ERROR")
async def similar_image_search(
    image_id: int = Path(..., description="图像ID"),
    search_targets: List[str] = Query(["image"], description="搜索目标类型，可选：image-图像向量，title-标题向量，description-描述向量"),
    search_type: Literal["vector", "multi"] = Query("vector", description="搜索类型：vector-直接向量搜索，multi-多维向量搜索"), 
    filter_params: CommonFilterParams = Depends(get_query_filter_params),
    conn = Depends(get_db)
):
    """
    根据已有图像ID查找相似图像，支持向量搜索和多维向量搜索
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
    
    # 对于向量搜索，使用search_by_image_id
    if search_type == "vector":
        # 对每个搜索目标执行向量搜索
        all_results = []
        for target in search_targets:
            # 使用单SQL查询完成向量获取和搜索
            target_results = search_by_image_id(
                conn=conn,
                image_id=image_id,
                vector_type=target,
                k=filter_params.limit,
                filters=filters,
                exclude_self=True
            )
            all_results.extend(target_results)
        
        # 按相似度排序并去重
        unique_results = {}
        for item in all_results:
            if item["id"] not in unique_results or item["distance"] < unique_results[item["id"]]["distance"]:
                unique_results[item["id"]] = item
        
        # 转换为列表并排序
        sorted_results = sorted(unique_results.values(), key=lambda x: x["distance"])
        
        # 应用分页
        results = sorted_results[filter_params.offset:filter_params.offset+filter_params.limit]
        
        return results
        
    elif search_type == "multi":
        # 使用多维向量搜索
        results = image_id_search(
            conn=conn,
            image_id=image_id,
            search_targets=search_targets,
            filters=filters,
            limit=filter_params.limit,
            offset=filter_params.offset,
            exclude_self=True
        )
        
        return results
    else:
        raise HTTPException(
            status_code=400, 
            detail=f"不支持的搜索类型: {search_type}"
        )

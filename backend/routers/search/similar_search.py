from fastapi import APIRouter, Path, Query, Depends
from typing import List, Optional, Literal
import traceback
import sqlite3

# 导入数据库连接函数
from ...db_func.core import get_db
# 导入响应模型
from ...global_schemas import ResponseModel

# 导入搜索功能模块
from ...db_func.search_func.search_by_image_id import search_by_image_id
from ...db_func.search_func.multi_vector_search import image_id_search
# 导入共用工具函数
from .utils import build_filters, process_json_fields, create_paginated_response, handle_search_error

router = APIRouter()

@router.get("/similar/{image_id}")
async def similar_image_search(
    image_id: int = Path(..., description="图像ID"),
    search_targets: List[str] = Query(["image"], description="搜索目标类型，可选：image-图像向量，title-标题向量，description-描述向量"),
    search_type: Literal["vector", "multi"] = Query("vector", description="搜索类型：vector-直接向量搜索，multi-多维向量搜索"), 
    filename: Optional[str] = Query(None, description="按文件名过滤"),
    tags: Optional[List[str]] = Query(None, description="按标签过滤"),
    start_date: Optional[str] = Query(None, description="开始日期 (YYYY-MM-DD HH:MM:SS)"),
    end_date: Optional[str] = Query(None, description="结束日期 (YYYY-MM-DD HH:MM:SS)"),
    limit: int = Query(20, description="返回结果数量限制"),
    offset: int = Query(0, description="分页偏移"),
    conn = Depends(get_db)
):
    """
    根据已有图像ID查找相似图像，支持向量搜索和多维向量搜索
    """
    try:
        # 构建过滤条件
        filters = build_filters(
            filename=filename,
            tags=tags,
            start_date=start_date,
            end_date=end_date
        )
            
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
        
        results = []        
        # 对于向量搜索，使用search_by_image_id
        if search_type == "vector":
            try:
                # 对每个搜索目标执行向量搜索
                all_results = []
                for target in search_targets:
                    # 使用单SQL查询完成向量获取和搜索
                    target_results = search_by_image_id(
                        conn=conn,
                        image_id=image_id,
                        vector_type=target,
                        k=limit,
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
                results = sorted_results[offset:offset+limit]
                
                # 处理JSON字段
                results = process_json_fields(results)
                
                return create_paginated_response(
                    results=results,
                    limit=limit,
                    offset=offset,
                    total_items=len(sorted_results),
                    message="相似图像搜索成功"
                )
            except Exception as e:
                print(f"向量搜索失败: {e}")
                traceback.print_exc()
                return handle_search_error(
                    e=e, 
                    limit=limit, 
                    offset=offset, 
                    error_code="VECTOR_SEARCH_ERROR"
                )
            
        elif search_type == "multi":
            # 使用多维向量搜索
            results = image_id_search(
                conn=conn,
                image_id=image_id,
                search_targets=search_targets,
                filters=filters,
                limit=limit,
                offset=offset,
                exclude_self=True
            )
            
            # 处理JSON字段
            results = process_json_fields(results)
            
            return create_paginated_response(
                results=results,
                limit=limit,
                offset=offset,
                message="多维向量搜索成功"
            )
        else:
            return ResponseModel.error(
                code="INVALID_SEARCH_TYPE",
                message=f"不支持的搜索类型: {search_type}",
                http_code=400
            )
            
    except Exception as e:
        return handle_search_error(
            e=e, 
            limit=limit, 
            offset=offset, 
            error_code="SIMILAR_SEARCH_ERROR"
        )

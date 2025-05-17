from fastapi import APIRouter, HTTPException, Query, Path, UploadFile, File, Form, Body, Depends
from typing import List, Optional, Dict, Any, Union, Literal
import tempfile
import shutil
import json
import sqlite3
import os
import traceback

from datetime import datetime
from PIL import Image as PILImage
from contextlib import contextmanager

# 导入数据库连接函数
from ...db_func.core import get_db
# 导入响应模型
from ...global_schemas import ResponseModel

# 导入搜索功能模块
from ...db_func.search_func.basic_search import get_filtered_image_ids
from ...db_func.search_func.text_search import search_by_text
from ...db_func.search_func.vector_search import find_similar_images
from ...db_func.search_func.multi_vector_search import text_search, image_search, image_id_search
from ...db_func.search_func.search_by_image_id import search_by_image_id

# 导入图像处理相关功能
from ...utils.generate_vector import encode_text, encode_image


router = APIRouter(prefix="/search", tags=["search"])


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
    filters = {}
    if filename:
        filters["filename"] = filename
    if tags:
        filters["tags"] = tags
    if start_date:
        filters["start_date"] = start_date  
    if end_date:
        filters["end_date"] = end_date
    
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
            
            return ResponseModel.paginated_response(
                data=results,
                page=offset // limit + 1,
                page_size=limit,
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
            
            # 向量搜索目前可能无法获取准确的总条目数，使用结果长度作为估计
            total = len(results) + offset
            
            return ResponseModel.paginated_response(
                data=results,
                page=offset // limit + 1,
                page_size=limit,
                total_items=total,
                message="向量搜索成功"
            )
        else:
            raise HTTPException(status_code=400, detail=f"不支持的搜索类型: {search_type}")
            
    except Exception as e:
        traceback.print_exc()
        return ResponseModel.paginated_error(
            error_code="SEARCH_ERROR",
            message=f"搜索失败: {str(e)}",
            http_code=500,
            page=offset // limit + 1,
            page_size=limit
        )


@router.post("/image")
async def image_search_api(
    file: UploadFile = File(..., description="上传的图像文件"),
    search_targets: List[str] = Form(["image"], description="搜索目标类型，可选：image-图像向量，title-标题向量，description-描述向量"),
    filename: Optional[str] = Form(None, description="按文件名过滤"),
    tags: Optional[List[str]] = Form(None, description="按标签过滤"),
    start_date: Optional[str] = Form(None, description="开始日期 (YYYY-MM-DD HH:MM:SS)"),
    end_date: Optional[str] = Form(None, description="结束日期 (YYYY-MM-DD HH:MM:SS)"),
    limit: int = Form(20, description="返回结果数量限制"),
    offset: int = Form(0, description="分页偏移"),
    conn = Depends(get_db)
):
    """
    使用图像搜索相似图片，通过向量搜索
    """
    try:
        # 构建过滤条件
        filters = {}
        if filename:
            filters["filename"] = filename
        if tags:
            filters["tags"] = tags
        if start_date:
            filters["start_date"] = start_date
        if end_date:
            filters["end_date"] = end_date
            
        # 创建临时文件保存上传的图片
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        temp_file_path = temp_file.name
        temp_file.close()
        print("临时文件路径:", temp_file_path)
        
        try:
            # 保存上传的图像文件
            with open(temp_file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
                
            # 使用PIL打开图像以确保它是有效的图像
            img = PILImage.open(temp_file_path)
            
            # 使用multi_vector_search模块中的image_search函数
            results = image_search(
                conn=conn,
                image_path=temp_file_path,
                search_targets=search_targets,
                filters=filters,
                limit=limit,
                offset=offset
            )
            
            # 向量搜索目前可能无法获取准确的总条目数，使用结果长度作为估计
            total = len(results) + offset
            
            return ResponseModel.paginated_response(
                data=results,
                page=offset // limit + 1,
                page_size=limit,
                total_items=total,
                message="图像搜索成功"
            )
        finally:
            # 清理临时文件
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except Exception as e:
        traceback.print_exc()
        return ResponseModel.paginated_error(
            error_code="IMAGE_SEARCH_ERROR",
            message=f"图像搜索失败: {str(e)}",
            http_code=500,
            page=offset // limit + 1,
            page_size=limit
        )


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
        filters = {}
        if filename:
            filters["filename"] = filename
        if tags:
            filters["tags"] = tags
        if start_date:
            filters["start_date"] = start_date
        if end_date:
            filters["end_date"] = end_date
            
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
        
        return ResponseModel.paginated_response(
            data=results,
            page=offset // limit + 1,
            page_size=limit,
            total_items=len(results) + offset,
            message=f"向量搜索成功"
        )
    except Exception as e:
        traceback.print_exc()
        return ResponseModel.paginated_error(
            error_code="VECTOR_SEARCH_ERROR",
            message=f"向量搜索失败: {str(e)}",
            http_code=500,
            page=offset // limit + 1,
            page_size=limit
        )


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
        filters = {}
        if filename:
            filters["filename"] = filename
        if tags:
            filters["tags"] = tags
        if start_date:
            filters["start_date"] = start_date
        if end_date:
            filters["end_date"] = end_date
            
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
            except Exception as e:
                print(f"向量搜索失败: {e}")
                traceback.print_exc()
                return ResponseModel.error(
                    code="VECTOR_SEARCH_ERROR",
                    message=f"向量搜索失败: {str(e)}",
                    http_code=500
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
        else:
            return ResponseModel.error(
                code="INVALID_SEARCH_TYPE",
                message=f"不支持的搜索类型: {search_type}",
                http_code=400
            )
        
        # 向量搜索目前可能无法获取准确的总条目数，使用结果长度作为估计
        total = len(results) + offset
        
        return ResponseModel.paginated_response(
            data=results,
            page=offset // limit + 1,
            page_size=limit,
            total_items=total,
            message="相似图像搜索成功"
        )
                
    except sqlite3.Error as e:
        traceback.print_exc()
        return ResponseModel.paginated_error(
            error_code="DATABASE_ERROR",
            message=f"数据库错误: {str(e)}",
            http_code=500,
            page=offset // limit + 1,
            page_size=limit
        )
    except Exception as e:
        traceback.print_exc()
        return ResponseModel.paginated_error(
            error_code="SIMILAR_SEARCH_ERROR",
            message=f"相似图像搜索失败: {str(e)}",
            http_code=500,
            page=offset // limit + 1,
            page_size=limit
        )


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
        filters = {}
        if filename:
            filters["filename"] = filename
        if title:
            filters["title"] = title
        if description:
            filters["description"] = description
        if tags:
            filters["tags"] = tags
        if start_date:
            filters["start_date"] = start_date
        if end_date:
            filters["end_date"] = end_date
            
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
                page_size=limit,
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
        for result in results:
            if result.get('tags') and isinstance(result['tags'], str):
                try:
                    result['tags'] = json.loads(result['tags'])
                except:
                    result['tags'] = []
                    
            if result.get('metadata') and isinstance(result['metadata'], str):
                try:
                    result['metadata'] = json.loads(result['metadata'])
                except:
                    result['metadata'] = {}
        
        # 恢复原始的row_factory
        conn.row_factory = original_row_factory
        
        return ResponseModel.paginated_response(
            data=results,
            page=offset // limit + 1,
            page_size=limit,
            total_items=len(image_ids),
            message="过滤搜索成功"
        )
        
    except Exception as e:
        traceback.print_exc()
        return ResponseModel.paginated_error(
            error_code="FILTER_SEARCH_ERROR",
            message=f"过滤搜索失败: {str(e)}",
            http_code=500,
            page=offset // limit + 1,
            page_size=limit
        )

from fastapi import APIRouter, HTTPException, Query, Depends, UploadFile, File, Form
from typing import List, Optional, Literal, Union
import sqlite3

# 导入数据库连接函数
from ...db_func.core.connection import get_db

# 导入搜索功能模块
from ...db_func.repositories.search import SearchRepository

# 导入基础组件
from .base import (
    CommonFilterParams, get_query_filter_params, get_form_filter_params, 
    search_handler, process_image_upload, cleanup_temp_file
)

router = APIRouter()

@router.get("/unified")
@search_handler(error_code="UNIFIED_SEARCH_ERROR")
async def unified_text_search_api(
    q: str = Query(..., description="搜索文本"),
    search_type: Literal["title", "description", "both", "vector"] = Query("vector", description="搜索类型：title-仅标题文本匹配，description-仅描述文本匹配，both-标题和描述文本匹配，vector-向量搜索"),
    vector_targets: List[str] = Query(["title", "description", "image"], alias="vector_targets[]", description="向量搜索目标，仅在search_type为vector时有效"),
    filter_params: CommonFilterParams = Depends(get_query_filter_params),
    conn = Depends(get_db)
):
    """
    统一文本搜索API，支持多种搜索类型:
    - 文本匹配搜索（title、description或both）
    - 向量搜索（vector）- 默认类型
    """
    print(f"统一搜索 - 搜索文本: {q}, 搜索类型: {search_type}, 向量搜索目标: {vector_targets}")
    
    # 构建过滤条件
    filters = filter_params.build_filters()
    
    # 创建搜索 repository
    search_repo = SearchRepository()
    
    if search_type in ["title", "description", "both"]:            
        # 使用文本匹配搜索
        results = search_repo.basic_search(
            text=q,
            search_type=search_type,
            filters=filters,
            limit=filter_params.limit,
            offset=filter_params.offset
        )
        
        return results
        
    elif search_type == "vector":
        # 使用向量搜索 - 统一的搜索方法
        results = search_repo.unified_search(
            query_type="text",
            query_content=q,
            search_targets=vector_targets,
            filters=filters,
            limit=filter_params.limit,
            offset=filter_params.offset
        )
        
        return results
    else:
        raise HTTPException(status_code=400, detail=f"不支持的搜索类型: {search_type}")


@router.post("/unified/image")
@search_handler(error_code="UNIFIED_IMAGE_SEARCH_ERROR")
async def unified_image_search_api(
    file: UploadFile = File(..., description="上传的图像文件"),
    search_targets: List[str] = Form(["image"], description="搜索目标类型，可选：image-图像向量，title-标题向量，description-描述向量"),
    filter_params: CommonFilterParams = Depends(get_form_filter_params),
    conn = Depends(get_db)
):
    """
    统一图像搜索API，通过向量搜索寻找相似图片
    """
    print(f"统一图像搜索 - 搜索目标: {search_targets}")
    
    # 构建过滤条件
    filters = filter_params.build_filters()
        
    # 处理上传图片
    temp_file_path = process_image_upload(file)
    
    # 创建搜索 repository
    search_repo = SearchRepository()
    
    try:
        # 使用统一的搜索方法
        results = search_repo.unified_search(
            query_type="image",
            query_content=temp_file_path,
            search_targets=search_targets,
            filters=filters,
            limit=filter_params.limit,
            offset=filter_params.offset
        )
        
        return results
    finally:
        # 清理临时文件
        cleanup_temp_file(temp_file_path)


@router.post("/unified/vector")
@search_handler(error_code="UNIFIED_VECTOR_SEARCH_ERROR")
async def unified_vector_search_api(
    query_embedding: List[float] = Form(..., description="查询向量"),
    search_targets: List[str] = Form(["title", "description", "image"], description="搜索目标类型，可选：image-图像向量，title-标题向量，description-描述向量"),
    filter_params: CommonFilterParams = Depends(get_form_filter_params),
    conn = Depends(get_db)
):
    """
    统一向量搜索API，直接使用提供的向量进行搜索
    """
    print(f"统一向量搜索 - 向量维度: {len(query_embedding)}, 搜索目标: {search_targets}")
    
    # 构建过滤条件
    filters = filter_params.build_filters()
    
    # 创建搜索 repository
    search_repo = SearchRepository()
    
    # 使用直接向量搜索方法
    results = search_repo.vector_search_direct(
        query_embedding=query_embedding,
        search_targets=search_targets,
        filters=filters,
        limit=filter_params.limit,
        offset=filter_params.offset
    )
    
    return results

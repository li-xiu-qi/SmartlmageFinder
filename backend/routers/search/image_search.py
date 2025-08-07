from fastapi import APIRouter, UploadFile, File, Form, Depends
from typing import List, Optional

# 导入数据库连接函数
from ...db_func.core.connection import get_db

# 导入搜索功能模块
from ...db_func.repositories.search import SearchRepository

# 导入基础组件
from .base import (
    CommonFilterParams, get_form_filter_params, search_handler, 
    process_image_upload, cleanup_temp_file
)

router = APIRouter()

@router.post("/image")
@search_handler(error_code="IMAGE_SEARCH_ERROR")
async def image_search_api(
    file: UploadFile = File(..., description="上传的图像文件"),
    search_targets: List[str] = Form(["image"], description="搜索目标类型，可选：image-图像向量，title-标题向量，description-描述向量"),
    filter_params: CommonFilterParams = Depends(get_form_filter_params),
    conn = Depends(get_db)
):
    """
    使用图像搜索相似图片，通过向量搜索
    """
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

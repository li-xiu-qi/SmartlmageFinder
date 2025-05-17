from fastapi import APIRouter, UploadFile, File, Form, Depends
from typing import List, Optional
import tempfile
import shutil
import os
import traceback
from PIL import Image as PILImage

# 导入数据库连接函数
from ...db_func.core import get_db
# 导入响应模型
from ...global_schemas import ResponseModel

# 导入搜索功能模块
from ...db_func.search_func.multi_vector_search import image_search
# 导入共用工具函数
from .utils import build_filters, process_json_fields, create_paginated_response, handle_search_error

router = APIRouter()

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
        filters = build_filters(
            filename=filename,
            tags=tags,
            start_date=start_date,
            end_date=end_date
        )
            
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
            PILImage.open(temp_file_path)
            
            # 使用multi_vector_search模块中的image_search函数
            results = image_search(
                conn=conn,
                image_path=temp_file_path,
                search_targets=search_targets,
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
                message="图像搜索成功"
            )
        finally:
            # 清理临时文件
            if os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                except PermissionError:
                    # 文件可能仍在使用中，稍后将被系统自动清理
                    print(f"无法删除临时文件 {temp_file_path}，文件可能仍在使用中")
                
    except Exception as e:
        return handle_search_error(
            e=e, 
            limit=limit, 
            offset=offset, 
            error_code="IMAGE_SEARCH_ERROR"
        )

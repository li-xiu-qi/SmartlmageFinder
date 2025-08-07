"""
搜索功能的基类和共用组件
提供统一的参数处理、过滤逻辑和响应格式化
"""
from fastapi import Query, Form, Path, Depends, HTTPException, UploadFile, File
from typing import List, Optional, Dict, Any, Callable, Type, TypeVar, Generic, Union, Literal
import sqlite3
import tempfile
import os
import shutil
import traceback
from functools import wraps
from PIL import Image as PILImage

# 导入数据库连接函数
from ...db_func.core.connection import get_db
# 导入响应模型
from ...global_schemas import ResponseModel
# 导入共用工具函数
from .utils import build_filters, process_json_fields, create_paginated_response, handle_search_error

# 定义常用的查询参数类型
class CommonFilterParams:
    """定义共用的过滤参数"""
    def __init__(
        self,
        filename: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ):
        print("CommonFilterParams目前接收到的tags:",tags)
        # 打印tags的数据类型
        print("tags的数据类型：",type(tags))
        
        self.filename = filename
        self.title = title
        self.description = description
        self.tags = tags
        self.start_date = start_date
        self.end_date = end_date
        self.limit = limit
        self.offset = offset
    
    def build_filters(self) -> Dict[str, Any]:
        """构建过滤条件字典"""
        return build_filters(
            filename=self.filename,
            title=self.title,
            description=self.description,
            tags=self.tags,
            start_date=self.start_date,
            end_date=self.end_date
        )

# 定义通用的查询参数依赖项
def get_query_filter_params(
    filename: Optional[str] = Query(None, description="按文件名过滤"),
    title: Optional[str] = Query(None, description="按标题过滤"),
    description: Optional[str] = Query(None, description="按描述过滤"),
    tags: Optional[List[str]] = Query(None, description="按标签过滤"),
    start_date: Optional[str] = Query(None, description="开始日期 (YYYY-MM-DD HH:MM:SS)"),
    end_date: Optional[str] = Query(None, description="结束日期 (YYYY-MM-DD HH:MM:SS)"),
    limit: int = Query(20, description="返回结果数量限制"),
    offset: int = Query(0, description="分页偏移"),
) -> CommonFilterParams:
    """获取通用的查询过滤参数，用于GET请求"""
    return CommonFilterParams(
        filename=filename,
        title=title,
        description=description,
        tags=tags,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset
    )

def get_form_filter_params(
    filename: Optional[str] = Form(None, description="按文件名过滤"),
    tags: Optional[List[str]] = Form(None, description="按标签过滤"),
    start_date: Optional[str] = Form(None, description="开始日期 (YYYY-MM-DD HH:MM:SS)"),
    end_date: Optional[str] = Form(None, description="结束日期 (YYYY-MM-DD HH:MM:SS)"),
    limit: int = Form(20, description="返回结果数量限制"),
    offset: int = Form(0, description="分页偏移"),
) -> CommonFilterParams:
    """获取通用的查询过滤参数，用于POST请求的表单"""
    return CommonFilterParams(
        filename=filename,
        tags=tags,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset
    )

def process_image_upload(file: UploadFile) -> str:
    """
    处理上传的图像文件，返回临时文件路径
    
    Args:
        file: 上传的文件对象
    
    Returns:
        str: 临时文件路径
    """
    # 创建临时文件保存上传的图片
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
    temp_file_path = temp_file.name
    temp_file.close()
    print("临时文件路径:", temp_file_path)
    
    # 保存上传的图像文件
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # 使用PIL打开图像以确保它是有效的图像
    PILImage.open(temp_file_path)
    
    return temp_file_path

def search_handler(error_code: str = "SEARCH_ERROR"):
    """
    装饰器函数，处理搜索函数中的异常和结果格式化
    
    Args:
        error_code: 错误代码前缀
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                # 提取可能存在的limit和offset参数
                limit = kwargs.get('limit', 20)
                if isinstance(limit, CommonFilterParams):
                    limit = limit.limit
                    
                offset = kwargs.get('offset', 0)
                if isinstance(offset, CommonFilterParams):
                    offset = offset.offset
                
                # 执行搜索函数
                results = await func(*args, **kwargs)
                
                # 如果函数已经返回了完整的响应，直接返回
                if isinstance(results, dict) and 'status' in results:
                    return results
                
                # 处理JSON字段
                if isinstance(results, list):
                    results = process_json_fields(results)
                
                # 创建分页响应
                return create_paginated_response(
                    results=results,
                    limit=limit,
                    offset=offset,
                    message=f"{func.__name__}成功"
                )
            except Exception as e:
                traceback.print_exc()
                return handle_search_error(
                    e=e,
                    limit=limit if 'limit' in locals() else 20,
                    offset=offset if 'offset' in locals() else 0,
                    error_code=error_code
                )
        return wrapper
    return decorator

def cleanup_temp_file(file_path: str) -> None:
    """
    清理临时文件
    
    Args:
        file_path: 临时文件路径
    """
    if os.path.exists(file_path):
        try:
            os.unlink(file_path)
        except PermissionError:
            # 文件可能仍在使用中，稍后将被系统自动清理
            print(f"无法删除临时文件 {file_path}，文件可能仍在使用中")

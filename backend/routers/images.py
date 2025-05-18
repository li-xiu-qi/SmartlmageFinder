from fastapi import (
    APIRouter,
    Query,
    Path,
    UploadFile,
    File,
    Form,
    Depends,
)
import sqlite3
from typing import List, Optional
import os
import shutil
from datetime import datetime
import json
from PIL import Image as PILImage
import uuid

# 导入数据库和数据模型
from ..db_func.core import get_db
from ..db_func.images_func.create import add_image_to_database
from ..db_func.images_func.get import get_image_by_id, get_images
from ..db_func.images_func.update import update_image as db_update_image
from ..db_func.images_func.delete import delete_image as db_delete_image
from ..global_schemas import ResponseModel, ErrorModel

# 添加配置导入
from ..config import settings


# 创建路由器
router = APIRouter(prefix="/api/v1/images", tags=["images"])


@router.get("/", response_model=ResponseModel)
async def list_images(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    sort_by: str = Query("created_at", description="排序字段"),
    order: str = Query("desc", description="排序方向"),
    start_date: Optional[str] = Query(None, description="开始日期过滤"),
    end_date: Optional[str] = Query(None, description="结束日期过滤"),
    tags: Optional[List[str]] = Query(None, description="标签过滤，可以是数组形式"),
    db: sqlite3.Connection = Depends(get_db),
):
    """获取图片列表，支持分页和各种过滤条件"""
    try:
        # 获取图片列表和总数
        images, total_count = get_images(
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            order=order,
            start_date=start_date,
            end_date=end_date,
            tags=tags,
            conn=db
        )
        
        # 使用分页响应
        return ResponseModel.paginated_response(
            data=images,
            page=page,
            page_size=page_size,
            total_items=total_count,
            message="获取图片列表成功"
        )
    except Exception as e:
        return ResponseModel.error(
            code="IMAGE_LIST_ERROR",
            message=f"获取图片列表失败: {str(e)}",
            http_code=500
        )


@router.get("/{image_id}", response_model=ResponseModel)
async def get_image(
    image_id: int = Path(..., description="图片ID"),
    db: sqlite3.Connection = Depends(get_db),
):
    """通过ID获取单张图片的详细信息"""
    try:
        image = get_image_by_id(db, image_id)
        if not image:
            return ResponseModel.error(
                code="IMAGE_NOT_FOUND",
                message=f"找不到ID为 {image_id} 的图片",
                http_code=404
            )
        
        return ResponseModel.success(
            data=image,
            message="获取图片信息成功"
        )
    except Exception as e:
        return ResponseModel.error(
            code="IMAGE_GET_ERROR",
            message=f"获取图片信息失败: {str(e)}",
            http_code=500
        )


@router.post("/upload", response_model=ResponseModel)
async def upload_images(
    files: List[UploadFile] = File(..., description="上传的图片文件"),
    title: Optional[str] = Form(None, description="图片标题"),
    description: Optional[str] = Form(None, description="图片描述"),
    tags: Optional[str] = Form(None, description="图片标签，JSON数组字符串"),
    metadata: Optional[str] = Form(None, description="图片元数据，JSON字符串"),
    db: sqlite3.Connection = Depends(get_db),
):
    """上传图片文件并存储到数据库"""
    try:
        # 解析标签和元数据 - 使用 json.loads 解析字符串
        tag_list = json.loads(tags) if tags and isinstance(tags, str) else []
        meta_dict = json.loads(metadata) if metadata and isinstance(metadata, str) else {}
        
        # 确保上传目录存在
        upload_dir = settings.get_config().UPLOAD_DIR
        os.makedirs(upload_dir, exist_ok=True)
        
        uploaded_images = []
        for file in files:
            # 生成文件名和路径
            original_filename = file.filename
            file_ext = original_filename.split(".")[-1]
            unique_filename = f"{uuid.uuid4().hex}.{file_ext}"
            file_path = os.path.join(upload_dir, unique_filename)
            
            # 保存文件
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # 获取图像信息
            try:
                with PILImage.open(file_path) as img:
                    width, height = img.size
                    file_size = os.path.getsize(file_path)
            except Exception as e:
                return ResponseModel.error(
                    code="IMAGE_PROCESSING_ERROR",
                    message=f"处理图像失败: {str(e)}",
                    http_code=400
                )
            # 准备图像数据，tags 和 metadata 将由 add_image_to_database 处理序列化
            image_data = {
                "filename": original_filename,
                "filepath": file_path,
                "title": title or original_filename,
                "description": description or "",
                "file_size": file_size,
                "file_type": file_ext,
                "width": width,
                "height": height,
                "created_at": datetime.now().isoformat(),
                "tags": tag_list,
                "metadata": meta_dict
            }
            
            # 添加到数据库
            image_id = add_image_to_database(db, image_data)
            
            # 获取新添加的图像信息
            image = get_image_by_id(db, image_id)
            uploaded_images.append(image)
        return ResponseModel.success(
            data=uploaded_images,
            message=f"成功上传 {len(uploaded_images)} 个文件"
        )
    except Exception as e:
        # 使用自定义错误响应
        return ResponseModel(
            status="error",
            code=500,
            message=f"上传图片失败: {str(e)}",
            data=None,
            error=ErrorModel(
                code="UPLOAD_ERROR",
                message=f"上传图片失败: {str(e)}"
            )
        )


@router.patch("/{image_id}", response_model=ResponseModel)
async def update_image(
    image_id: int = Path(..., description="图片ID"),
    title: Optional[str] = Form(None, description="图片标题"),
    description: Optional[str] = Form(None, description="图片描述"),
    tags: Optional[str] = Form(None, description="图片标签，JSON数组字符串"),
    metadata: Optional[str] = Form(None, description="图片元数据，JSON字符串"),
    db: sqlite3.Connection = Depends(get_db),
):
    """更新图片信息"""
    try:
        # 准备更新数据
        update_data = {}
        
        if title is not None:
            update_data["title"] = title
        
        if description is not None:
            update_data["description"] = description
        if tags is not None:
            tag_data = json.loads(tags) if isinstance(tags, str) else tags
            update_data["tags"] = tag_data
        
        if metadata is not None:
            meta_data = json.loads(metadata) if isinstance(metadata, str) else metadata
            update_data["metadata"] = meta_data
        
        # 如果没有要更新的数据，返回错误
        if not update_data:
            return ResponseModel.error(
                code="NO_UPDATE_DATA",
                message="没有提供要更新的数据",
                http_code=400
            )
        
        # 执行更新
        success = db_update_image(db, image_id, update_data)
        
        if not success:
            return ResponseModel.error(
                code="IMAGE_NOT_FOUND",
                message=f"找不到ID为 {image_id} 的图片",
                http_code=404
            )
        
        # 获取更新后的图片
        updated_image = get_image_by_id(db, image_id)
        
        return ResponseModel.success(
            data=updated_image,
            message="图片信息更新成功"
        )
    except Exception as e:
        return ResponseModel.error(
            code="UPDATE_ERROR",
            message=f"更新图片失败: {str(e)}",
            http_code=500
        )


@router.delete("/{image_id}", response_model=ResponseModel)
async def delete_image(
    image_id: int = Path(..., description="图片ID"),
    db: sqlite3.Connection = Depends(get_db),
):
    """删除图片及其关联数据"""
    try:
        # 先获取图片信息，以便删除文件
        image = get_image_by_id(db, image_id)
        
        if not image:
            return ResponseModel.error(
                code="IMAGE_NOT_FOUND",
                message=f"找不到ID为 {image_id} 的图片",
                http_code=404
            )
        
        # 从数据库删除图片记录
        success = db_delete_image(db, image_id)
        
        if success and os.path.exists(image.get('filepath', '')):
            try:
                # 删除物理文件
                os.remove(image['filepath'])
            except Exception as file_e:
                # 文件删除失败不影响整体操作
                print(f"删除文件失败: {file_e}")
        
        return ResponseModel.success(
            data=None,
            message="图片删除成功"
        )
    except Exception as e:
        return ResponseModel.error(
            code="DELETE_ERROR",
            message=f"删除图片失败: {str(e)}",
            http_code=500
        )


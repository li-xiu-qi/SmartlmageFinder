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
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import shutil
from datetime import datetime
import json
from PIL import Image as PILImage
import uuid

# 导入数据库和数据模型
from ..db_func.core import get_db
from ..db_func.images_func.create import batch_add_images_to_database
from ..db_func.images_func.get import get_image_by_id, get_images
from ..db_func.images_func.update import update_image as db_update_image
from ..db_func.images_func.delete import delete_image as db_delete_image, batch_delete_images as db_batch_delete_images
from ..global_schemas import ResponseModel

# 添加配置导入
from ..config import settings


# 创建路由器
router = APIRouter(prefix="/api/v1/images", tags=["images"])


class BatchDeleteRequest(BaseModel):
    image_ids: List[int]


@router.get("/")
async def list_images(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    sort_by: str = Query("created_at", description="排序字段"),
    order: str = Query("desc", description="排序方向"),
    start_date: Optional[str] = Query(None, description="开始日期过滤"),
    end_date: Optional[str] = Query(None, description="结束日期过滤"),
    tags: Optional[List[str]] = Query(None, alias="tags[]", description="标签过滤，可以是数组形式"),
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


@router.get("/{image_id}")
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


@router.post("/upload")
async def upload_images(
    files: List[UploadFile] = File(..., description="上传的图片文件"),
    title: Optional[str] = Form(None, description="图片标题"),
    description: Optional[str] = Form(None, description="图片描述"),
    tags: Optional[str] = Form(None, description="图片标签，JSON数组字符串"),
    metadata: Optional[str] = Form(None, description="图片元数据，JSON字符串"),
    db: sqlite3.Connection = Depends(get_db),
):
    """上传图片文件并存储到数据库，支持单个或批量上传"""
    try:
        # 获取配置
        config = settings.get_config()
        if not config:
            return ResponseModel.error(
                code="CONFIG_ERROR",
                message="系统配置未正确加载",
                http_code=500
            )
        
        upload_dir = config.UPLOAD_DIR
        
        # 确保上传目录存在
        os.makedirs(upload_dir, exist_ok=True)
        
        # 解析可选参数
        tag_list = []
        if tags:
            try:
                tag_list = json.loads(tags) if isinstance(tags, str) else tags
            except json.JSONDecodeError:
                tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
        
        meta_dict = {}
        if metadata:
            try:
                meta_dict = json.loads(metadata) if isinstance(metadata, str) else metadata
            except json.JSONDecodeError:
                meta_dict = {}
        
        # 批量上传处理
        return await _upload_images(files, title, description, tag_list, meta_dict, upload_dir, db)
        
    except Exception as e:
        return ResponseModel.error(
            code="UPLOAD_ERROR",
            message=f"上传图片失败: {str(e)}",
            http_code=500
        )


async def _upload_images(
    files: List[UploadFile], 
    title: Optional[str], 
    description: Optional[str],
    tag_list: List[str], 
    meta_dict: Dict[str, Any],
    upload_dir: str,
    db: sqlite3.Connection
):
    """批量上传图片处理函数（兼容单个文件）"""
    print(f"批量处理模式，共 {len(files)} 个文件")
    
    # 第一步：批量保存文件并收集信息
    images_data = []
    uploaded_files = []
    
    for file in files:
        try:
            # 生成唯一文件名
            file_extension = os.path.splitext(file.filename)[1].lower()
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            file_path = os.path.join(upload_dir, unique_filename)
            
            # 保存文件
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            uploaded_files.append(file_path)
            
            # 获取图片信息
            with PILImage.open(file_path) as img:
                width, height = img.size
            
            file_size = os.path.getsize(file_path)
            
            # 准备数据库记录
            image_data = {
                'filename': file.filename,
                'filepath': file_path,
                'title': title or os.path.splitext(file.filename)[0],
                'description': description or '',
                'file_size': file_size,
                'file_type': file.content_type,
                'width': width,
                'height': height,
                'tags': tag_list,
                'metadata': meta_dict
            }
            images_data.append(image_data)
            
        except Exception as e:
            # 如果处理单个文件失败，清理已上传的文件
            for uploaded_file in uploaded_files:
                try:
                    os.remove(uploaded_file)
                except:
                    pass
            raise Exception(f"处理文件 {file.filename} 失败: {str(e)}")
    
    # 第二步：批量添加到数据库（包括批量生成向量）
    try:
        image_ids = batch_add_images_to_database(db, images_data)
        
        # 第三步：获取所有图像信息返回
        uploaded_images = []
        for image_id in image_ids:
            image = get_image_by_id(db, image_id)
            if image:
                uploaded_images.append(image)
        
        return ResponseModel.success(
            data=uploaded_images,
            message=f"上传成功，共处理 {len(uploaded_images)} 个文件"
        )
        
    except Exception as e:
        # 数据库操作失败，清理已上传的文件
        for uploaded_file in uploaded_files:
            try:
                os.remove(uploaded_file)
            except:
                pass
        raise e


@router.patch("/{image_id}")
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
        # 检查图片是否存在
        existing_image = get_image_by_id(db, image_id)
        if not existing_image:
            return ResponseModel.error(
                code="IMAGE_NOT_FOUND",
                message=f"找不到ID为 {image_id} 的图片",
                http_code=404
            ).to_dict()
        
        # 解析标签
        tag_list = None
        if tags is not None:
            try:
                tag_list = json.loads(tags) if isinstance(tags, str) else tags
            except json.JSONDecodeError:
                tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
        
        # 解析元数据
        meta_dict = None
        if metadata is not None:
            try:
                meta_dict = json.loads(metadata) if isinstance(metadata, str) else metadata
            except json.JSONDecodeError:
                meta_dict = {}
        
        # 更新图片信息
        update_data = {}
        if title is not None:
            update_data['title'] = title
        if description is not None:
            update_data['description'] = description
        if tag_list is not None:
            update_data['tags'] = tag_list
        if meta_dict is not None:
            update_data['metadata'] = meta_dict
            
        success = db_update_image(
            conn=db,
            image_id=image_id,
            update_data=update_data
        )
        
        if success:
            # 获取更新后的图片信息
            updated_image = get_image_by_id(db, image_id)
            return ResponseModel.success(
                data=updated_image,
                message="图片信息更新成功"
            ).to_dict()
        else:
            return ResponseModel.error(
                code="UPDATE_ERROR",
                message="更新图片信息失败",
                http_code=500
            ).to_dict()
            
    except Exception as e:
        return ResponseModel.error(
            code="UPDATE_ERROR",
            message=f"更新图片信息失败: {str(e)}",
            http_code=500
        ).to_dict()


@router.delete("/batch")
async def batch_delete_images(
    request: BatchDeleteRequest,
    db: sqlite3.Connection = Depends(get_db),
):
    """批量删除图片及其关联数据"""
    try:
        if not request.image_ids:
            return ResponseModel.error(
                code="INVALID_REQUEST",
                message="图片ID列表不能为空",
                http_code=400
            )
        
        # 先获取所有图片信息，以便删除文件
        image_files_to_delete = []
        for image_id in request.image_ids:
            try:
                image = get_image_by_id(db, image_id)
                if image and image.get('filepath'):
                    image_files_to_delete.append((image_id, image['filepath']))
            except Exception as e:
                print(f"获取图片 {image_id} 信息失败: {e}")
        
        # 使用批量删除函数
        result = db_batch_delete_images(db, request.image_ids)
        
        # 删除成功的图片文件
        deleted_files = []
        for image_id, filepath in image_files_to_delete:
            if image_id not in result['failed_ids'] and os.path.exists(filepath):
                try:
                    os.remove(filepath)
                    deleted_files.append(filepath)
                except Exception as file_e:
                    print(f"删除文件 {filepath} 失败: {file_e}")
        
        # 构建响应消息
        message = f"批量删除完成，成功删除 {result['success_count']} 张图片"
        if result['failed_count'] > 0:
            message += f"，失败 {result['failed_count']} 张图片"
        
        # 构建响应数据，与前端期望的类型匹配
        response_data = {
            "success_count": result['success_count'],
            "failed_count": result['failed_count'],
            "total_count": result['total_count'],
            "failed_ids": result['failed_ids'],
            "deleted_files": deleted_files
        }
        
        # 如果有错误详情，也包含进去
        if result.get('errors'):
            response_data['errors'] = result['errors']
        
        return ResponseModel.success(
            data=response_data,
            message=message
        )
        
    except Exception as e:
        return ResponseModel.error(
            code="BATCH_DELETE_ERROR",
            message=f"批量删除图片失败: {str(e)}",
            http_code=500
        )


@router.delete("/{image_id}")
async def delete_image(
    image_id: int = Path(..., description="图片ID"),
    db: sqlite3.Connection = Depends(get_db),
):
    """删除单张图片及其关联数据"""
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
        
        if not success:
            return ResponseModel.error(
                code="DELETE_ERROR",
                message="删除图片记录失败",
                http_code=500
            )
        
        # 删除物理文件
        try:
            if os.path.exists(image.get('filepath', '')):
                os.remove(image['filepath'])
                print(f"已删除文件: {image['filepath']}")
        except Exception as file_e:
            print(f"删除文件失败: {file_e}")
        
        return ResponseModel.success(
            data=None,
            message="图片删除成功"
        )
    except Exception as e:        return ResponseModel.error(
            code="DELETE_ERROR",
            message=f"删除图片失败: {str(e)}",
            http_code=500
        )

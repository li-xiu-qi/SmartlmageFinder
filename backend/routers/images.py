"""
图片相关的路由
"""
import os
import json
import shutil
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, Query
from pydantic import BaseModel

# 导入数据库连接函数
from ..db_func.core.connection import get_db
# 导入响应模型
from ..global_schemas import ResponseModel
# 导入图片相关的数据库操作
from ..db_func.repositories.images import ImageRepository

router = APIRouter()

# 请求模型
class ImageUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

class BatchDeleteRequest(BaseModel):
    image_ids: List[int]

class BatchUpdateRequest(BaseModel):
    image_ids: List[int]
    updates: dict

@router.get("/")
async def get_images_list(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    sort_by: str = Query("created_at", description="排序字段"),
    order: str = Query("desc", description="排序方向 (asc/desc)"),
    filename: Optional[str] = Query(None, description="文件名过滤"),
    title: Optional[str] = Query(None, description="标题过滤"),
    description: Optional[str] = Query(None, description="描述过滤"),
    tags: Optional[str] = Query(None, description="标签过滤 (逗号分隔)"),
    start_date: Optional[str] = Query(None, description="开始日期 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="结束日期 (YYYY-MM-DD)"),
    conn = Depends(get_db)
):
    """获取图片列表"""
    try:
        # 构建过滤条件
        filters = {}
        if filename:
            filters['filename'] = filename
        if title:
            filters['title'] = title
        if description:
            filters['description'] = description
        if start_date:
            filters['start_date'] = start_date
        if end_date:
            filters['end_date'] = end_date
        if tags:
            # 将逗号分隔的标签字符串转换为列表
            filters['tags'] = [tag.strip() for tag in tags.split(',') if tag.strip()]
        
        image_repo = ImageRepository()
        images, total_count = image_repo.get_list(
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            order=order,
            filters=filters
        )
        
        return ResponseModel.paginated_response(
            data=images,
            page=page,
            page_size=page_size,
            total_items=total_count,
            message="获取图片列表成功"
        )
    except Exception as e:
        return ResponseModel.error(
            code="FETCH_IMAGES_ERROR",
            message=f"获取图片列表失败: {str(e)}"
        )

@router.get("/{image_id}")
async def get_image_by_id(
    image_id: int,
    conn = Depends(get_db)
):
    """根据ID获取单个图片信息"""
    try:
        image_repo = ImageRepository()
        image = image_repo.get_by_id(image_id)
        
        if not image:
            return ResponseModel.error(
                code="IMAGE_NOT_FOUND",
                message="图片不存在",
                http_code=404
            )
        
        return ResponseModel.success(
            data=image,
            message="获取图片信息成功"
        )
    except Exception as e:
        return ResponseModel.error(
            code="FETCH_IMAGE_ERROR",
            message=f"获取图片信息失败: {str(e)}"
        )

@router.post("/upload")
async def upload_images(
    files: List[UploadFile] = File(...),
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    auto_analyze: bool = Form(True),
    conn = Depends(get_db)
):
    """上传图片"""
    try:
        from ..config.config import Settings
        from ..ai_func.analyze_image_id import analyze_image_id
        from ..ai_func.image_analysis import ImageAnalysis
        
        # 获取配置
        settings = Settings()
        upload_dir = settings.get_config().UPLOAD_DIR
        
        # 确保上传目录存在
        os.makedirs(upload_dir, exist_ok=True)
        
        uploaded_images = []
        
        for file in files:
            # 验证文件类型
            if not file.content_type or not file.content_type.startswith('image/'):
                continue
            
            # 生成唯一文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            filename = f"{timestamp}_{file.filename}"
            filepath = os.path.join(upload_dir, filename)
            
            # 保存文件
            with open(filepath, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # 获取文件信息
            file_stat = os.stat(filepath)
            file_size = file_stat.st_size
            
            # 基础图片信息
            image_data = {
                'filename': file.filename,
                'filepath': filepath,
                'title': title or file.filename,
                'description': description or '',
                'file_size': file_size,
                'file_type': file.content_type,
                'width': 0,  # 后续可以通过PIL获取
                'height': 0,
                'created_at': datetime.now(),
                'updated_at': datetime.now(),
                'metadata': '{}',
                'tags': '[]'
            }
            
            uploaded_images.append(image_data)
        
        if not uploaded_images:
            return ResponseModel.error(
                code="NO_VALID_IMAGES",
                message="没有有效的图片文件"
            )
        
        # 批量插入数据库
        image_repo = ImageRepository()
        image_ids = image_repo.batch_create(uploaded_images)
        
        # 获取插入后的完整信息
        result_images = []
        for image_id in image_ids:
            image = image_repo.get_by_id(image_id)
            if image:
                result_images.append(image)
        
        # 如果启用自动分析，异步处理
        if auto_analyze:
            # 创建图像分析器实例
            image_analyzer = ImageAnalysis()
            for image_id in image_ids:
                try:
                    analyze_image_id(image_analyzer, image_id)
                except Exception as e:
                    print(f"自动分析图片 {image_id} 失败: {str(e)}")
        
        return ResponseModel.success(
            data=result_images,
            message=f"成功上传 {len(result_images)} 张图片"
        )
        
    except Exception as e:
        return ResponseModel.error(
            code="UPLOAD_ERROR",
            message=f"上传失败: {str(e)}"
        )

@router.put("/{image_id}")
async def update_image(
    image_id: int,
    request: ImageUpdateRequest,
    conn = Depends(get_db)
):
    """更新图片信息"""
    try:
        image_repo = ImageRepository()
        
        # 检查图片是否存在
        existing_image = image_repo.get_by_id(image_id)
        if not existing_image:
            return ResponseModel.error(
                code="IMAGE_NOT_FOUND",
                message="图片不存在",
                http_code=404
            )
        
        # 准备更新数据
        update_data = {}
        if request.title is not None:
            update_data['title'] = request.title
        if request.description is not None:
            update_data['description'] = request.description
        
        if not update_data:
            return ResponseModel.error(
                code="NO_UPDATE_DATA",
                message="没有提供更新数据"
            )
        
        # 添加更新时间
        update_data['updated_at'] = datetime.now()
        
        # 执行更新
        success = image_repo.update(image_id, update_data)
        
        if success:
            # 获取更新后的数据
            updated_image = image_repo.get_by_id(image_id)
            return ResponseModel.success(
                data=updated_image,
                message="图片信息更新成功"
            )
        else:
            return ResponseModel.error(
                code="UPDATE_FAILED",
                message="更新失败"
            )
            
    except Exception as e:
        return ResponseModel.error(
            code="UPDATE_ERROR",
            message=f"更新图片信息失败: {str(e)}"
        )

@router.delete("/batch")
async def batch_delete_images(
    request: BatchDeleteRequest,
    conn = Depends(get_db)
):
    """批量删除图片"""
    try:
        if not request.image_ids:
            return ResponseModel.error(
                code="NO_IMAGE_IDS",
                message="没有提供要删除的图片ID"
            )
        
        image_repo = ImageRepository()
        
        # 获取要删除的图片信息（用于删除文件）
        images_to_delete = []
        for image_id in request.image_ids:
            image = image_repo.get_by_id(image_id)
            if image:
                images_to_delete.append(image)
        
        # 从数据库删除
        result = image_repo.batch_delete(request.image_ids)
        
        # 删除实际文件
        deleted_files = []
        for image in images_to_delete:
            try:
                if os.path.exists(image['filepath']):
                    os.remove(image['filepath'])
                    deleted_files.append(image['filepath'])
            except Exception as e:
                print(f"删除文件失败 {image['filepath']}: {str(e)}")
        
        return ResponseModel.success(
            data={
                "deleted_count": result.get('deleted_count', 0),
                "deleted_files": deleted_files
            },
            message=f"成功删除 {result.get('deleted_count', 0)} 张图片"
        )
        
    except Exception as e:
        return ResponseModel.error(
            code="BATCH_DELETE_ERROR",
            message=f"批量删除失败: {str(e)}"
        )

@router.delete("/{image_id}")
async def delete_image(
    image_id: int,
    conn = Depends(get_db)
):
    """删除单张图片"""
    try:
        image_repo = ImageRepository()
        
        # 获取图片信息
        image = image_repo.get_by_id(image_id)
        if not image:
            return ResponseModel.error(
                code="IMAGE_NOT_FOUND",
                message="图片不存在",
                http_code=404
            )
        
        # 从数据库删除
        success = image_repo.delete(image_id)
        
        if success:
            # 删除实际文件
            try:
                if os.path.exists(image['filepath']):
                    os.remove(image['filepath'])
            except Exception as e:
                print(f"删除文件失败 {image['filepath']}: {str(e)}")
            
            return ResponseModel.success(
                message="图片删除成功"
            )
        else:
            return ResponseModel.error(
                code="DELETE_FAILED",
                message="删除失败"
            )
            
    except Exception as e:
        return ResponseModel.error(
            code="DELETE_ERROR",
            message=f"删除图片失败: {str(e)}"
        )

@router.post("/batch-update")
async def batch_update_images(
    request: BatchUpdateRequest,
    conn = Depends(get_db)
):
    """批量更新图片"""
    try:
        if not request.image_ids:
            return ResponseModel.error(
                code="NO_IMAGE_IDS",
                message="没有提供要更新的图片ID"
            )
        
        if not request.updates:
            return ResponseModel.error(
                code="NO_UPDATE_DATA",
                message="没有提供更新数据"
            )
        
        image_repo = ImageRepository()
        
        # 添加更新时间
        update_data = request.updates.copy()
        update_data['updated_at'] = datetime.now()
        
        # 执行批量更新
        success_count = 0
        for image_id in request.image_ids:
            if image_repo.update(image_id, update_data):
                success_count += 1
        
        return ResponseModel.success(
            data={
                "updated_count": success_count,
                "total_count": len(request.image_ids)
            },
            message=f"成功更新 {success_count} 张图片"
        )
        
    except Exception as e:
        return ResponseModel.error(
            code="BATCH_UPDATE_ERROR",
            message=f"批量更新失败: {str(e)}"
        )

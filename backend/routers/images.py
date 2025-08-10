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
from PIL import Image as PILImage

# 导入数据库连接函数
# 数据访问通过仓库内部管理连接，无需显式依赖注入 get_db
# 导入响应模型
from ..global_schemas import ResponseModel
# 导入图片相关的数据库操作
from ..db_func.repositories.images import ImageRepository
from ..utils.image_utils import build_public_url

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


def _attach_public_url(image: dict) -> dict:
    if image and 'public_url' not in image:
        image['public_url'] = build_public_url(image.get('filepath') or '')
    return image

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
    tags_list: Optional[List[str]] = Query(None, alias="tags[]", description="标签过滤 (多值参数，等价于 tags 的数组形式)"),
    start_date: Optional[str] = Query(None, description="开始日期 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="结束日期 (YYYY-MM-DD)")
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
        # 统一处理标签过滤，兼容 tags=逗号分隔字符串 与 tags[]=多值数组
        merged_tags: List[str] = []
        if tags:
            merged_tags.extend([tag.strip() for tag in tags.split(',') if tag.strip()])
        if tags_list:
            for item in tags_list:
                if isinstance(item, str):
                    merged_tags.extend([t.strip() for t in item.split(',') if t.strip()])
        if merged_tags:
            # 去重
            filters['tags'] = list(set(merged_tags))
        
        image_repo = ImageRepository()
        images, total_count = image_repo.get_list(
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            order=order,
            filters=filters
        )
        
        # 添加 public_url
        images_with_url = [_attach_public_url(img) for img in images]
        return ResponseModel.paginated_response(
            data=images_with_url,
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
    image_id: int
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
            data=_attach_public_url(image),
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
    auto_analyze: bool = Form(True)
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
            
            # 获取文件信息 + 尺寸
            file_stat = os.stat(filepath)
            file_size = file_stat.st_size
            width = 0
            height = 0
            try:
                with PILImage.open(filepath) as im:
                    width, height = im.size
            except Exception as img_e:
                print(f"读取图片尺寸失败 {filepath}: {img_e}")
            
            # 基础图片信息
            image_data = {
                'filename': file.filename,
                'filepath': filepath,
                'title': title or file.filename,
                'description': description or '',
                'file_size': file_size,
                'file_type': file.content_type,
                'width': width,
                'height': height,
                'created_at': datetime.now(),
                'updated_at': datetime.now(),
                # 使用Python原生类型，入库时由仓库层统一转换为JSON字符串
                'metadata': {},
                'tags': []
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
                result_images.append(_attach_public_url(image))
        
        # 如果启用自动分析：执行分析并将结果写回数据库（同步简单实现，后续可改为后台任务）
        if auto_analyze:
            image_analyzer = ImageAnalysis()
            for image_id in image_ids:
                try:
                    analysis = analyze_image_id(image_analyzer, image_id)
                    if analysis and not analysis.get("error"):
                        # 仅当分析成功且至少有一个字段非空才更新
                        update_payload = {}
                        if analysis.get("title"):
                            update_payload["title"] = analysis.get("title")
                        if analysis.get("description"):
                            update_payload["description"] = analysis.get("description")
                        # tags 必须是列表且非空
                        tags_field = analysis.get("tags")
                        if isinstance(tags_field, list) and tags_field:
                            update_payload["tags"] = tags_field
                        if update_payload:
                            image_repo.update(image_id, update_payload)
                except Exception as e:
                    print(f"自动分析图片 {image_id} 失败: {str(e)}")

            # 重新获取最新信息（包含回填）
            refreshed = []
            for image_id in image_ids:
                img = image_repo.get_by_id(image_id)
                if img:
                    refreshed.append(_attach_public_url(img))
            if refreshed:
                result_images = refreshed
        
        # 同步生成向量（标题/描述/图像）
        if image_ids:
            try:
                from ..db_func.repositories.batch_vector_manager import BatchVectorManager
                from ..db_func.core.connection import get_db_connection
                batch_source = [{
                    'image_id': img['id'],
                    'filepath': img.get('filepath'),
                    'title': img.get('title') or '',
                    'description': img.get('description') or ''
                } for img in result_images]
                with get_db_connection() as conn:
                    mgr = BatchVectorManager(conn)
                    processed_ids = mgr.add_batch_vectors(batch_source)
                    print(f"上传后自动生成向量完成: {len(processed_ids)} 张图片")
            except Exception as e:
                print(f"上传后自动生成向量失败: {e}")

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
    request: ImageUpdateRequest
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
            if updated_image:
                # 内部策略：仅对本次明确更新的字段生成对应向量
                try:
                    from ..db_func.repositories.vectors import VectorRepository
                    vec_repo = VectorRepository()
                    if request.title is not None:
                        vec_repo.add_title_vector(image_id, updated_image.get('title') or '')
                    if request.description is not None:
                        vec_repo.add_description_vector(image_id, updated_image.get('description') or '')
                    print(f"更新后已重建相关文本向量: image_id={image_id}")
                except Exception as e:
                    print(f"更新后重建向量失败: {e}")
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
    request: BatchDeleteRequest
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
    image_id: int
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
    request: BatchUpdateRequest
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

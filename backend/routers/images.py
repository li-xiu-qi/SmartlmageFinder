from fastapi import APIRouter, HTTPException, Query, Path, UploadFile, File, Form, BackgroundTasks
from typing import List, Optional, Dict, Any
from ..schemas import ResponseModel, ImageResponse, ImageListItem, ImageUpdate
import os
import shutil
from datetime import datetime
import json
from PIL import Image as PILImage
from .. import db
from ..config import settings
router = APIRouter(prefix="/images", tags=["images"])



@router.get("/", response_model=ResponseModel)
async def get_images(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    sort_by: str = Query("created_at", description="排序字段"),
    order: str = Query("desc", description="排序方向"),
    start_date: Optional[str] = Query(None, description="开始日期过滤"),
    end_date: Optional[str] = Query(None, description="结束日期过滤"),
    tags: Optional[List[str]] = Query(None,alias="tags[]", description="标签过滤，可以是数组形式") # 由于前端发送的是tags[]，所以这里需要使用alias来处理
):
    
    """获取图片列表，支持分页、排序和多种过滤"""
    # 处理标签过滤
    tag_list = None
    if tags:
        tag_list = [tag.strip() for tag in tags if tag.strip()]
    print("tags:", tags)
    print("tags_type:", type(tags))
    print("tag_list:", tag_list)
    # 获取图片列表和总数
    images, total_count = db.get_images(
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        order=order,
        start_date=start_date,
        end_date=end_date,
        tags=tag_list
    )
    
    # 转换为前端需要的格式
    image_list = []
    for image in images:
        image_list.append({
            "uuid": image["uuid"],
            "title": image["title"],
            "filepath": image["filepath"],
            "created_at": image["created_at"],
            "tags": image["tags"]
        })
    
    # 计算总页数
    total_pages = (total_count + page_size - 1) // page_size
    
    # 构建响应
    return ResponseModel.success(
        data={"images": image_list},
        metadata={
            "page": page,
            "page_size": page_size,
            "total": total_count,
            "total_pages": total_pages
        }
    )

@router.get("/{uuid}", response_model=ResponseModel)
async def get_image(uuid: str = Path(..., description="图片UUID")):
    """获取图片详细信息"""
    image = db.get_image_by_uuid(uuid)
    if not image:
        return ResponseModel.error(
            code="NOT_FOUND",
            message="图片不存在"
        )
    
    # 返回图片信息
    return ResponseModel.success(data=image)

@router.post("/upload", response_model=ResponseModel)
async def upload_images(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(..., description="上传的图片文件"),
    metadata: Optional[str] = Form(None, description="图片元数据，JSON字符串"),
    title: Optional[str] = Form(None, description="图片标题"),
    description: Optional[str] = Form(None, description="图片描述"),
    tags: Optional[str] = Form(None, description="图片标签，JSON数组字符串"),
):
    """上传单张或多张图片"""
    # 确保上传目录存在
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    # 解析元数据
    common_metadata = {}
    if metadata:
        try:
            common_metadata = json.loads(metadata)
        except json.JSONDecodeError:
            return ResponseModel.error(
                code="INVALID_REQUEST",
                message="元数据JSON格式无效"
            )
    
    # 解析标签
    common_tags = []
    if tags:
        try:
            common_tags = json.loads(tags)
            if not isinstance(common_tags, list):
                return ResponseModel.error(
                    code="INVALID_REQUEST",
                    message="标签必须是JSON数组格式"
                )
        except json.JSONDecodeError:
            return ResponseModel.error(
                code="INVALID_REQUEST",
                message="标签JSON格式无效"
            )
    
    uploaded = []
    failed = []
    
    for file in files:
        try:
            # 生成基于日期的子目录
            today = datetime.now().strftime("%Y/%m/%d")
            save_dir = os.path.join(settings.UPLOAD_DIR, today)
            os.makedirs(save_dir, exist_ok=True)
            
            # 生成文件路径
            file_ext = os.path.splitext(file.filename)[1]
            save_path = os.path.join(save_dir, f"{datetime.now().strftime('%H%M%S')}_{file.filename}")
            
            # 保存文件
            with open(save_path, "wb") as f:
                shutil.copyfileobj(file.file, f)
            
            # 获取图片尺寸
            width = height = None
            try:
                with PILImage.open(save_path) as img:
                    width, height = img.size
            except:
                pass
            
            # 创建图片记录
            image_data = {
                "filename": file.filename,
                "filepath": save_path.replace("\\", "/"),
                "file_size": os.path.getsize(save_path),
                "file_type": file_ext.lstrip(".").lower(),
                "width": width,
                "height": height,
                "metadata": common_metadata,
                "tags": common_tags,
                "title": title,
                "description": description
            }
            
            # 保存到数据库
            created_image = db.create_image(image_data)
            
            uploaded.append({
                "uuid": created_image["uuid"],
                "original_filename": file.filename,
                "file_size": image_data["file_size"],
                "stored_path": image_data["filepath"]
            })
            

        except Exception as e:
            failed.append({
                "filename": file.filename,
                "error": str(e)
            })
    
    # 构建响应
    return ResponseModel.success(
        data={
            "uploaded": uploaded,
            "failed": failed
        },
        metadata={
            "total": len(files),
            "success": len(uploaded),
            "failed": len(failed)
        }
    )

@router.patch("/{uuid}", response_model=ResponseModel)
async def update_image(
    update_data: ImageUpdate,
    uuid: str = Path(..., description="图片UUID")
):
    """更新图片信息（标题、描述、标签或元数据）"""
    # 更新图片
    updated_image = db.update_image(uuid, update_data.dict(exclude_none=True))
    
    if not updated_image:
        return ResponseModel.error(
            code="NOT_FOUND",
            message="图片不存在"
        )
    
    # 返回更新后的简要信息
    return ResponseModel.success(
        data={
            "uuid": updated_image["uuid"],
            "title": updated_image["title"],
            "updated_at": updated_image["updated_at"]
        }
    )

@router.delete("/{uuid}", response_model=ResponseModel)
async def delete_image(uuid: str = Path(..., description="图片UUID")):
    """删除指定的图片及其所有元数据"""
    # 获取图片信息（用于后续删除文件）
    image = db.get_image_by_uuid(uuid)
    if not image:
        return ResponseModel.error(
            code="NOT_FOUND",
            message="图片不存在"
        )
    
    # 删除数据库记录
    success = db.delete_image(uuid)
    
    if not success:
        return ResponseModel.error(
            code="DATABASE_ERROR",
            message="删除图片失败"
        )
    
    # 尝试删除文件（如果存在）
    try:
        if os.path.exists(image["filepath"]):
            os.remove(image["filepath"])
    except Exception as e:
        # 文件删除失败不影响整体操作
        pass
    
    return ResponseModel.success(
        data={
            "message": "图片已成功删除"
        }
    )

@router.delete("/", response_model=ResponseModel)
async def batch_delete_images(uuids: List[str]):
    """批量删除多张图片"""
    deleted = 0
    failed = 0
    details = []
    
    for uuid in uuids:
        # 获取图片信息
        image = db.get_image_by_uuid(uuid)
        if not image:
            failed += 1
            details.append({
                "uuid": uuid,
                "status": "failed",
                "reason": "图片不存在"
            })
            continue
        
        # 删除数据库记录
        success = db.delete_image(uuid)
        
        if success:
            # 尝试删除文件
            try:
                if os.path.exists(image["filepath"]):
                    os.remove(image["filepath"])
            except Exception as e:
                # 文件删除失败不影响整体操作
                pass
                
            deleted += 1
            details.append({
                "uuid": uuid,
                "status": "deleted"
            })
        else:
            failed += 1
            details.append({
                "uuid": uuid,
                "status": "failed",
                "reason": "数据库删除失败"
            })
    
    return ResponseModel.success(
        data={
            "deleted": deleted,
            "failed": failed,
            "details": details if failed > 0 else []
        }
    )
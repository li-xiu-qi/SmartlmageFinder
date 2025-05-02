from fastapi import APIRouter, Query, Path
from typing import List, Optional
from ..schemas import ResponseModel, TagAddRequest
from .. import db

router = APIRouter(tags=["tags"])

@router.get("/tags", response_model=ResponseModel)
async def get_tags(limit: int = Query(50, ge=1, le=200, description="返回标签数量")):
    """获取系统中所有已使用标签及其使用频率"""
    tags = db.get_popular_tags(limit=limit)
    
    return ResponseModel.success(
        data={"tags": tags},
        metadata={"total": len(tags)}
    )

@router.post("/images/{uuid}/tags", response_model=ResponseModel)
async def add_tags_to_image(
    tag_data: TagAddRequest,
    uuid: str = Path(..., description="图片UUID")
):
    """为指定图片添加一个或多个标签"""
    # 添加标签
    updated_image = db.add_tags_to_image(uuid, tag_data.tags)
    
    if not updated_image:
        return ResponseModel.error(
            code="NOT_FOUND",
            message="图片不存在"
        )
    
    return ResponseModel.success(
        data={
            "uuid": updated_image["uuid"],
            "tags": updated_image["tags"]
        }
    )

@router.delete("/images/{uuid}/tags/{tag}", response_model=ResponseModel)
async def remove_tag_from_image(
    uuid: str = Path(..., description="图片UUID"),
    tag: str = Path(..., description="要删除的标签")
):
    """从指定图片中删除标签"""
    # 获取图片
    image = db.get_image_by_uuid(uuid)
    if not image:
        return ResponseModel.error(
            code="NOT_FOUND",
            message="图片不存在"
        )
    
    # 检查标签是否存在
    if tag not in image["tags"]:
        return ResponseModel.error(
            code="NOT_FOUND",
            message="标签不存在于该图片"
        )
    
    # 移除标签
    updated_image = db.remove_tag_from_image(uuid, tag)
    
    return ResponseModel.success(
        data={
            "uuid": updated_image["uuid"],
            "tags": updated_image["tags"]
        }
    )
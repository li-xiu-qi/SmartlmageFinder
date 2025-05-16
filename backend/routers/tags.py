from fastapi import APIRouter, Depends, Query, Path, Body, HTTPException
from typing import List, Optional, Dict, Set
from pydantic import BaseModel, Field
import json

from backend import db_func
from backend.db_func.core import get_db
from backend.db_func.images_func.get import get_images_by_tag, get_images_by_ids, get_image_by_id
from backend.db_func.tags_func.get_tags import get_tags_count, get_all_tags
from backend.global_schemas import ResponseModel


# 定义请求模型
class UpdateTagsRequest(BaseModel):
    tags: List[str] = Field(..., description="标签列表")


router = APIRouter(prefix="/tags", tags=["tags"])

@router.get("/", response_model=ResponseModel)
async def get_tags(
    limit: int = Query(50, ge=1, le=200, description="返回标签数量"),
    conn = Depends(get_db)
):
    """获取系统中所有已使用标签及其使用频率"""
    tag_counts = get_tags_count(conn)
    sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
    limited_tags = sorted_tags[:limit]
    result = [{"tag": tag, "count": count} for tag, count in limited_tags]
    
    return ResponseModel.success(
        data=result,
        message="成功获取标签列表",
        metadata={"total": len(tag_counts)}
    )


@router.get("/search", response_model=ResponseModel)
async def search_tags(
    query: str = Query(..., description="标签搜索关键字"),
    limit: int = Query(20, ge=1, le=100, description="返回标签数量"),
    conn = Depends(get_db)
):
    """搜索符合关键字的标签，用于自动完成功能"""
    all_tags = get_all_tags(conn)
    query_lower = query.lower()
    matched_tags = [tag for tag in all_tags if query_lower in tag.lower()]
    limited_tags = matched_tags[:limit]
    
    return ResponseModel.success(
        data=limited_tags,
        message="成功搜索标签",
        metadata={"total": len(matched_tags)}
    )


@router.get("/by-tag/{tag}", response_model=ResponseModel)
async def get_images_by_tag_endpoint(
    tag: str = Path(..., description="标签名称"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    conn = Depends(get_db)
):
    """根据标签获取图片列表"""
    image_ids = get_images_by_tag(conn, tag)
    total = len(image_ids)
    
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    page_image_ids = image_ids[start_idx:end_idx]
    
    images = get_images_by_ids(page_image_ids, conn)
    
    return ResponseModel.paginated_response(
        data=images,
        page=page,
        page_size=page_size,
        total_items=total,
        message=f"成功获取标签 '{tag}' 的图片列表",
        additional_metadata={"tag": tag}
    )


@router.get("/by-multiple-tags", response_model=ResponseModel)
async def get_images_by_multiple_tags(
    tags: str = Query(..., description="多个标签，以逗号分隔"),
    mode: str = Query("or", description="匹配模式：'or'表示匹配任一标签，'and'表示匹配所有标签"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    conn = Depends(get_db)
):
    """根据多个标签获取图片列表"""
    tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
    if not tag_list:
        return ResponseModel.error(
            code="INVALID_TAGS",
            message="请提供有效的标签列表",
            http_code=400
        )
    
    all_matching_ids: Set[int] = set()
    
    for tag in tag_list:
        tag_image_ids = set(get_images_by_tag(conn, tag))
        
        if mode.lower() == "or":
            all_matching_ids.update(tag_image_ids)
        else:
            if not all_matching_ids:
                all_matching_ids = tag_image_ids
            else:
                all_matching_ids.intersection_update(tag_image_ids)
    
    image_ids = list(all_matching_ids)
    total = len(image_ids)
    
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    page_image_ids = image_ids[start_idx:end_idx]
    
    images = get_images_by_ids(page_image_ids, conn)
    
    return ResponseModel.paginated_response(
        data=images,
        page=page,
        page_size=page_size,
        total_items=total,
        message=f"成功获取{'满足所有' if mode.lower() == 'and' else '满足任一'}标签的图片列表",
        additional_metadata={
            "tags": tag_list,
            "mode": mode
        }
    )



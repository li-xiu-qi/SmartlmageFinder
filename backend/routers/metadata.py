from fastapi import APIRouter, Query, Path
from typing import List, Dict, Any
from ..schemas import ResponseModel, MetadataUpdateRequest
from .. import db

router = APIRouter(tags=["metadata"])

@router.get("/metadata/fields", response_model=ResponseModel)
async def get_metadata_fields(limit: int = Query(50, ge=1, le=200, description="返回字段数量")):
    """获取系统中所有已使用的元数据字段及其使用频率"""
    fields = db.get_metadata_fields(limit=limit)
    
    return ResponseModel.success(
        data={"fields": fields},
        metadata={"total": len(fields)}
    )

@router.patch("/images/{uuid}/metadata", response_model=ResponseModel)
async def update_image_metadata(
    metadata_data: MetadataUpdateRequest,
    uuid: str = Path(..., description="图片UUID")
):
    """更新指定图片的元数据"""
    # 更新元数据
    updated_image = db.update_image_metadata(uuid, metadata_data.metadata)
    
    if not updated_image:
        return ResponseModel.error(
            code="NOT_FOUND",
            message="图片不存在"
        )
    
    return ResponseModel.success(
        data={
            "uuid": updated_image["uuid"],
            "updated_at": updated_image["updated_at"]
        }
    )
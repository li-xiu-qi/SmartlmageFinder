from fastapi import APIRouter, Depends, Path, Body
from typing import Dict, Any
from pydantic import BaseModel, Field
import sqlite3
import json # 添加 json 导入

from backend.db_func.core.connection import get_db
from backend.db_func.repositories.images import ImageRepository
from backend.db_func.repositories.metadata import MetadataRepository
from backend.global_schemas import ResponseModel

router = APIRouter(prefix="/api/v1/metadata", tags=["metadata"])

class MetadataUpdateRequest(BaseModel):
    metadata: Dict[str, Any] = Field(..., description="要更新的元数据字典")

@router.put("/{image_id}/update")
async def update_image_metadata_endpoint(
    image_id: int = Path(..., description="图片ID", ge=1),
    payload: MetadataUpdateRequest = Body(..., description="元数据更新请求体"),
    conn: sqlite3.Connection = Depends(get_db)
):
    """
    更新指定图片的元数据。
    元数据将以JSON对象的形式存储。
    """
    # 检查图片是否存在
    image_repo = ImageRepository()
    image = image_repo.get_by_id(image_id)
    if not image:
        return ResponseModel.error(
            code="IMAGE_NOT_FOUND",
            message=f"未找到ID为 {image_id} 的图片",
            http_code=404
        )

    try:
        metadata_repo = MetadataRepository()
        success = metadata_repo.update_metadata(image_id, payload.metadata)
        if success:
            # 成功更新后，获取最新的图片信息（包含更新后的元数据）
            updated_image = image_repo.get_by_id(image_id)
            return ResponseModel.success(
                data=updated_image, # 返回更新后的完整图片信息
                message="元数据更新成功"
            )
        else:
            # 此处假设 update_image_metadata 返回 False 意味着图片未找到或没有实际更新
            # （例如，元数据与现有数据相同，或者 image_id 无效导致 rowcount 为 0）。
            # 根据 update_image_metadata 的具体实现，可能需要调整错误代码和消息。
            return ResponseModel.error(
                code="METADATA_UPDATE_FAILED",
                message=f"更新图片ID {image_id} 的元数据失败，图片可能不存在或数据无变化",
                http_code=400 # 或者 404 如果确定是图片不存在
            )
    except json.JSONEncoderError as je:
        # 特定的JSON编码错误处理
        print(f"更新元数据时发生JSON编码错误: {je}")
        return ResponseModel.error(
            code="JSON_ENCODE_ERROR",
            message=f"元数据格式错误，无法编码为JSON: {str(je)}",
            http_code=400
        )
    except sqlite3.Error as dbe:
        # 特定的数据库错误处理
        print(f"更新元数据时发生数据库错误: {dbe}")
        return ResponseModel.error(
            code="DATABASE_ERROR",
            message=f"更新元数据时发生数据库错误: {str(dbe)}",
            http_code=500
        )
    except Exception as e:
        # 其他所有未预料到的异常
        print(f"更新元数据时发生内部错误: {e}")
        return ResponseModel.error(
            code="INTERNAL_SERVER_ERROR",
            message=f"更新元数据时发生未预料的内部错误: {str(e)}",
            http_code=500
        )

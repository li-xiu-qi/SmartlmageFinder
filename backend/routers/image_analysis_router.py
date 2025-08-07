from fastapi import APIRouter, Path, BackgroundTasks, UploadFile, File, Form, Depends
from typing import List

import time
import os
import shutil
import tempfile

from ..global_schemas import ResponseModel

from ..ai_func.analyze_upload_image import analyze_upload_image
from ..config import settings
from ..ai_func.image_analysis import ImageAnalysis
from ..db_func.core.connection import get_db

# 创建路由器
router = APIRouter(prefix="/api/v1/ai", tags=["ai"])

def get_image_analyzer() -> ImageAnalysis:
    """获取图像分析器实例"""
    return ImageAnalysis()


@router.post("/analyze-upload-image")
async def analyze_uploaded_image(
    file: UploadFile = File(..., description="要分析的图片文件"),
    detail: str = Form("low", description="细节级别: low或high"),
    analyzer: ImageAnalysis = Depends(get_image_analyzer),  # 使用依赖注入
):
    """分析用户上传的图片，生成标题、描述和标签"""
    try:
        if not analyzer:
            return ResponseModel.error(
                code="SERVICE_UNAVAILABLE",
                message="图像分析服务不可用，请确认配置了正确的API密钥",
                http_code=500
            )
          # 调用分析函数
        start_time = time.time()
        analyze_result = analyze_upload_image(
            image_analyzer_instance=analyzer, 
            upload_image=file, 
            detail=detail
        )
        end_time = time.time()
          # 返回结果
        return ResponseModel.success(
            data=analyze_result,
            message="图片分析成功",
            metadata={
                "model": "AI多模态模型",
                "time_ms": int((end_time - start_time) * 1000)
            }
        )
    except Exception as e:
        print("出错了",(e))
        return ResponseModel.error(
            code="AI_PROCESSING_ERROR",
            message=f"AI处理出错: {str(e)}",
            http_code=500
        )

@router.post("/analyze-image-id/{image_id}")
async def analyze_image(image_id: str = Path(..., description="图片的ID"),
                        detail: str = Form("low", description="细节级别: low或high"),
                        analyzer: ImageAnalysis = Depends(get_image_analyzer),  # 使用依赖注入
                        conn = Depends(get_db),  # 使用依赖注入获取数据库连接
                        ):
    """分析图片并生成标题、描述和标签"""
    try:
        if not analyzer:
            return ResponseModel.error(
                code="SERVICE_UNAVAILABLE",
                message="图像分析服务不可用，请确认配置了正确的API密钥",
                http_code=500
            )
          # 调用分析函数
        from ..ai_func.analyze_image_id import analyze_image_id
        
        start_time = time.time()
        analyze_result = analyze_image_id(
            image_analyzer_instance=analyzer,
            image_id=image_id,
            detail=detail,
            conn=conn
        )
        # 注意：使用依赖注入时，FastAPI会自动管理连接的生命周期，不需要手动关闭
        end_time = time.time()
          # 处理可能的错误
        if "error" in analyze_result and analyze_result["error"]:
            return ResponseModel.error(
                code="IMAGE_ANALYSIS_ERROR",
                message=analyze_result["error"],
                http_code=400
            )
        
        # 返回成功结果
        return ResponseModel.success(
            data=analyze_result,
            message="图片分析成功",
            metadata={
                "model": "AI多模态模型",
                "time_ms": int((end_time - start_time) * 1000)
            }
        )
    except Exception as e:
        return ResponseModel.error(
            code="AI_PROCESSING_ERROR",
            message=f"AI处理出错: {str(e)}",
            http_code=500
        )

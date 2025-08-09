from fastapi import APIRouter, Path, BackgroundTasks, UploadFile, File, Form, Depends
from ...global_schemas import ResponseModel  # type: ignore
from ...ai_func.analyze_upload_image import analyze_upload_image  # type: ignore
from ...config import settings  # type: ignore
from ...ai_func.image_analysis import ImageAnalysis  # type: ignore
from ...ai_func.analyze_image_id import analyze_image_id  # type: ignore
from ...db_func.core.connection import get_db  # type: ignore

# 注意：此文件相对于 backend/routers/ai/ 需要使用三点导入到项目根，
# 这里采用运行时包路径，VS Code 可能暂时报红，但执行无碍。

router = APIRouter()

def get_image_analyzer() -> ImageAnalysis:
    return ImageAnalysis()

@router.post("/analyze-upload-image")
async def analyze_uploaded_image(
    file: UploadFile = File(..., description="要分析的图片文件"),
    detail: str = Form("low", description="细节级别: low或high"),
    analyzer: ImageAnalysis = Depends(get_image_analyzer),
):
    try:
        if not analyzer:
            return ResponseModel.error(
                code="SERVICE_UNAVAILABLE",
                message="图像分析服务不可用，请确认配置了正确的API密钥",
                http_code=500
            )
        analyze_result = analyze_upload_image(
            image_analyzer_instance=analyzer,
            upload_image=file,
            detail=detail
        )
        return ResponseModel.success(
            data=analyze_result,
            message="图片分析成功",
            metadata={
                "model": "AI多模态模型"
            }
        )
    except Exception as e:
        return ResponseModel.error(
            code="AI_PROCESSING_ERROR",
            message=f"AI处理出错: {str(e)}",
            http_code=500
        )

@router.post("/analyze-image-id/{image_id}")
async def analyze_image(
    image_id: str = Path(..., description="图片的ID"),
    detail: str = Form("low", description="细节级别: low或high"),
    analyzer: ImageAnalysis = Depends(get_image_analyzer),
    conn = Depends(get_db),
):
    try:
        if not analyzer:
            return ResponseModel.error(
                code="SERVICE_UNAVAILABLE",
                message="图像分析服务不可用，请确认配置了正确的API密钥",
                http_code=500
            )
        analyze_result = analyze_image_id(
            image_analyzer_instance=analyzer,
            image_id=image_id,
            detail=detail,
            conn=conn
        )
        if "error" in analyze_result and analyze_result["error"]:
            return ResponseModel.error(
                code="IMAGE_ANALYSIS_ERROR",
                message=analyze_result["error"],
                http_code=400
            )
        return ResponseModel.success(
            data=analyze_result,
            message="图片分析成功",
            metadata={
                "model": "AI多模态模型"
            }
        )
    except Exception as e:
        return ResponseModel.error(
            code="AI_PROCESSING_ERROR",
            message=f"AI处理出错: {str(e)}",
            http_code=500
        )

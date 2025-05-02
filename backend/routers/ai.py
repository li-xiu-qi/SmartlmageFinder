from fastapi import APIRouter, Query, Path, BackgroundTasks, UploadFile, File, Form, HTTPException
from typing import List, Dict, Any, Optional
from ..schemas import ResponseModel, GenerateRequest, BatchGenerateRequest, GeneratedContent
from .. import db
import uuid as uuid_lib
import time
import os
import tempfile
import shutil

# 导入图像分析和向量生成模块
from ..image_analysis import ImageAnalysis, get_image_hash
from ..config import settings

router = APIRouter(prefix="/ai", tags=["ai"])

# 模拟任务状态存储
tasks = {}

# 检查AI功能是否启用并初始化图像分析器
image_analyzer = None
ai_available = False

if settings.AI_ENABLED:
    try:
        image_analyzer = ImageAnalysis(api_key=os.getenv("OPENAI_API_KEY"))
        ai_available = image_analyzer is not None
        print("AI图像分析服务初始化成功")
    except Exception as e:
        print(f"初始化图像分析器失败: {e}")
else:
    print("AI功能已在配置中禁用，图像分析服务不可用")

@router.post("/generate/{uuid}", response_model=ResponseModel)
async def generate_content(
    generate_options: GenerateRequest,
    uuid: str = Path(..., description="图片UUID")
):
    """使用多模态模型为指定图片生成标题、描述和标签"""
    # 检查图片是否存在
    image = db.get_image_by_uuid(uuid)
    if not image:
        return ResponseModel.error(
            code="NOT_FOUND",
            message="图片不存在"
        )
    
    # 检查图像分析器是否可用
    if not image_analyzer:
        return ResponseModel.error(
            code="SERVICE_UNAVAILABLE",
            message="图像分析服务不可用，请确认配置了正确的API密钥"
        )
    
    # 获取图片文件路径
    image_path = image["filepath"]
    if not os.path.exists(image_path):
        return ResponseModel.error(
            code="FILE_ERROR",
            message="图片文件不存在"
        )
    
    generated = {}
    start_time = time.time()
    
    try:
        # 调用图像分析
        analysis_result = image_analyzer.analyze_image(
            local_image_path=image_path,
            detail="low" if generate_options.detail == "low" else "high"
        )
        
        # 处理生成结果
        if generate_options.generate_title and "title" in analysis_result:
            generated["title"] = analysis_result["title"]
        
        if generate_options.generate_description and "description" in analysis_result:
            generated["description"] = analysis_result["description"]
        
        if generate_options.generate_tags and "tags" in analysis_result:
            generated["tags"] = analysis_result["tags"]
        
        # 如果分析出现错误
        if "error" in analysis_result:
            return ResponseModel.error(
                code="AI_ANALYSIS_ERROR",
                message=analysis_result["error"]
            )
        
        # 应用生成的内容到图片
        update_data = {}
        if "title" in generated and generated["title"]:
            update_data["title"] = generated["title"]
        if "description" in generated and generated["description"]:
            update_data["description"] = generated["description"]
        if "tags" in generated and generated["tags"]:
            update_data["tags"] = generated["tags"]
        
        # 更新图片
        if update_data:
            db.update_image(uuid, update_data)
    
    except Exception as e:
        return ResponseModel.error(
            code="AI_PROCESSING_ERROR",
            message=f"AI处理出错: {str(e)}"
        )
    
    end_time = time.time()
    processing_time = int((end_time - start_time) * 1000)  # 毫秒
    
    return ResponseModel.success(
        data={
            "uuid": uuid,
            "generated": generated,
            "applied": bool(update_data)
        },
        metadata={
            "model": "AI多模态模型",
            "time_ms": processing_time
        }
    )

@router.post("/batch-generate", response_model=ResponseModel)
async def batch_generate(
    batch_request: BatchGenerateRequest,
    background_tasks: BackgroundTasks
):
    """批量为多张图片生成内容"""
    # 检查图像分析器是否可用
    if not image_analyzer:
        return ResponseModel.error(
            code="SERVICE_UNAVAILABLE",
            message="图像分析服务不可用，请确认配置了正确的API密钥"
        )
    
    # 创建任务
    task_id = str(uuid_lib.uuid4())
    
    # 初始化任务状态
    tasks[task_id] = {
        "status": "processing",
        "total": len(batch_request.uuids),
        "processed": 0,
        "succeeded": 0,
        "failed": 0,
        "results": [],
        "start_time": time.time()
    }
    
    # 添加后台任务
    background_tasks.add_task(
        process_batch_generation,
        task_id,
        batch_request.uuids,
        batch_request.options
    )
    
    return ResponseModel.success(
        data={
            "task_id": task_id,
            "total_images": len(batch_request.uuids),
            "status": "processing"
        }
    )

@router.get("/tasks/{task_id}", response_model=ResponseModel)
async def get_task_status(task_id: str = Path(..., description="任务ID")):
    """查询批量生成任务的状态"""
    if task_id not in tasks:
        return ResponseModel.error(
            code="NOT_FOUND",
            message="任务不存在或已过期"
        )
    
    task_info = tasks[task_id]
    
    # 计算元数据
    metadata = {
        "start_time": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(task_info["start_time"]))
    }
    
    if task_info["status"] == "completed":
        end_time = task_info.get("end_time", time.time())
        metadata["end_time"] = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(end_time))
        metadata["duration_ms"] = int((end_time - task_info["start_time"]) * 1000)
    
    return ResponseModel.success(
        data={
            "task_id": task_id,
            "status": task_info["status"],
            "progress": {
                "total": task_info["total"],
                "processed": task_info["processed"],
                "succeeded": task_info["succeeded"],
                "failed": task_info["failed"]
            },
            "results": task_info["results"] if task_info["status"] == "completed" else None
        },
        metadata=metadata
    )

@router.post("/analyze-upload", response_model=ResponseModel)
async def analyze_uploaded_image(
    file: UploadFile = File(..., description="要分析的图片文件"),
    generate_title: bool = Form(True, description="是否生成标题"),
    generate_description: bool = Form(True, description="是否生成描述"),
    generate_tags: bool = Form(True, description="是否生成标签"),
    detail: str = Form("low", description="细节级别: low或high")
):
    """分析用户上传的图片，生成标题、描述和标签"""
    # 检查图像分析器是否可用
    if not image_analyzer:
        return ResponseModel.error(
            code="SERVICE_UNAVAILABLE",
            message="图像分析服务不可用，请确认配置了正确的API密钥"
        )
    
    # 将图片保存到临时文件
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
        shutil.copyfileobj(file.file, temp_file)
        temp_path = temp_file.name
    
    try:
        # 分析图片
        start_time = time.time()
        result = image_analyzer.analyze_image(
            local_image_path=temp_path,
            detail="low" if detail == "low" else "high"
        )
        end_time = time.time()
        
        # 过滤结果
        generated = {}
        if generate_title and "title" in result:
            generated["title"] = result["title"]
        if generate_description and "description" in result:
            generated["description"] = result["description"]
        if generate_tags and "tags" in result:
            generated["tags"] = result["tags"]
        
        # 如果分析出现错误
        if "error" in result:
            return ResponseModel.error(
                code="AI_ANALYSIS_ERROR",
                message=result["error"]
            )
        
        return ResponseModel.success(
            data={
                "generated": generated,
                "filename": file.filename
            },
            metadata={
                "model": "AI多模态模型",
                "time_ms": int((end_time - start_time) * 1000)
            }
        )
    except Exception as e:
        return ResponseModel.error(
            code="AI_PROCESSING_ERROR",
            message=f"AI处理出错: {str(e)}"
        )
    finally:
        # 删除临时文件
        if os.path.exists(temp_path):
            os.unlink(temp_path)

# 批量处理函数
async def process_batch_generation(task_id: str, uuids: List[str], options: GenerateRequest):
    """后台批量生成内容"""
    task = tasks[task_id]
    
    for uuid in uuids:
        # 获取图片
        image = db.get_image_by_uuid(uuid)
        
        if not image:
            task["failed"] += 1
            task["results"].append({
                "uuid": uuid,
                "status": "error",
                "error": "图片不存在"
            })
            task["processed"] += 1
            continue
        
        # 获取图片路径
        image_path = image["filepath"]
        if not os.path.exists(image_path):
            task["failed"] += 1
            task["results"].append({
                "uuid": uuid,
                "status": "error",
                "error": "图片文件不存在"
            })
            task["processed"] += 1
            continue
        
        try:
            # 调用图像分析
            if image_analyzer:
                analysis_result = image_analyzer.analyze_image(
                    local_image_path=image_path,
                    detail="low" if options.detail == "low" else "high"
                )
                
                # 处理生成结果
                update_data = {}
                if options.generate_title and "title" in analysis_result:
                    update_data["title"] = analysis_result["title"]
                
                if options.generate_description and "description" in analysis_result:
                    update_data["description"] = analysis_result["description"]
                
                if options.generate_tags and "tags" in analysis_result:
                    update_data["tags"] = analysis_result["tags"]
                
                # 更新图片
                if update_data and not "error" in analysis_result:
                    db.update_image(uuid, update_data)
                    
                    task["succeeded"] += 1
                    task["results"].append({
                        "uuid": uuid,
                        "status": "success"
                    })
                else:
                    # 处理失败，但可能有部分结果
                    task["failed"] += 1
                    task["results"].append({
                        "uuid": uuid,
                        "status": "error",
                        "error": analysis_result.get("error", "AI分析未返回有效内容")
                    })
            else:
                # 图像分析器不可用
                task["failed"] += 1
                task["results"].append({
                    "uuid": uuid,
                    "status": "error",
                    "error": "图像分析服务不可用"
                })
                
        except Exception as e:
            task["failed"] += 1
            task["results"].append({
                "uuid": uuid,
                "status": "error",
                "error": str(e)
            })
        
        task["processed"] += 1
        # 每处理一个图像暂停一小段时间，避免API速率限制
        time.sleep(0.5)
    
    # 更新任务状态
    task["status"] = "completed"
    task["end_time"] = time.time()

@router.post("/analyze/{uuid}", response_model=ResponseModel)
async def analyze_image(uuid: str = Path(..., description="图片的UUID")):
    """分析图片并生成标题、描述和标签"""
    # 检查AI分析功能是否可用
    if not ai_available:
        return ResponseModel.error(
            code="SERVICE_UNAVAILABLE",
            message="AI分析功能不可用，请检查API密钥配置"
        )
    
    # 获取图片信息
    image = db.get_image_by_uuid(uuid)
    if not image:
        return ResponseModel.error(
            code="NOT_FOUND",
            message="图片不存在"
        )
    
    # 检查图片文件是否存在
    image_path = image["filepath"]
    if not os.path.exists(image_path):
        return ResponseModel.error(
            code="FILE_ERROR",
            message="图片文件不存在"
        )
    
    # 分析图片
    try:
        start_time = time.time()
        
        result = image_analyzer.analyze_image(local_image_path=image_path)
        
        if "error" in result:
            return ResponseModel.error(
                code="ANALYSIS_ERROR",
                message=f"分析图片失败: {result['error']}"
            )
        
        # 更新图片信息
        update_data = {}
        if result.get("title"):
            update_data["title"] = result["title"]
        
        if result.get("description"):
            update_data["description"] = result["description"]
        
        if result.get("tags") and isinstance(result["tags"], list):
            update_data["tags"] = result["tags"]
        
        # 仅在有内容时更新
        if update_data:
            updated_image = db.update_image(uuid, update_data)
            
            end_time = time.time()
            processing_time = int((end_time - start_time) * 1000)  # 毫秒
            
            return ResponseModel.success(
                data={
                    "uuid": uuid,
                    "analysis": result,
                    "updated": True,
                    "image": updated_image
                },
                metadata={
                    "time_ms": processing_time
                }
            )
        else:
            return ResponseModel.error(
                code="EMPTY_RESULT",
                message="AI分析未产生有效结果"
            )
    
    except Exception as e:
        return ResponseModel.error(
            code="PROCESSING_ERROR",
            message=f"处理图片时出错: {str(e)}"
        )

@router.post("/batch-analyze", response_model=ResponseModel)
async def batch_analyze_images(uuids: List[str]):
    """批量分析多张图片"""
    # 检查AI分析功能是否可用
    if not ai_available:
        return ResponseModel.error(
            code="SERVICE_UNAVAILABLE",
            message="AI分析功能不可用，请检查API密钥配置"
        )
    
    if not uuids:
        return ResponseModel.error(
            code="BAD_REQUEST",
            message="UUID列表不能为空"
        )
    
    start_time = time.time()
    
    # 处理结果
    results = []
    failed = []
    
    # 分析每张图片
    for uuid in uuids:
        try:
            # 获取图片信息
            image = db.get_image_by_uuid(uuid)
            if not image:
                failed.append({
                    "uuid": uuid,
                    "error": "图片不存在"
                })
                continue
            
            # 检查图片文件是否存在
            image_path = image["filepath"]
            if not os.path.exists(image_path):
                failed.append({
                    "uuid": uuid,
                    "error": "图片文件不存在"
                })
                continue
            
            # 分析图片
            result = image_analyzer.analyze_image(local_image_path=image_path)
            
            if "error" in result:
                failed.append({
                    "uuid": uuid,
                    "error": f"分析失败: {result['error']}"
                })
                continue
            
            # 更新图片信息
            update_data = {}
            if result.get("title"):
                update_data["title"] = result["title"]
            
            if result.get("description"):
                update_data["description"] = result["description"]
            
            if result.get("tags") and isinstance(result["tags"], list):
                update_data["tags"] = result["tags"]
            
            # 仅在有内容时更新
            if update_data:
                updated_image = db.update_image(uuid, update_data)
                results.append({
                    "uuid": uuid,
                    "analysis": result,
                    "updated": True
                })
            else:
                failed.append({
                    "uuid": uuid,
                    "error": "AI分析未产生有效结果"
                })
        
        except Exception as e:
            failed.append({
                "uuid": uuid,
                "error": f"处理出错: {str(e)}"
            })
    
    end_time = time.time()
    total_time = int((end_time - start_time) * 1000)  # 毫秒
    
    return ResponseModel.success(
        data={
            "success": results,
            "failed": failed,
            "total": len(uuids),
            "success_count": len(results),
            "failed_count": len(failed)
        },
        metadata={
            "total_time_ms": total_time,
            "avg_time_ms": int(total_time / len(uuids)) if uuids else 0
        }
    )
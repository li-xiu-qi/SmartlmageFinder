from fastapi import APIRouter, HTTPException, Query, Path, UploadFile, File, Form
from typing import List, Optional, Dict, Any
from ..schemas import ResponseModel, TextSearchQuery
import os
import shutil
from datetime import datetime
import json
from PIL import Image as PILImage
from .. import db
from .. import vector_db
import tempfile
import time
import numpy as np

# 导入向量生成相关功能
from ..generate_vector import get_model, encode_text, encode_image
from ..image_analysis import get_image_hash
from ..config import settings

router = APIRouter(prefix="/search", tags=["search"])

# 检查AI功能是否启用并验证模型是否可加载
vector_search_available = False
if settings.AI_ENABLED:
    try:
        model = get_model()
        vector_search_available = True
        print("向量搜索模型加载成功")
    except Exception as e:
        vector_search_available = False
        print(f"向量搜索模型加载失败: {e}")
else:
    print("AI功能已在配置中禁用，向量搜索不可用")

@router.get("/text", response_model=ResponseModel)
async def text_search(
    q: str = Query(..., description="搜索查询文本"),
    mode: str = Query("hybrid", description="搜索模式: vector、text或hybrid"),
    vector_type: str = Query("mixed", description="向量类型: title、description或mixed"),
    limit: int = Query(20, ge=1, le=1000, description="返回结果数量"),
    start_date: Optional[str] = Query(None, description="开始日期过滤"),
    end_date: Optional[str] = Query(None, description="结束日期过滤"),
    tags: Optional[str] = Query(None, description="标签过滤，逗号分隔")
):
    """使用文本查询相似图片"""
    # 处理标签过滤
    tag_list = None
    if tags:
        tag_list = [tag.strip() for tag in tags.split(",")]
    
    start_time = time.time()
    
    # 根据模式执行搜索
    if mode == "text" or (mode == "vector" and not vector_search_available) or (mode == "hybrid" and not vector_search_available):
        # 使用纯文本搜索
        results = db.search_by_text(
            query=q,
            mode="text",
            limit=limit,
            start_date=start_date,
            end_date=end_date,
            tags=tag_list
        )
    elif mode == "vector" and vector_search_available:
        # 使用纯向量搜索
        # 根据向量类型选择不同的搜索方法
        if vector_type == "title":
            vector_results = vector_db.search_by_title(q, limit=limit*2)
        elif vector_type == "description":
            vector_results = vector_db.search_by_description(q, limit=limit*2)
        else:  # mixed - 默认或不识别的类型
            vector_results = vector_db.search_by_text(q, limit=limit*2)
            
        # 获取向量搜索结果的详细信息并应用过滤
        results = []
        for vec_result in vector_results:
            # 获取图片详细信息
            img = db.get_image_by_uuid(vec_result["uuid"])
            if img:
                # 应用过滤条件
                include = True
                # 日期过滤
                if start_date and img["created_at"] < start_date:
                    include = False
                if end_date and img["created_at"] > end_date:
                    include = False
                # 标签过滤
                if tag_list and not any(tag in img["tags"] for tag in tag_list):
                    include = False
                    
                if include:
                    # 添加相似度得分
                    img["score"] = float(vec_result["similarity"])
                    results.append(img)
        
        # 限制结果数量
        results = results[:limit]
    else:  # hybrid模式，结合文本和向量搜索
        # 获取文本搜索结果
        text_results = db.search_by_text(
            query=q,
            mode="text",
            limit=limit*2,
            start_date=start_date,
            end_date=end_date,
            tags=tag_list
        )
        
        # 如果向量搜索可用，获取向量搜索结果
        vector_results = []
        if vector_search_available:
            # 根据向量类型选择不同的搜索方法
            if vector_type == "title":
                vector_results = vector_db.search_by_title(q, limit=limit*2)
            elif vector_type == "description":
                vector_results = vector_db.search_by_description(q, limit=limit*2)
            else:  # mixed - 默认或不识别的类型
                vector_results = vector_db.search_by_text(q, limit=limit*2)
        
        # 合并结果，使用两种搜索的得分
        all_results = {}
        
        # 添加文本搜索结果
        for result in text_results:
            uuid = result["uuid"]
            all_results[uuid] = result
            # 文本搜索得分权重为0.4
            all_results[uuid]["score"] = result["score"] * 0.4
        
        # 添加向量搜索结果
        for result in vector_results:
            uuid = result["uuid"]
            if uuid in all_results:
                # 如果已存在，结合向量搜索相似度（权重0.6）
                all_results[uuid]["score"] += float(result["similarity"]) * 0.6
            else:
                # 如果尚不存在，获取图片信息并添加
                img = db.get_image_by_uuid(uuid)
                if img:
                    # 应用过滤条件
                    include = True
                    # 日期过滤
                    if start_date and img["created_at"] < start_date:
                        include = False
                    if end_date and img["created_at"] > end_date:
                        include = False
                    # 标签过滤
                    if tag_list and not any(tag in img["tags"] for tag in tag_list):
                        include = False
                        
                    if include:
                        # 只有向量得分，权重为0.6
                        img["score"] = float(result["similarity"]) * 0.6
                        all_results[uuid] = img
        
        # 转换为列表并按混合分数排序
        results = list(all_results.values())
        results.sort(key=lambda x: x["score"], reverse=True)
        # 限制结果数量
        results = results[:limit]
    
    # 计算处理时间
    end_time = time.time()
    processing_time = int((end_time - start_time) * 1000)  # 毫秒
    
    # 格式化结果
    formatted_results = []
    for result in results:
        formatted_results.append({
            "uuid": result["uuid"],
            "title": result["title"],
            "description": result.get("description", ""),
            "filepath": result["filepath"],
            "score": float(result["score"]),  # 确保score是浮点数
            "tags": result["tags"]
        })
    
    return ResponseModel.success(
        data={"results": formatted_results},
        metadata={
            "query": q,
            "mode": mode,
            "vector_type": vector_type,
            "total": len(formatted_results),
            "time_ms": processing_time
        }
    )

@router.post("/image", response_model=ResponseModel)
async def image_search(
    image: UploadFile = File(..., description="要搜索的参考图片文件"),
    limit: int = Query(20, ge=1, le=100, description="返回结果数量"),
    start_date: Optional[str] = Query(None, description="开始日期过滤"),
    end_date: Optional[str] = Query(None, description="结束日期过滤"),
    tags: Optional[str] = Query(None, description="标签过滤，逗号分隔")
):
    """上传图片搜索相似图片"""
    # 检查向量搜索是否可用
    if not vector_search_available:
        return ResponseModel.error(
            code="SERVICE_UNAVAILABLE",
            message="向量搜索功能不可用，请检查模型配置"
        )
    
    # 检查文件是否有效
    if not image or not image.filename:
        return ResponseModel.error(
            code="INVALID_FILE",
            message="未收到有效的图片文件"
        )
    
    # 处理标签过滤
    tag_list = None
    if tags:
        tag_list = [tag.strip() for tag in tags.split(",")]
    
    temp_path = None
    try:
        # 创建临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
            temp_path = temp_file.name
            # 复制上传的文件内容
            contents = await image.read()
            temp_file.write(contents)
            await image.seek(0)  # 重置文件指针，以防后续需要再次读取
        
        start_time = time.time()
        
        # 使用向量索引进行图像搜索
        vector_results = vector_db.search_by_image(temp_path, limit=limit*2)
            
        # 获取向量搜索结果的详细信息并应用过滤
        results = []
        for vec_result in vector_results:
            # 获取图片详细信息
            img = db.get_image_by_uuid(vec_result["uuid"])
            if img:
                # 应用过滤条件
                include = True
                # 日期过滤
                if start_date and img["created_at"] < start_date:
                    include = False
                if end_date and img["created_at"] > end_date:
                    include = False
                # 标签过滤
                if tag_list and not any(tag in img["tags"] for tag in tag_list):
                    include = False
                    
                if include:
                    # 添加相似度得分
                    img["score"] = float(vec_result["similarity"])
                    results.append(img)
        
        # 限制结果数量
        results = results[:limit]
        
        # 格式化结果
        formatted_results = []
        for result in results:
            formatted_results.append({
                "uuid": result["uuid"],
                "title": result["title"],
                "description": result.get("description", ""),
                "filepath": result["filepath"],
                "score": float(result["score"]),  # 确保score是浮点数
                "tags": result["tags"]
            })
        
        end_time = time.time()
        processing_time = int((end_time - start_time) * 1000)  # 毫秒
        
        return ResponseModel.success(
            data={"results": formatted_results},
            metadata={
                "mode": "vector",
                "total": len(formatted_results),
                "time_ms": processing_time
            }
        )
            
    except Exception as e:
        print(f"图片搜索处理出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return ResponseModel.error(
            code="PROCESSING_ERROR",
            message=f"图片处理出错: {str(e)}"
        )
    finally:
        # 删除临时文件
        if temp_path and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except Exception as e:
                print(f"删除临时文件失败: {str(e)}")

@router.get("/similar/{uuid}", response_model=ResponseModel)
async def similar_image_search(
    uuid: str = Path(..., description="参考图片的UUID"),
    limit: int = Query(20, ge=1, le=100, description="返回结果数量"),
    start_date: Optional[str] = Query(None, description="开始日期过滤"),
    end_date: Optional[str] = Query(None, description="结束日期过滤"),
    tags: Optional[str] = Query(None, description="标签过滤，逗号分隔"),
    search_type: str = Query("image", description="搜索类型: title、description或image")
):
    """根据系统中已存在的图片UUID搜索相似图片"""
    # 检查向量搜索是否可用
    if not vector_search_available:
        return ResponseModel.error(
            code="SERVICE_UNAVAILABLE",
            message="向量搜索功能不可用，请检查模型配置"
        )
    
    # 检查图片是否存在
    image = db.get_image_by_uuid(uuid)
    if not image:
        return ResponseModel.error(
            code="NOT_FOUND",
            message="参考图片不存在"
        )
    
    # 处理标签过滤
    tag_list = None
    if tags:
        tag_list = [tag.strip() for tag in tags.split(",")]
    
    start_time = time.time()
    
    try:
        # 使用向量索引搜索相似内容
        vector_results = vector_db.search_by_uuid(uuid, limit=limit*2, search_type=search_type)
        
        if not vector_results:
            return ResponseModel.error(
                code="NO_VECTOR",
                message=f"未找到图片{search_type}向量索引，请先建立索引"
            )
        
        # 获取向量搜索结果的详细信息并应用过滤
        results = []
        for vec_result in vector_results:
            # 获取图片详细信息
            img = db.get_image_by_uuid(vec_result["uuid"])
            if img:
                # 应用过滤条件
                include = True
                # 日期过滤
                if start_date and img["created_at"] < start_date:
                    include = False
                if end_date and img["created_at"] > end_date:
                    include = False
                # 标签过滤
                if tag_list and not any(tag in img["tags"] for tag in tag_list):
                    include = False
                    
                if include:
                    # 添加相似度得分
                    img["score"] = float(vec_result["similarity"])
                    results.append(img)
        
        # 格式化结果
        formatted_results = []
        for result in results:
            formatted_results.append({
                "uuid": result["uuid"],
                "title": result["title"],
                "description": result.get("description", ""),
                "filepath": result["filepath"],
                "score": float(result["score"]),
                "tags": result["tags"]
            })
        
        # 限制结果数量
        formatted_results = formatted_results[:limit]
        
        end_time = time.time()
        processing_time = int((end_time - start_time) * 1000)  # 毫秒
        
        return ResponseModel.success(
            data={"results": formatted_results},
            metadata={
                "reference_uuid": uuid,
                "search_type": search_type,
                "total": len(formatted_results),
                "time_ms": processing_time
            }
        )
            
    except Exception as e:
        return ResponseModel.error(
            code="SYSTEM_ERROR",
            message=f"系统错误: {str(e)}"
        )
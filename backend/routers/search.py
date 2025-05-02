from fastapi import APIRouter, HTTPException, Query, Path, UploadFile, File, Form
from typing import List, Optional, Dict, Any
from ..schemas import ResponseModel, TextSearchQuery
import os
import shutil
from datetime import datetime
import json
from PIL import Image as PILImage
from .. import db
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
    limit: int = Query(20, ge=1, le=100, description="返回结果数量"),
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
        # 使用纯向量搜索 (暂未实现，后续版本添加)
        # 先通过文本搜索获取结果
        results = db.search_by_text(
            query=q,
            mode="text",
            limit=limit*2,  # 获取更多结果以便后续排序
            start_date=start_date,
            end_date=end_date,
            tags=tag_list
        )
        
        # 获取查询文本的向量表示
        try:
            query_vector = encode_text(q)
            
            # 为结果图片生成向量并计算相似度
            # 注：实际实现应该在数据库中存储向量，这里仅作为示例
            for result in results:
                # 在实际实现中，这些向量应从数据库获取而不是即时计算
                if result['title']:
                    # 简单计算基于标题的相似度
                    title_vector = encode_text(result['title'])
                    # 计算余弦相似度
                    similarity = np.dot(query_vector, title_vector) / (np.linalg.norm(query_vector) * np.linalg.norm(title_vector))
                    result['score'] = max(similarity, result['score'])
            
            # 按相似度排序
            results.sort(key=lambda x: x['score'], reverse=True)
            # 限制结果数量
            results = results[:limit]
            
        except Exception as e:
            print(f"向量搜索出错: {e}")
            # 如果向量搜索失败，回退到文本搜索
            pass
    else:  # hybrid模式，结合文本和向量搜索
        # 先获取所有匹配的结果
        results = db.search_by_text(
            query=q,
            mode="text",
            limit=limit*2,
            start_date=start_date,
            end_date=end_date,
            tags=tag_list
        )
        
        # 如果向量搜索可用，使用向量相似度重新排序
        if vector_search_available and results:
            try:
                query_vector = encode_text(q)
                
                # 计算向量相似度
                for result in results:
                    if result['title']:
                        title_vector = encode_text(result['title'])
                        # 计算余弦相似度
                        similarity = np.dot(query_vector, title_vector) / (np.linalg.norm(query_vector) * np.linalg.norm(title_vector))
                        # 混合分数：文本匹配分数 * 0.4 + 向量相似度 * 0.6
                        result['score'] = result['score'] * 0.4 + similarity * 0.6
                
                # 按混合分数排序
                results.sort(key=lambda x: x['score'], reverse=True)
                # 限制结果数量
                results = results[:limit]
                
            except Exception as e:
                print(f"混合搜索出错: {e}")
                # 如果混合搜索失败，保持文本搜索结果
                pass
    
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
    
    # 处理标签过滤
    tag_list = None
    if tags:
        tag_list = [tag.strip() for tag in tags.split(",")]
    
    # 将上传的图片保存到临时文件
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
        shutil.copyfileobj(image.file, temp_file)
        temp_path = temp_file.name
    
    try:
        start_time = time.time()
        
        # 获取所有图片
        # 注意：在实际实现中，应该预先存储所有图片的向量，并使用高效的向量检索
        images, _ = db.get_images(page=1, page_size=500)  # 获取一批图片进行搜索
        
        # 加载查询图像并计算其向量
        try:
            query_img = PILImage.open(temp_path)
            query_vector = encode_image(query_img)
            
            # 计算每张图片与查询图片的相似度
            results = []
            for img in images:
                try:
                    # 在实际实现中，这些向量应从数据库获取而不是即时计算
                    img_path = img["filepath"]
                    if os.path.exists(img_path):
                        db_img = PILImage.open(img_path)
                        img_vector = encode_image(db_img)
                        
                        # 计算余弦相似度
                        similarity = np.dot(query_vector, img_vector) / (np.linalg.norm(query_vector) * np.linalg.norm(img_vector))
                        
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
                            results.append({
                                "uuid": img["uuid"],
                                "title": img["title"],
                                "description": img.get("description", ""),
                                "filepath": img["filepath"],
                                "score": float(similarity),
                                "tags": img["tags"]
                            })
                except Exception as e:
                    print(f"处理图片 {img['uuid']} 出错: {e}")
                    continue
            
            # 按相似度排序
            results.sort(key=lambda x: x['score'], reverse=True)
            # 限制结果数量
            results = results[:limit]
            
            end_time = time.time()
            processing_time = int((end_time - start_time) * 1000)  # 毫秒
            
            return ResponseModel.success(
                data={"results": results},
                metadata={
                    "mode": "vector",
                    "total": len(results),
                    "time_ms": processing_time
                }
            )
            
        except Exception as e:
            return ResponseModel.error(
                code="PROCESSING_ERROR",
                message=f"图片处理出错: {str(e)}"
            )
    finally:
        # 删除临时文件
        if os.path.exists(temp_path):
            os.unlink(temp_path)

@router.get("/similar/{uuid}", response_model=ResponseModel)
async def similar_image_search(
    uuid: str = Path(..., description="参考图片的UUID"),
    limit: int = Query(20, ge=1, le=100, description="返回结果数量"),
    start_date: Optional[str] = Query(None, description="开始日期过滤"),
    end_date: Optional[str] = Query(None, description="结束日期过滤"),
    tags: Optional[str] = Query(None, description="标签过滤，逗号分隔")
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
    
    # 获取参考图片路径
    ref_image_path = image["filepath"]
    if not os.path.exists(ref_image_path):
        return ResponseModel.error(
            code="FILE_ERROR",
            message="参考图片文件不存在"
        )
    
    try:
        # 获取所有图片
        images, _ = db.get_images(page=1, page_size=500)  # 获取一批图片进行搜索
        
        # 加载参考图像并计算其向量
        try:
            ref_img = PILImage.open(ref_image_path)
            ref_vector = encode_image(ref_img)
            
            # 计算每张图片与参考图片的相似度
            results = []
            for img in images:
                # 跳过参考图片自身
                if img["uuid"] == uuid:
                    continue
                    
                try:
                    img_path = img["filepath"]
                    if os.path.exists(img_path):
                        db_img = PILImage.open(img_path)
                        img_vector = encode_image(db_img)
                        
                        # 计算余弦相似度
                        similarity = np.dot(ref_vector, img_vector) / (np.linalg.norm(ref_vector) * np.linalg.norm(img_vector))
                        
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
                            results.append({
                                "uuid": img["uuid"],
                                "title": img["title"],
                                "description": img.get("description", ""),
                                "filepath": img["filepath"],
                                "score": float(similarity),
                                "tags": img["tags"]
                            })
                except Exception as e:
                    print(f"处理图片 {img['uuid']} 出错: {e}")
                    continue
            
            # 按相似度排序
            results.sort(key=lambda x: x['score'], reverse=True)
            # 限制结果数量
            results = results[:limit]
            
            end_time = time.time()
            processing_time = int((end_time - start_time) * 1000)  # 毫秒
            
            return ResponseModel.success(
                data={"results": results},
                metadata={
                    "reference_uuid": uuid,
                    "mode": "vector",
                    "total": len(results),
                    "time_ms": processing_time
                }
            )
            
        except Exception as e:
            return ResponseModel.error(
                code="PROCESSING_ERROR",
                message=f"图片处理出错: {str(e)}"
            )
    except Exception as e:
        return ResponseModel.error(
            code="SYSTEM_ERROR",
            message=f"系统错误: {str(e)}"
        )
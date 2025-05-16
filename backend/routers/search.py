from fastapi import APIRouter, HTTPException, Query, Path, UploadFile, File, Form, Body, Depends
from typing import List, Optional, Dict, Any, Union, TypeVar, Generic, Callable, Literal

from backend import db_func
import os
import sqlite3
import shutil
from datetime import datetime
import json
from PIL import Image as PILImage
import tempfile
import time
import numpy as np
import functools
from contextlib import contextmanager

# 导入向量生成相关功能
from ..utils.generate_vector import model, encode_image, encode_text
# 导入数据库连接函数
from ..db_func.core import get_db



router = APIRouter(prefix="/search", tags=["search"])

@router.get("/text")
async def text_search(
    q: str = Query(..., description="搜索文本"),
    search_type: Literal["title", "description", "both", "vector", "hybrid"] = Query("both", description="搜索类型：title-仅标题文本匹配，description-仅描述文本匹配，both-标题和描述文本匹配，vector-向量搜索，hybrid-混合搜索"),
    vector_targets: List[str] = Query(["title", "description"], description="向量搜索目标，仅在search_type为vector或hybrid时有效"),
    filename: Optional[str] = Query(None, description="按文件名过滤"),
    tags: Optional[List[str]] = Query(None, description="按标签过滤"),
    start_date: Optional[str] = Query(None, description="开始日期 (YYYY-MM-DD HH:MM:SS)"),
    end_date: Optional[str] = Query(None, description="结束日期 (YYYY-MM-DD HH:MM:SS)"), 
    limit: int = Query(20, description="返回结果数量限制"),
    offset: int = Query(0, description="分页偏移"),
    conn = Depends(get_db)
):
    """
    文本搜索API，支持多种搜索类型:
    - 文本匹配搜索（title、description或both）
    - 向量搜索（vector）
    - 混合搜索（hybrid）
    """
    # 构建过滤条件
    filters = {}
    if filename:
        filters["filename"] = filename
    if tags:
        filters["tags"] = tags
    if start_date:
        filters["start_date"] = start_date  
    if end_date:
        filters["end_date"] = end_date
    
    try:
        if search_type in ["title", "description", "both"]:
            # 使用文本匹配搜索
            return db_func.search_by_text(
                text=q,
                search_type=search_type,
                filters=filters,
                limit=limit,
                offset=offset
            )
        elif search_type == "vector":
            # 使用向量搜索
            from ..db_func.search_func.hybrid_search import hybrid_search
            
            return hybrid_search(
                conn=conn,
                query=q,
                query_type="text",
                search_targets=vector_targets,
                filters=filters,
                limit=limit,
                offset=offset
            )
        elif search_type == "hybrid":
            # 使用混合搜索
            from ..db_func.search_func.hybrid_search import hybrid_search
            
            return hybrid_search(
                conn=conn,
                query=q,
                query_type="text",
                search_targets=vector_targets,
                filters=filters,
                limit=limit,
                offset=offset
            )
        else:
            raise HTTPException(status_code=400, detail=f"不支持的搜索类型: {search_type}")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")

@router.post("/image")
async def image_search(
    file: UploadFile = File(..., description="上传的图像文件"),
    search_targets: List[str] = Form(["image"], description="搜索目标类型，可选：image-图像向量，title-标题向量，description-描述向量"),
    search_type: Literal["vector", "hybrid"] = Form("vector", description="搜索类型：vector-向量搜索，hybrid-混合搜索"),
    filename: Optional[str] = Form(None, description="按文件名过滤"),
    tags: Optional[List[str]] = Form(None, description="按标签过滤"),
    start_date: Optional[str] = Form(None, description="开始日期 (YYYY-MM-DD HH:MM:SS)"),
    end_date: Optional[str] = Form(None, description="结束日期 (YYYY-MM-DD HH:MM:SS)"),
    limit: int = Form(20, description="返回结果数量限制"),
    offset: int = Form(0, description="分页偏移"),
    conn = Depends(get_db)
):
    """
    使用图像搜索相似图片，支持纯向量搜索和混合搜索
    """
    try:
        # 构建过滤条件
        filters = {}
        if filename:
            filters["filename"] = filename
        if tags:
            filters["tags"] = tags
        if start_date:
            filters["start_date"] = start_date
        if end_date:
            filters["end_date"] = end_date
            
        # 创建临时文件保存上传的图片
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        temp_file_path = temp_file.name
        temp_file.close()
        
        try:
            # 保存上传的图像文件
            with open(temp_file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
              # 使用PIL打开图像以确保它是有效的图像
            img = PILImage.open(temp_file_path)
            # 获取图像的向量表示
            image_embedding = encode_image(temp_file_path)
            
            if search_type == "vector":
                from ..db_func.search_func.vector_search import find_similar_images
                
                results = []
                # 对每个搜索目标执行向量搜索
                for target in search_targets:
                    target_results = find_similar_images(
                        conn=conn,
                        query_embedding=image_embedding.tolist(),
                        vector_type=target,
                        k=limit,
                        filters=filters
                    )
                    results.extend(target_results)
                
                # 按相似度排序并去重
                unique_results = {}
                for item in results:
                    if item["id"] not in unique_results or item["distance"] < unique_results[item["id"]]["distance"]:
                        unique_results[item["id"]] = item
                
                # 转换为列表并排序
                sorted_results = sorted(unique_results.values(), key=lambda x: x["distance"])
                
                # 应用分页
                return sorted_results[offset:offset+limit]
            elif search_type == "hybrid":
                from ..db_func.search_func.hybrid_search import hybrid_search
                
                return hybrid_search(
                    conn=conn,
                    query=temp_file_path,
                    query_type="image",
                    search_targets=search_targets,
                    filters=filters,
                    limit=limit,
                    offset=offset
                )
            else:
                raise HTTPException(status_code=400, detail=f"不支持的搜索类型: {search_type}")
                
        finally:
            # 清理临时文件
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"图像搜索失败: {str(e)}")

@router.get("/similar/{image_id}")
async def similar_image_search(
    image_id: int = Path(..., description="图像ID"),
    search_targets: List[str] = Query(["image"], description="搜索目标类型，可选：image-图像向量，title-标题向量，description-描述向量"),
    search_type: Literal["vector", "hybrid"] = Query("vector", description="搜索类型：vector-向量搜索，hybrid-混合搜索"), 
    filename: Optional[str] = Query(None, description="按文件名过滤"),
    tags: Optional[List[str]] = Query(None, description="按标签过滤"),
    start_date: Optional[str] = Query(None, description="开始日期 (YYYY-MM-DD HH:MM:SS)"),
    end_date: Optional[str] = Query(None, description="结束日期 (YYYY-MM-DD HH:MM:SS)"),
    limit: int = Query(20, description="返回结果数量限制"),
    offset: int = Query(0, description="分页偏移"),
    conn = Depends(get_db)
):
    """
    根据已有图像ID查找相似图像，支持向量搜索和混合搜索
    """
    try:
        # 构建过滤条件
        filters = {}
        if filename:
            filters["filename"] = filename
        if tags:
            filters["tags"] = tags
        if start_date:
            filters["start_date"] = start_date
        if end_date:
            filters["end_date"] = end_date
            
        # 首先获取指定ID的图像信息
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM images WHERE id = ?", (image_id,))
        image = cursor.fetchone()
        
        if not image:
            raise HTTPException(status_code=404, detail=f"未找到ID为{image_id}的图像")
        
        # 对于向量搜索，需要从向量表获取对应的向量
        if search_type == "vector":
            from ..db_func.search_func.vector_search import find_similar_images
            
            results = []
            for target in search_targets:
                # 检索目标向量
                vector_table = f"{target}_vectors"
                cursor.execute(
                    f"SELECT embedding FROM {vector_table} WHERE image_id = ?", 
                    (image_id,)
                )
                vector_row = cursor.fetchone()
                
                if not vector_row:
                    continue  # 如果没有找到向量，跳过这个目标
                
                # 将向量字符串转为列表
                embedding = json.loads(vector_row["embedding"])
                
                # 执行相似搜索
                target_results = find_similar_images(
                    conn=conn,
                    query_embedding=embedding,
                    vector_type=target,
                    k=limit,
                    filters=filters
                )
                results.extend(target_results)
            
            # 按相似度排序并去重
            # 同时去除查询图像本身
            unique_results = {}
            for item in results:
                if item["id"] == image_id:
                    continue  # 跳过查询图像本身
                if item["id"] not in unique_results or item["distance"] < unique_results[item["id"]]["distance"]:
                    unique_results[item["id"]] = item
            
            # 转换为列表并排序
            sorted_results = sorted(unique_results.values(), key=lambda x: x["distance"])
            
            # 应用分页
            return sorted_results[offset:offset+limit]
            
        elif search_type == "hybrid":
            from ..db_func.search_func.hybrid_search import hybrid_search
            
            # 对于混合搜索，我们可以直接用图像ID作为查询参数
            return hybrid_search(
                conn=conn,
                query=image_id,  # 直接传递图像ID
                query_type="image_id",  # 指定查询类型为图像ID
                search_targets=search_targets,
                filters=filters,
                limit=limit,
                offset=offset,
                exclude_self=True  # 排除查询图像本身
            )
        else:
            raise HTTPException(status_code=400, detail=f"不支持的搜索类型: {search_type}")
                
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"数据库错误: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"相似图像搜索失败: {str(e)}")

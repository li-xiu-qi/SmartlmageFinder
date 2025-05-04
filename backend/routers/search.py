from fastapi import APIRouter, HTTPException, Query, Path, UploadFile, File, Form, Body
from typing import List, Optional, Dict, Any, Union
from ..schemas import ResponseModel, TextSearchQuery, SearchType, TextMatchMode, VectorMatchMode, ImageVectorMatchMode
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
    search_type: SearchType = Query(SearchType.HYBRID, description="搜索类型: text(传统文本匹配)、vector(向量搜索)或hybrid(混合搜索)"),
    text_match_mode: TextMatchMode = Query(TextMatchMode.COMBINED, description="文本匹配模式: title(标题)、description(描述)或combined(标题+描述)"),
    vector_match_mode: VectorMatchMode = Query(VectorMatchMode.COMBINED, description="向量匹配模式: title(标题向量)、description(描述向量)或combined(标题+描述向量)"),
    limit: int = Query(20, ge=1, le=1000, description="返回结果数量"),
    start_date: Optional[str] = Query(None, description="开始日期过滤"),
    end_date: Optional[str] = Query(None, description="结束日期过滤"),
    tags: Optional[str] = Query(None, description="标签过滤，逗号分隔")
):
    """
    使用文本查询相似图片
    
    - 当search_type=text时: 使用传统文本匹配，根据text_match_mode匹配标题、描述或两者
    - 当search_type=vector时: 使用向量搜索，根据vector_match_mode匹配标题向量、描述向量或两者
    - 当search_type=hybrid时: 结合传统文本匹配和向量搜索
    """
    # 处理标签过滤
    tag_list = None
    if tags:
        tag_list = [tag.strip() for tag in tags.split(",")]
    
    start_time = time.time()
    results = []
    
    # 1. 非向量检索部分 (传统文本匹配)
    if search_type == SearchType.TEXT or (search_type != SearchType.TEXT and not vector_search_available):
        # 使用纯文本搜索
        text_results = []
        
        # 根据文本匹配模式执行不同的搜索
        if text_match_mode == TextMatchMode.TITLE:
            # 仅匹配标题
            text_results = db.search_by_text(
                query=q,
                mode="title_only",  # 需要在db.py中实现此模式
                limit=limit,
                start_date=start_date,
                end_date=end_date,
                tags=tag_list
            )
        elif text_match_mode == TextMatchMode.DESCRIPTION:
            # 仅匹配描述
            text_results = db.search_by_text(
                query=q,
                mode="description_only",  # 需要在db.py中实现此模式
                limit=limit,
                start_date=start_date,
                end_date=end_date,
                tags=tag_list
            )
        else:  # 默认为COMBINED
            # 匹配标题和描述
            text_results = db.search_by_text(
                query=q,
                mode="text",  # 传统模式
                limit=limit,
                start_date=start_date,
                end_date=end_date,
                tags=tag_list
            )
        
        results = text_results
    
    # 2. 向量检索部分
    elif search_type == SearchType.VECTOR and vector_search_available:
        vector_results = []
        
        # 根据向量匹配模式执行不同的搜索
        if vector_match_mode == VectorMatchMode.TITLE:
            # 仅使用标题向量
            vector_results = vector_db.search_by_title(q, limit=limit*2)
        elif vector_match_mode == VectorMatchMode.DESCRIPTION:
            # 仅使用描述向量
            vector_results = vector_db.search_by_description(q, limit=limit*2)
        else:  # 默认为COMBINED
            # 使用混合向量搜索 (标题+描述)
            vector_results = vector_db.search_by_text(q, limit=limit*2)
        
        # 获取向量搜索结果的详细信息并应用过滤
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
        
    # 3. 混合检索部分
    else:  # hybrid模式，结合文本和向量搜索
        # 获取文本搜索结果
        text_results = []
        
        # 根据文本匹配模式执行不同的搜索
        if text_match_mode == TextMatchMode.TITLE:
            # 仅匹配标题
            text_results = db.search_by_text(
                query=q,
                mode="title_only",
                limit=limit*2,
                start_date=start_date,
                end_date=end_date,
                tags=tag_list
            )
        elif text_match_mode == TextMatchMode.DESCRIPTION:
            # 仅匹配描述
            text_results = db.search_by_text(
                query=q,
                mode="description_only",
                limit=limit*2,
                start_date=start_date,
                end_date=end_date,
                tags=tag_list
            )
        else:  # 默认为COMBINED
            # 匹配标题和描述
            text_results = db.search_by_text(
                query=q,
                mode="text",
                limit=limit*2,
                start_date=start_date,
                end_date=end_date,
                tags=tag_list
            )
        
        # 获取向量搜索结果
        vector_results = []
        if vector_search_available:
            # 根据向量匹配模式执行不同的搜索
            if vector_match_mode == VectorMatchMode.TITLE:
                # 仅使用标题向量
                vector_results = vector_db.search_by_title(q, limit=limit*2)
            elif vector_match_mode == VectorMatchMode.DESCRIPTION:
                # 仅使用描述向量
                vector_results = vector_db.search_by_description(q, limit=limit*2)
            else:  # 默认为COMBINED
                # 使用混合向量搜索
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
    
    # 结果排序和限制数量
    results.sort(key=lambda x: x.get("score", 0), reverse=True)
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
            "score": float(result.get("score", 0.0)),  # 确保score是浮点数
            "tags": result["tags"]
        })
    
    return ResponseModel.success(
        data={"results": formatted_results},
        metadata={
            "query": q,
            "search_type": search_type,
            "text_match_mode": text_match_mode,
            "vector_match_mode": vector_match_mode,
            "total": len(formatted_results),
            "time_ms": processing_time
        }
    )

@router.post("/image", response_model=ResponseModel)
async def image_search(
    image: UploadFile = File(..., description="要搜索的参考图片文件"),
    search_type: VectorMatchMode = Form(VectorMatchMode.IMAGE, description="搜索类型: image(图像向量)、title(标题向量)、description(描述向量)或combined(综合)"),
    match_modes: List[ImageVectorMatchMode] = Form([ImageVectorMatchMode.IMAGE], description="匹配模式: image(图像), title(标题), description(描述), combined(综合)"),
    weights: Optional[str] = Form(None, description="各个匹配模式的权重，格式为逗号分隔的浮点数，与match_modes对应"),
    limit: int = Form(20, ge=1, le=100, description="返回结果数量"),
    start_date: Optional[str] = Form(None, description="开始日期过滤"),
    end_date: Optional[str] = Form(None, description="结束日期过滤"),
    tags: Optional[str] = Form(None, description="标签过滤，逗号分隔")
):
    """
    上传图片搜索相似图片
    
    支持多种搜索模式:
    - 图片向量对图片向量
    - 图片向量对标题向量
    - 图片向量对描述向量
    - 图片向量对综合向量 (图片+标题+描述)
    
    可以通过match_modes指定一个或多个匹配模式，并通过weights指定每种模式的权重
    """
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
    
    # 处理权重
    mode_weights = {}
    if weights:
        weight_values = [float(w.strip()) for w in weights.split(",")]
        if len(weight_values) != len(match_modes):
            return ResponseModel.error(
                code="INVALID_PARAM",
                message="权重数量必须与匹配模式数量一致"
            )
        for mode, weight in zip(match_modes, weight_values):
            mode_weights[mode] = weight
    else:
        # 默认权重均匀分布
        weight_value = 1.0 / len(match_modes)
        for mode in match_modes:
            mode_weights[mode] = weight_value
    
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
        
        # 存储所有搜索结果
        all_results = {}
        
        # 对每种匹配模式执行搜索
        for mode in match_modes:
            # 基于匹配模式执行不同的向量搜索
            vector_results = []
            
            if mode == ImageVectorMatchMode.IMAGE:
                # 图片向量对图片向量搜索
                vector_results = vector_db.search_by_image(temp_path, limit=limit*2)
            elif mode == ImageVectorMatchMode.TITLE:
                # 图片向量对标题向量搜索
                # 需要先将图片编码为向量，然后搜索标题向量
                img = PILImage.open(temp_path)
                query_vector = encode_image(img)
                vector_results = vector_db.search_by_vector(query_vector, index_type="title", limit=limit*2)
            elif mode == ImageVectorMatchMode.DESCRIPTION:
                # 图片向量对描述向量搜索
                img = PILImage.open(temp_path)
                query_vector = encode_image(img)
                vector_results = vector_db.search_by_vector(query_vector, index_type="description", limit=limit*2)
            elif mode == ImageVectorMatchMode.COMBINED:
                # 图片向量对综合向量搜索 (需要综合计算多个向量索引的结果)
                img = PILImage.open(temp_path)
                query_vector = encode_image(img)
                
                # 获取多种向量的搜索结果
                image_results = vector_db.search_by_vector(query_vector, index_type="image", limit=limit*2)
                title_results = vector_db.search_by_vector(query_vector, index_type="title", limit=limit*2)
                desc_results = vector_db.search_by_vector(query_vector, index_type="description", limit=limit*2)
                
                # 合并结果
                combined_results = {}
                
                # 处理图像结果
                for result in image_results:
                    uuid = result["uuid"]
                    combined_results[uuid] = {"uuid": uuid, "similarity": float(result["similarity"]) * 0.6}
                
                # 处理标题结果
                for result in title_results:
                    uuid = result["uuid"]
                    if uuid in combined_results:
                        combined_results[uuid]["similarity"] += float(result["similarity"]) * 0.2
                    else:
                        combined_results[uuid] = {"uuid": uuid, "similarity": float(result["similarity"]) * 0.2}
                
                # 处理描述结果
                for result in desc_results:
                    uuid = result["uuid"]
                    if uuid in combined_results:
                        combined_results[uuid]["similarity"] += float(result["similarity"]) * 0.2
                    else:
                        combined_results[uuid] = {"uuid": uuid, "similarity": float(result["similarity"]) * 0.2}
                
                # 转换为列表
                vector_results = list(combined_results.values())
            
            # 为每个结果添加当前搜索模式的权重
            for result in vector_results:
                uuid = result["uuid"]
                
                if uuid not in all_results:
                    all_results[uuid] = {
                        "uuid": uuid,
                        "weighted_similarity": float(result["similarity"]) * mode_weights[mode],
                        "similarity_components": {str(mode): float(result["similarity"])}
                    }
                else:
                    all_results[uuid]["weighted_similarity"] += float(result["similarity"]) * mode_weights[mode]
                    all_results[uuid]["similarity_components"][str(mode)] = float(result["similarity"])
        
        # 将结果转换为列表
        result_list = list(all_results.values())
        
        # 按加权相似度排序
        result_list.sort(key=lambda x: x["weighted_similarity"], reverse=True)
        
        # 获取详细图片信息
        formatted_results = []
        for result in result_list[:limit*2]:  # 获取两倍结果用于过滤
            # 获取图片详细信息
            img = db.get_image_by_uuid(result["uuid"])
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
                    img["score"] = result["weighted_similarity"]
                    img["similarity_components"] = result["similarity_components"]
                    formatted_results.append({
                        "uuid": img["uuid"],
                        "title": img["title"],
                        "description": img.get("description", ""),
                        "filepath": img["filepath"],
                        "score": float(img["score"]),
                        "similarity_components": img["similarity_components"],
                        "tags": img["tags"]
                    })
        
        # 限制结果数量
        formatted_results = formatted_results[:limit]
        
        end_time = time.time()
        processing_time = int((end_time - start_time) * 1000)  # 毫秒
        
        return ResponseModel.success(
            data={"results": formatted_results},
            metadata={
                "search_type": search_type,
                "match_modes": [str(mode) for mode in match_modes],
                "weights": mode_weights,
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
    match_modes: List[VectorMatchMode] = Query([VectorMatchMode.IMAGE],alias="match_modes[]", description="匹配模式: image(图像), title(标题), description(描述), combined(综合)"), # 因为前端请求的值是以match_modes[]的形式传递的，所以这里需要使用alias来指定参数名
    limit: int = Query(20, ge=1, le=100, description="返回结果数量"),
    start_date: Optional[str] = Query(None, description="开始日期过滤"),
    end_date: Optional[str] = Query(None, description="结束日期过滤"),
    tags: Optional[str] = Query(None, description="标签过滤，逗号分隔")
):
    """
    根据系统中已存在的图片UUID搜索相似图片
    
    支持多种匹配模式:
    - 图片向量: 使用图片的视觉特征向量进行匹配
    - 标题向量: 使用图片标题的语义向量进行匹配
    - 描述向量: 使用图片描述的语义向量进行匹配
    - 综合模式: 结合上述多种向量的匹配结果
    
    可以通过match_modes指定一个或多个匹配模式
    """
    print(f"开始搜索相似图片，UUID: {uuid}, 匹配模式: {match_modes}, 限制数量: {limit}")
    # 检查向量搜索是否可用
    if not vector_search_available:
        return ResponseModel(
            status="error",
            error={
                "code": "SERVICE_UNAVAILABLE",
                "message": "向量搜索功能不可用，请检查模型配置"
            },
            data=None,
            metadata={}
        )
    
    # 检查图片是否存在
    image = db.get_image_by_uuid(uuid)
    if not image:
        return ResponseModel(
            status="error",
            error={
                "code": "NOT_FOUND",
                "message": "参考图片不存在"
            },
            data=None,
            metadata={}
        )
    
    # 处理标签过滤
    tag_list = None
    if tags:
        tag_list = [tag.strip() for tag in tags.split(",")]
    
    start_time = time.time()
    
    try:
        # 处理多种匹配模式
        all_results = {}
        mode_weights = {}
        total_weight = 0.0
        
        # 设置权重 - 根据匹配模式设置合理的默认值
        for mode in match_modes:
            if mode == VectorMatchMode.IMAGE:
                mode_weights[mode] = 0.7  # 图像匹配权重最高
            elif mode == VectorMatchMode.TITLE:
                mode_weights[mode] = 0.15  # 标题匹配权重中等
            elif mode == VectorMatchMode.DESCRIPTION:
                mode_weights[mode] = 0.15  # 描述匹配权重中等
            else:  # COMBINED或其他
                mode_weights[mode] = 0.4  # 综合模式权重适中
            total_weight += mode_weights[mode]
        
        # 权重归一化
        if total_weight > 0:
            for mode in mode_weights:
                mode_weights[mode] = mode_weights[mode] / total_weight
        
        # 对每种模式执行搜索
        for mode in match_modes:
            search_type_str = str(mode)  # 转换为字符串以匹配函数参数
            
            # 查询相似结果
            results = db.search_similar_to_uuid(
                uuid=uuid,
                search_type=search_type_str,
                limit=limit*2,  # 获取更多结果以便过滤和合并
                start_date=start_date,
                end_date=end_date,
                tags=tag_list
            )
            
            # 添加权重并合并结果
            for result in results:
                if result['uuid'] not in all_results:
                    # 首次添加这个结果
                    result['weighted_score'] = result['score'] * mode_weights[mode]
                    result['score_components'] = {str(mode): result['score']}
                    all_results[result['uuid']] = result
                else:
                    # 更新已有结果的加权分数
                    all_results[result['uuid']]['weighted_score'] += result['score'] * mode_weights[mode]
                    all_results[result['uuid']]['score_components'][str(mode)] = result['score']
        
        # 将合并结果转为列表
        merged_results = list(all_results.values())
        
        # 排序并更新最终得分
        for result in merged_results:
            result['score'] = result['weighted_score']  # 用加权分数替换原有分数
            
        merged_results.sort(key=lambda x: x['score'], reverse=True)
        
        # 限制结果数量
        merged_results = merged_results[:limit]
        
        if not merged_results:
            return ResponseModel(
                status="error",
                error={
                    "code": "NO_RESULTS",
                    "message": "未找到相似图片"
                },
                data=None,
                metadata={}
            )
        
        end_time = time.time()
        processing_time = int((end_time - start_time) * 1000)  # 毫秒
        
        return ResponseModel.success(
            data={"results": merged_results},
            metadata={
                "reference_uuid": uuid,
                "match_modes": [str(mode) for mode in match_modes],
                "mode_weights": {str(k): v for k, v in mode_weights.items()},
                "total": len(merged_results),
                "time_ms": processing_time
            }
        )
            
    except Exception as e:
        print(f"相似图片搜索处理出错: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return ResponseModel(
            status="error",
            error={
                "code": "SYSTEM_ERROR",
                "message": f"系统错误: {str(e)}"
            },
            data=None,
            metadata={}
        )
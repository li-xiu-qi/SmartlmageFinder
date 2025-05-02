import os
import faiss
import numpy as np
import pickle
from typing import List, Dict, Any, Tuple, Optional, Union
from PIL import Image

# 导入项目的向量生成模块
from .generate_vector import encode_text, encode_image
from .config import settings

# 向量维度 (基于 jinaai/jina-embeddings-v2-base-en 模型)
VECTOR_DIM = 1024


# 全局变量
text_index = None  # 文本向量索引
image_index = None  # 图像向量索引
uuid_map = {}  # UUID到索引ID的映射


def init_indices():
    """初始化向量索引"""
    global text_index, image_index, uuid_map
    
    # 创建或加载文本向量索引
    if os.path.exists(settings.TEXT_INDEX_PATH):
        try:
            text_index = faiss.read_index(settings.TEXT_INDEX_PATH)
            print(f"已加载文本向量索引，包含{text_index.ntotal}个向量")
        except Exception as e:
            print(f"加载文本向量索引失败: {e}")
            text_index = faiss.IndexFlatIP(VECTOR_DIM)  # 使用内积相似度
    else:
        text_index = faiss.IndexFlatIP(VECTOR_DIM)
        print("创建了新的文本向量索引")
    
    # 创建或加载图像向量索引
    if os.path.exists(settings.IMAGE_INDEX_PATH):
        try:
            image_index = faiss.read_index(settings.IMAGE_INDEX_PATH)
            print(f"已加载图像向量索引，包含{image_index.ntotal}个向量")
        except Exception as e:
            print(f"加载图像向量索引失败: {e}")
            image_index = faiss.IndexFlatIP(VECTOR_DIM)
    else:
        image_index = faiss.IndexFlatIP(VECTOR_DIM)
        print("创建了新的图像向量索引")
    
    # 加载UUID映射
    if os.path.exists(settings.UUID_MAP_PATH):
        try:
            with open(settings.UUID_MAP_PATH, 'rb') as f:
                uuid_map = pickle.load(f)
            print(f"已加载UUID映射，包含{len(uuid_map)}个条目")
        except Exception as e:
            print(f"加载UUID映射失败: {e}")
            uuid_map = {}
    else:
        uuid_map = {}
        print("创建了新的UUID映射")


def save_indices():
    """保存向量索引到磁盘"""
    if text_index is not None:
        try:
            faiss.write_index(text_index, settings.TEXT_INDEX_PATH)
            print(f"文本向量索引已保存，包含{text_index.ntotal}个向量")
        except Exception as e:
            print(f"保存文本向量索引失败: {e}")
    
    if image_index is not None:
        try:
            faiss.write_index(image_index, settings.IMAGE_INDEX_PATH)
            print(f"图像向量索引已保存，包含{image_index.ntotal}个向量")
        except Exception as e:
            print(f"保存图像向量索引失败: {e}")
    
    # 保存UUID映射
    try:
        with open(settings.UUID_MAP_PATH, 'wb') as f:
            pickle.dump(uuid_map, f)
        print(f"UUID映射已保存，包含{len(uuid_map)}个条目")
    except Exception as e:
        print(f"保存UUID映射失败: {e}")


def add_text_vector(uuid: str, text: str):
    """将文本向量添加到索引"""
    global text_index, uuid_map
    
    if text_index is None:
        init_indices()
    
    # 生成文本向量
    vector = encode_text(text)
    
    # 确保向量为numpy数组，并转换为float32类型
    if not isinstance(vector, np.ndarray):
        vector = np.array(vector)
    
    if vector.dtype != np.float32:
        vector = vector.astype(np.float32)
    
    # 确保向量是二维的 [1, dim]
    if len(vector.shape) == 1:
        vector = vector.reshape(1, -1)
    
    # 如果已存在此UUID，先标记删除
    if uuid in uuid_map:
        old_id = uuid_map[uuid]["text_id"]
        # 在FAISS中，我们不能直接删除，但可以用零向量替代
        # 这里我们直接添加新向量，并在uuid_map中更新索引
    
    # 添加向量到索引
    idx = text_index.ntotal
    text_index.add(vector)
    
    # 更新UUID映射
    if uuid not in uuid_map:
        uuid_map[uuid] = {"text_id": idx, "image_id": None}
    else:
        uuid_map[uuid]["text_id"] = idx
    
    return idx


def add_image_vector(uuid: str, image_path: str):
    """将图像向量添加到索引"""
    global image_index, uuid_map
    
    if image_index is None:
        init_indices()
    
    # 检查文件是否存在
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"图像文件不存在: {image_path}")
    
    # 生成图像向量
    try:
        # 打开图像
        img = Image.open(image_path)
        # 生成向量
        vector = encode_image(img)
        
        # 确保向量为numpy数组，并转换为float32类型
        if not isinstance(vector, np.ndarray):
            vector = np.array(vector)
        
        if vector.dtype != np.float32:
            vector = vector.astype(np.float32)
        
        # 确保向量是二维的 [1, dim]
        if len(vector.shape) == 1:
            vector = vector.reshape(1, -1)
        
        # 如果已存在此UUID，先标记删除
        if uuid in uuid_map and uuid_map[uuid]["image_id"] is not None:
            old_id = uuid_map[uuid]["image_id"]
            # 同样，我们不直接删除，而是在uuid_map中更新索引
        
        # 添加向量到索引
        idx = image_index.ntotal
        image_index.add(vector)
        
        # 更新UUID映射
        if uuid not in uuid_map:
            uuid_map[uuid] = {"text_id": None, "image_id": idx}
        else:
            uuid_map[uuid]["image_id"] = idx
        
        return idx
        
    except Exception as e:
        raise Exception(f"处理图像向量时出错: {e}")


def delete_vectors(uuid: str):
    """标记删除向量索引中的条目"""
    if uuid in uuid_map:
        # 在生产环境中，我们需要一个更复杂的删除策略
        # 这里我们简单地从UUID映射中移除，但向量仍然在索引中
        # 定期维护时可以重建索引来真正清理已删除的向量
        del uuid_map[uuid]
        return True
    return False


def search_by_text(query_text: str, limit: int = 20) -> List[Dict[str, Any]]:
    """通过文本查询向量索引"""
    if text_index is None or text_index.ntotal == 0:
        return []
    
    # 生成查询文本的向量
    query_vector = encode_text(query_text)
    
    # 确保向量为numpy数组，并转换为float32类型
    if not isinstance(query_vector, np.ndarray):
        query_vector = np.array(query_vector)
    
    if query_vector.dtype != np.float32:
        query_vector = query_vector.astype(np.float32)
    
    # 确保向量是二维的 [1, dim]
    if len(query_vector.shape) == 1:
        query_vector = query_vector.reshape(1, -1)
    
    # 执行搜索
    try:
        D, I = text_index.search(query_vector, min(limit, text_index.ntotal))
        
        # 转换结果
        results = []
        for i, (distance, idx) in enumerate(zip(D[0], I[0])):
            # 查找对应的UUID
            uuid = None
            for u, ids in uuid_map.items():
                if ids["text_id"] == idx:
                    uuid = u
                    break
            
            if uuid:
                results.append({
                    "uuid": uuid,
                    "similarity": float(distance),
                    "index": int(idx)
                })
        
        return results
    
    except Exception as e:
        print(f"文本搜索失败: {e}")
        return []


def search_by_image(image_path: str, limit: int = 20) -> List[Dict[str, Any]]:
    """通过图像路径查询向量索引"""
    if image_index is None or image_index.ntotal == 0:
        return []
    
    # 检查文件是否存在
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"图像文件不存在: {image_path}")
    
    try:
        # 打开图像
        img = Image.open(image_path)
        # 生成向量
        query_vector = encode_image(img)
        
        # 确保向量为numpy数组，并转换为float32类型
        if not isinstance(query_vector, np.ndarray):
            query_vector = np.array(query_vector)
        
        if query_vector.dtype != np.float32:
            query_vector = query_vector.astype(np.float32)
        
        # 确保向量是二维的 [1, dim]
        if len(query_vector.shape) == 1:
            query_vector = query_vector.reshape(1, -1)
        
        # 执行搜索
        D, I = image_index.search(query_vector, min(limit, image_index.ntotal))
        
        # 转换结果
        results = []
        for i, (distance, idx) in enumerate(zip(D[0], I[0])):
            # 查找对应的UUID
            uuid = None
            for u, ids in uuid_map.items():
                if ids["image_id"] == idx:
                    uuid = u
                    break
            
            if uuid:
                results.append({
                    "uuid": uuid,
                    "similarity": float(distance),
                    "index": int(idx)
                })
        
        return results
    
    except Exception as e:
        print(f"图像搜索失败: {e}")
        return []


def search_by_uuid(uuid: str, limit: int = 20, search_type: str = "image") -> List[Dict[str, Any]]:
    """通过图片UUID查找相似图片"""
    if uuid not in uuid_map:
        return []
    
    if search_type == "image" and image_index is not None and uuid_map[uuid]["image_id"] is not None:
        # 使用图像向量搜索
        idx = uuid_map[uuid]["image_id"]
        
        # 从索引获取向量
        vector = np.zeros((1, VECTOR_DIM), dtype=np.float32)
        vector_id = np.array([idx], dtype=np.int64)
        
        # 这需要一个更复杂的方法来从FAISS检索单个向量
        # 以下是一个假设实现，实际上我们可能需要其他方法
        # 在实际生产环境中，您可能需要缓存向量或实现更高效的检索
        
        # 对于IndexFlatIP，我们可以直接访问底层存储
        if isinstance(image_index, faiss.IndexFlat):
            vector = faiss.vector_to_array(image_index.get_xb()).reshape(-1, VECTOR_DIM)[idx:idx+1]
        
        # 执行搜索
        D, I = image_index.search(vector, min(limit + 1, image_index.ntotal))  # +1 因为结果中会包含查询图片自身
        
        # 转换结果 (排除自身)
        results = []
        for i, (distance, result_idx) in enumerate(zip(D[0], I[0])):
            # 排除查询图片自身
            if result_idx == idx:
                continue
                
            # 查找对应的UUID
            result_uuid = None
            for u, ids in uuid_map.items():
                if ids["image_id"] == result_idx:
                    result_uuid = u
                    break
            
            if result_uuid:
                results.append({
                    "uuid": result_uuid,
                    "similarity": float(distance),
                    "index": int(result_idx)
                })
        
        return results
        
    elif search_type == "text" and text_index is not None and uuid_map[uuid]["text_id"] is not None:
        # 使用文本向量搜索
        idx = uuid_map[uuid]["text_id"]
        
        # 从索引获取向量
        vector = np.zeros((1, VECTOR_DIM), dtype=np.float32)
        
        # 对于IndexFlatIP，我们可以直接访问底层存储
        if isinstance(text_index, faiss.IndexFlat):
            vector = faiss.vector_to_array(text_index.get_xb()).reshape(-1, VECTOR_DIM)[idx:idx+1]
        
        # 执行搜索
        D, I = text_index.search(vector, min(limit + 1, text_index.ntotal))
        
        # 转换结果 (排除自身)
        results = []
        for i, (distance, result_idx) in enumerate(zip(D[0], I[0])):
            # 排除查询图片自身
            if result_idx == idx:
                continue
                
            # 查找对应的UUID
            result_uuid = None
            for u, ids in uuid_map.items():
                if ids["text_id"] == result_idx:
                    result_uuid = u
                    break
            
            if result_uuid:
                results.append({
                    "uuid": result_uuid,
                    "similarity": float(distance),
                    "index": int(result_idx)
                })
        
        return results
    
    return []

# 初始化索引
init_indices()
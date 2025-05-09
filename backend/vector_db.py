import os
import faiss
import numpy as np
import pickle
from typing import List, Dict, Any, Tuple, Optional, Union, Protocol, Callable
from PIL import Image
import abc

# 导入项目的向量生成模块
from .generate_vector import encode_text, encode_image
from .config import settings



class VectorIndex(abc.ABC):
    """向量索引抽象基类"""
    
    def __init__(self, index_path: str, index_type: str, uuid_map: Dict, encode_func: Callable):
        """初始化向量索引
        
        参数:
            index_path: 索引文件路径
            index_type: 索引类型标识符 ("title", "description", "image")
            uuid_map: UUID映射字典的引用
            encode_func: 编码函数，接受输入数据并返回向量
        """
        self.index_path = index_path
        self.index_type = index_type
        self.index = None
        self.uuid_map = uuid_map
        self.encode_func = encode_func
    
    def init_index(self):
        """初始化索引"""
        if os.path.exists(self.index_path):
            try:
                self.index = faiss.read_index(self.index_path)
                print(f"已加载{self.index_type}向量索引，包含{self.index.ntotal}个向量")
            except Exception as e:
                print(f"加载{self.index_type}向量索引失败: {e}")
                self.index = faiss.IndexFlatIP(settings.VECTOR_DIM)  # 使用内积相似度
        else:
            self.index = faiss.IndexFlatIP(settings.VECTOR_DIM)
            print(f"创建了新的{self.index_type}向量索引")
    
    def save_index(self):
        """保存索引到磁盘"""
        if self.index is not None:
            try:
                faiss.write_index(self.index, self.index_path)
                print(f"{self.index_type}向量索引已保存，包含{self.index.ntotal}个向量")
            except Exception as e:
                print(f"保存{self.index_type}向量索引失败: {e}")
    
    def add_vector(self, uuid: str, data):
        """添加向量到索引
        
        参数:
            uuid: 数据的UUID
            data: 要编码的数据(文本或图像路径)
        """
        if self.index is None:
            self.init_index()
        
        # 获取向量
        vector = self._get_vector(data)
        
        # 添加向量到索引
        idx = self.index.ntotal
        self.index.add(vector)
        
        # 更新UUID映射
        if uuid not in self.uuid_map:
            self.uuid_map[uuid] = {f"{self.index_type}_id": idx}
        else:
            self.uuid_map[uuid][f"{self.index_type}_id"] = idx
        
        return idx
    
    def search(self, query, limit: int = 20) -> List[Dict[str, Any]]:
        """搜索相似向量
        
        参数:
            query: 查询数据(文本或图像路径)
            limit: 返回结果数量上限
        """
        if self.index is None or self.index.ntotal == 0:
            return []
        
        # 获取查询向量
        query_vector = self._get_vector(query)
        
        # 执行搜索
        try:
            D, I = self.index.search(query_vector, min(limit, self.index.ntotal))
            
            # 转换结果
            results = []
            for i, (distance, idx) in enumerate(zip(D[0], I[0])):
                # 查找对应的UUID
                uuid = None
                for u, ids in self.uuid_map.items():
                    if ids.get(f"{self.index_type}_id") == idx:
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
            print(f"{self.index_type}搜索失败: {e}")
            return []
    
    def search_by_vector(self, query_vector: np.ndarray, limit: int = 20) -> List[Dict[str, Any]]:
        """使用向量直接搜索相似向量
        
        参数:
            query_vector: 查询向量
            limit: 返回结果数量上限
        """
        if self.index is None or self.index.ntotal == 0:
            return []
        
        # 确保向量格式正确
        if not isinstance(query_vector, np.ndarray):
            query_vector = np.array(query_vector)
        
        if query_vector.dtype != np.float32:
            query_vector = query_vector.astype(np.float32)
        
        # 确保向量是二维的 [1, dim]
        if len(query_vector.shape) == 1:
            query_vector = query_vector.reshape(1, -1)
            
        # 执行搜索
        try:
            D, I = self.index.search(query_vector, min(limit, self.index.ntotal))
            
            # 转换结果
            results = []
            for i, (distance, idx) in enumerate(zip(D[0], I[0])):
                # 查找对应的UUID
                uuid = None
                for u, ids in self.uuid_map.items():
                    if ids.get(f"{self.index_type}_id") == idx:
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
            print(f"{self.index_type}向量搜索失败: {e}")
            return []
    
    def search_by_id(self, idx: int, limit: int = 20) -> List[Dict[str, Any]]:
        """通过内部索引ID搜索相似向量"""
        if self.index is None or self.index.ntotal == 0:
            return []
        
        try:
            # 确保索引在有效范围内
            if idx < 0 or idx >= self.index.ntotal:
                print(f"索引ID {idx} 超出范围 [0, {self.index.ntotal-1}]")
                return []
            
            # 方法1: 简单地查询所有索引，通过UUID映射找到匹配的结果
            results = []
            source_uuid = None
            
            # 先找到对应的源UUID
            for u, ids in self.uuid_map.items():
                if ids.get(f"{self.index_type}_id") == idx:
                    source_uuid = u
                    break
            
            if not source_uuid:
                print(f"找不到索引ID {idx} 对应的UUID")
                return []
            
            # 对于每个索引项，创建一个结果
            for uuid, ids in self.uuid_map.items():
                # 跳过自己
                if uuid == source_uuid:
                    continue
                
                # 获取此UUID的索引ID
                result_id = ids.get(f"{self.index_type}_id")
                if result_id is not None:
                    # 尝试使用FAISS的方式计算相似度
                    try:
                        # 使用范围内的索引进行查询
                        if isinstance(self.index, faiss.IndexFlat):
                            # 只用到单个ID进行搜索，不取向量
                            D, I = self.index.search(self.index.reconstruct(idx).reshape(1, -1), limit + 1)
                            
                            # 找到当前UUID对应的位置和分数
                            for i, result_idx in enumerate(I[0]):
                                if result_idx == result_id:
                                    # 找到了当前UUID，添加结果
                                    results.append({
                                        "uuid": uuid,
                                        "similarity": float(D[0][i]),
                                        "index": int(result_id)
                                    })
                                    break
                    except Exception as e:
                        # 如果FAISS检索失败，使用备用计算方法
                        print(f"FAISS计算相似度失败: {e}，将使用备用方法")
                        # 简单地按照索引ID的接近程度生成一个相似度
                        similarity = 1.0 - abs(idx - result_id) / self.index.ntotal
                        
                        results.append({
                            "uuid": uuid,
                            "similarity": float(max(0.1, similarity)),  # 确保相似度至少为0.1
                            "index": int(result_id)
                        })
            
            # 按相似度排序
            results.sort(key=lambda x: x["similarity"], reverse=True)
            
            # 限制结果数量
            return results[:limit]
                
        except Exception as e:
            print(f"{self.index_type}ID搜索失败: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _get_vector(self, data) -> np.ndarray:
        """从数据中获取向量表示
        
        参数:
            data: 要编码的数据
        
        返回:
            numpy.ndarray: 归一化的向量表示
        """
        # 使用编码函数获取向量
        vector = self.encode_func(data)
        
        # 确保向量为numpy数组，并转换为float32类型
        if not isinstance(vector, np.ndarray):
            vector = np.array(vector)
        
        if vector.dtype != np.float32:
            vector = vector.astype(np.float32)
        
        # 确保向量是二维的 [1, dim]
        if len(vector.shape) == 1:
            vector = vector.reshape(1, -1)
        
        return vector


class TextVectorIndex(VectorIndex):
    """文本向量索引类"""
    
    def __init__(self, index_path: str, index_type: str, uuid_map: Dict):
        super().__init__(index_path, index_type, uuid_map, encode_text)


class ImageVectorIndex(VectorIndex):
    """图像向量索引类"""
    
    def __init__(self, index_path: str, uuid_map: Dict):
        super().__init__(index_path, "image", uuid_map, self._encode_image_wrapper)
    
    def _encode_image_wrapper(self, image_path: str) -> np.ndarray:
        """图像编码包装函数，处理图像路径转换为向量
        
        参数:
            image_path: 图像文件路径
            
        返回:
            numpy.ndarray: 图像的向量表示
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"图像文件不存在: {image_path}")
        
        # 打开图像
        img = Image.open(image_path)
        # 生成向量
        return encode_image(img)


# 全局变量
uuid_map = {}  # UUID到索引ID的映射
title_index = None
description_index = None
image_index = None


def init_indices():
    """初始化所有向量索引"""
    global uuid_map, title_index, description_index, image_index
    
    # 如果所有索引都已初始化，则直接返回
    if title_index is not None and description_index is not None and image_index is not None:
        return
    
    # 加载UUID映射
    if not uuid_map:  # 只在uuid_map为空时加载
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
    
    # 初始化各个索引（如果尚未初始化）
    if title_index is None:
        title_index = TextVectorIndex(settings.TITLE_INDEX_PATH, "title", uuid_map)
        title_index.init_index()
    
    if description_index is None:
        description_index = TextVectorIndex(settings.DESCRIPTION_INDEX_PATH, "description", uuid_map)
        description_index.init_index()
    
    if image_index is None:
        image_index = ImageVectorIndex(settings.IMAGE_INDEX_PATH, uuid_map)
        image_index.init_index()


def save_indices():
    """保存所有向量索引到磁盘"""
    if title_index:
        title_index.save_index()
    
    if description_index:
        description_index.save_index()
    
    if image_index:
        image_index.save_index()
    
    # 保存UUID映射
    try:
        with open(settings.UUID_MAP_PATH, 'wb') as f:
            pickle.dump(uuid_map, f)
        print(f"UUID映射已保存，包含{len(uuid_map)}个条目")
    except Exception as e:
        print(f"保存UUID映射失败: {e}")


def add_title_vector(uuid: str, title: str):
    """将标题向量添加到索引"""
    global title_index
    if title_index is None:
        init_indices()
    if not title or not title.strip():
        return None
    return title_index.add_vector(uuid, title)


def add_description_vector(uuid: str, description: str):
    """将描述向量添加到索引"""
    global description_index
    if description_index is None:
        init_indices()
    if not description or not description.strip():
        return None
    return description_index.add_vector(uuid, description)


def add_image_vector(uuid: str, image_path: str):
    """将图像向量添加到索引"""
    global image_index
    if image_index is None:
        init_indices()
    return image_index.add_vector(uuid, image_path)


def delete_vectors(uuid: str):
    """标记删除向量索引中的条目"""
    if uuid in uuid_map:
        # 在生产环境中，我们需要一个更复杂的删除策略
        # 这里我们简单地从UUID映射中移除，但向量仍然在索引中
        # 定期维护时可以重建索引来真正清理已删除的向量
        del uuid_map[uuid]
        return True
    return False


def search_by_title(query_text: str, limit: int = 20) -> List[Dict[str, Any]]:
    """通过标题文本查询向量索引"""
    global title_index
    if title_index is None:
        init_indices()
    return title_index.search(query_text, limit)


def search_by_description(query_text: str, limit: int = 20) -> List[Dict[str, Any]]:
    """通过描述文本查询向量索引"""
    global description_index
    if description_index is None:
        init_indices()
    return description_index.search(query_text, limit)


def search_by_image(image_path: str, limit: int = 20) -> List[Dict[str, Any]]:
    """通过图像路径查询向量索引"""
    global image_index
    if image_index is None:
        init_indices()
    return image_index.search(image_path, limit)


def search_by_vector(query_vector: np.ndarray, index_type: str = "image", limit: int = 20) -> List[Dict[str, Any]]:
    """根据向量类型搜索相似向量
    
    参数:
        query_vector: 查询向量
        index_type: 要搜索的索引类型，可选值: "title", "description", "image"
        limit: 返回结果数量上限
    
    返回:
        List[Dict[str, Any]]: 相似结果列表
    """
    global title_index, description_index, image_index
    
    if index_type == "title":
        if title_index is None:
            init_indices()
        return title_index.search_by_vector(query_vector, limit)
    
    elif index_type == "description":
        if description_index is None:
            init_indices()
        return description_index.search_by_vector(query_vector, limit)
    
    else:  # 默认为image
        if image_index is None:
            init_indices()
        return image_index.search_by_vector(query_vector, limit)


def search_by_uuid(uuid: str, limit: int = 20, search_type: str = "image") -> List[Dict[str, Any]]:
    """通过UUID查找相似内容
    
    参数:
        uuid: 要搜索的UUID
        limit: 返回结果数量上限
        search_type: 搜索类型，可选值: "title", "description", "image"
    """
    global uuid_map, title_index, description_index, image_index
    
    if uuid not in uuid_map:
        return []
    
    if search_type == "image" and uuid_map[uuid].get("image_id") is not None:
        if image_index is None:
            init_indices()
        return image_index.search_by_id(uuid_map[uuid]["image_id"], limit)
    
    elif search_type == "title" and uuid_map[uuid].get("title_id") is not None:
        if title_index is None:
            init_indices()
        return title_index.search_by_id(uuid_map[uuid]["title_id"], limit)
    
    elif search_type == "description" and uuid_map[uuid].get("description_id") is not None:
        if description_index is None:
            init_indices()
        return description_index.search_by_id(uuid_map[uuid]["description_id"], limit)
    
    # 默认使用图像向量
    elif uuid_map[uuid].get("image_id") is not None:
        if image_index is None:
            init_indices()
        return image_index.search_by_id(uuid_map[uuid]["image_id"], limit)
    
    return []


def search_by_text(query_text: str, limit: int = 20) -> List[Dict[str, Any]]:
    """通过文本查询标题和描述向量索引，并合并结果"""
    # 分别查询标题和描述
    title_results = search_by_title(query_text, limit)
    desc_results = search_by_description(query_text, limit)
    
    # 合并结果，按相似度排序
    all_results = {}
    
    for result in title_results:
        uuid = result["uuid"]
        all_results[uuid] = {
            "uuid": uuid,
            "similarity": result["similarity"] * 0.7,  # 标题权重更高
            "index": result["index"]
        }
    
    for result in desc_results:
        uuid = result["uuid"]
        if uuid in all_results:
            # 如果在标题结果中已存在，加权合并
            all_results[uuid]["similarity"] += result["similarity"] * 0.3  # 描述权重较低
        else:
            all_results[uuid] = {
                "uuid": uuid,
                "similarity": result["similarity"] * 0.3,  # 仅描述匹配时权重较低
                "index": result["index"]
            }
    
    # 转换为列表并按相似度排序
    merged_results = list(all_results.values())
    merged_results.sort(key=lambda x: x["similarity"], reverse=True)
    
    # 限制结果数量
    return merged_results[:limit]


# 初始化索引
init_indices()
from sentence_transformers import SentenceTransformer
from PIL import Image
import numpy as np
from typing import List, Union, Dict, Any
import os
import diskcache
import hashlib
import torch  # 导入torch库
from ..config import settings  # 导入配置
from ..utils.text_utils import get_text_cache_key  # 导入文本缓存键生成函数
from ..utils.image_utils import get_image_cache_key  # 导入图像缓存键生成函数

# 全局变量，用于保存加载的模型和维度信息
model = None
embedding_dimension = None
model_loading = False  # 添加加载状态标志


def load_model():
    """加载设置中指定的SentenceTransformer模型（非致命：失败返回 None）"""
    global model, embedding_dimension, model_loading
    
    # 如果模型已经加载，直接返回
    if model is not None:
        return model
    
    # 如果正在加载中，等待加载完成
    if model_loading:
        import time
        print("模型正在加载中，等待...")
        while model_loading and model is None:
            time.sleep(0.1)
        return model
    
    # 设置加载状态
    model_loading = True
    try:
        config = settings.get_config()
        model_path = getattr(config, 'MODEL_PATH', None)
        if not model_path:
            print("警告: MODEL_PATH 未配置，模型不可用")
            return None

        # 解析为绝对路径
        import os
        if not os.path.isabs(model_path):
            model_path = os.path.normpath(os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
                model_path.lstrip("./")
            ))
        if not os.path.isdir(model_path):
            print(f"警告: 模型目录不存在: {model_path}，向量功能不可用")
            return None

        # 判断是否有可用的CUDA设备
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"正在使用设备: {device}")
        
        print(f"正在加载模型: {model_path}")
        try:
            model = SentenceTransformer(
                model_path,
                trust_remote_code=True,
                device=device,
                model_kwargs={'default_task': 'retrieval'}
            )
        except TypeError as e:
            if 'default_task' in str(e):
                print("模型不接受 default_task 参数，使用兼容加载方式")
                model = SentenceTransformer(
                    model_path,
                    trust_remote_code=True,
                    device=device
                )
            else:
                raise

        # 优先使用 get_sentence_embedding_dimension; 失败/为空则探测
        try:
            embedding_dimension = model.get_sentence_embedding_dimension()
        except Exception:
            embedding_dimension = None
        if not embedding_dimension:
            try:
                probe = model.encode(["_dim_probe_"], normalize_embeddings=True, show_progress_bar=False)
            except TypeError:
                probe = model.encode(["_dim_probe_"])
            if isinstance(probe, list) and probe and len(probe[0]) > 0:
                embedding_dimension = len(probe[0])
            elif hasattr(probe, 'shape') and len(getattr(probe, 'shape', [])) >= 2:
                embedding_dimension = probe.shape[-1]
            else:
                fallback = settings.get_config().EMBEDDING_DIMENSION
                print(f"无法探测维度，使用配置回退: {fallback}")
                embedding_dimension = fallback
        print(f"模型加载成功，向量维度: {embedding_dimension}")
        return model

    except ImportError as e:
        print(f"警告: 模型依赖缺失 ({e})，向量功能不可用")
        return None
    except Exception as e:
        print(f"警告: 模型加载失败 ({e})，向量功能不可用")
        return None
    finally:
        model_loading = False

def get_model():
    """返回加载的模型实例（可能为 None）"""
    global model
    if model is None:
        load_model()
    return model


def get_embedding_dimension() -> int:
    """返回向量维度（模型不可用时返回配置值或 0）"""
    global embedding_dimension, model
    if model is None and not model_loading:
        load_model()
    return embedding_dimension or 0


def encode_text(text: Union[str, List[str]], cache_dir=None) -> np.ndarray:
    """将文本或文本列表编码成向量。"""
    # 使用缓存
    config = settings.get_config()
    cache_dir = cache_dir or config.TEXT_VECTOR_CACHE_DIR

    # 先尝试从缓存获取
    cache_key = get_text_cache_key(text)
    cache_instance = diskcache.Cache(
        directory=cache_dir, size_limit=config.MAX_CACHE_SIZE_GB * 2**30
    )

    embeddings = cache_instance.get(cache_key)
    if embeddings is not None:
        print(f"文本向量从缓存获取: {cache_key}")
        # 注意：从缓存加载的numpy数组在CPU上，如果后续有需要GPU的操作，需手动转移
        return embeddings

    # 缓存未命中，计算向量
    model_instance = get_model()
    if model_instance is None:
        raise RuntimeError("向量模型未加载，语义搜索不可用。请检查模型是否已下载。")
    # encode方法会自动处理设备，结果默认返回numpy数组(在CPU上)
    # 添加 task 参数以确保兼容性
    try:
        embeddings = model_instance.encode(text, normalize_embeddings=True, task='retrieval')
    except TypeError:
        # 如果模型不支持 task 参数，则使用原始方法
        embeddings = model_instance.encode(text, normalize_embeddings=True)

    cache_instance.set(cache_key, embeddings)

    return embeddings


def encode_image(
    image_input: Union[Image.Image, List[Image.Image], str, List[str]], cache_dir=None
) -> np.ndarray:
    """将图像(PIL Image、路径)或图像列表编码成向量。"""
    # 使用缓存
    config = settings.get_config()
    cache_dir = cache_dir or config.IMAGE_VECTOR_CACHE_DIR

    cache_key = get_image_cache_key(image_input)
    # 注意: diskcache 的 size_limit 单位为字节
    # 之前错误地传入了以 GB 为单位的浮点数，导致几乎所有写入都会被立即逐出
    cache_instance = diskcache.Cache(
        directory=cache_dir, size_limit=int(config.MAX_CACHE_SIZE_GB * (2**30))
    )

    embeddings = cache_instance.get(cache_key)
    if embeddings is not None:
        print(f"图像向量从缓存获取: {cache_key}")
        return embeddings

    # 缓存未命中，计算向量
    model_instance = get_model()
    if model_instance is None:
        raise RuntimeError("向量模型未加载，语义搜索不可用。请检查模型是否已下载。")
    # 处理单个PIL图像或路径
    if isinstance(image_input, (Image.Image, str)):
        images_to_encode = [image_input]
    else:
        images_to_encode = image_input

    # encode方法会自动处理设备，结果默认返回numpy数组(在CPU上)
    # 添加 task 参数以确保兼容性
    try:
        embeddings = model_instance.encode(images_to_encode, normalize_embeddings=True, task='retrieval')
    except TypeError:
        # 如果模型不支持 task 参数，则使用原始方法
        embeddings = model_instance.encode(images_to_encode, normalize_embeddings=True)

    # 如果输入是单个对象，返回单个向量
    if isinstance(image_input, (Image.Image, str)):
        embedding_to_cache = embeddings[0]
        embedding_to_return = embeddings[0]
    else:
        embedding_to_cache = embeddings
        embedding_to_return = embeddings

    cache_instance.set(cache_key, embedding_to_cache)

    return embedding_to_return
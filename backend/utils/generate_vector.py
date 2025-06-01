from sentence_transformers import SentenceTransformer
from PIL import Image
import numpy as np
from typing import List, Union, Dict, Any
import os
import diskcache
import hashlib
from ..config import settings  # 导入配置
from .text_utils import get_text_cache_key  # 导入文本缓存键生成函数
from .image_utils import get_image_cache_key  # 导入图像缓存键生成函数

# 全局变量，用于保存加载的模型和维度信息
model = None
embedding_dimension = None
model_loading = False  # 添加加载状态标志


def load_model():
    """加载设置中指定的SentenceTransformer模型并获取向量维度"""
    global model, embedding_dimension, model_loading
    
    # 如果模型已经加载，直接返回
    if model is not None:
        return model
    
    # 如果正在加载中，等待加载完成
    if model_loading:
        import time
        print("模型正在加载中，等待...")
        while model_loading and model is None:
            time.sleep(0.1)  # 等待100ms后再检查
        return model
    
    # 设置加载状态
    model_loading = True
    try:
        config = settings.get_config()
        print(f"正在加载模型: {config.MODEL_PATH}")
        model = SentenceTransformer(
            config.MODEL_PATH,
            trust_remote_code=True,
        )
        # 自动获取模型输出维度
        embedding_dimension = model.get_sentence_embedding_dimension()
        print(f"模型加载成功，向量维度: {embedding_dimension}")
        if embedding_dimension is None:
            embedding_dimension = settings.get_config().EMBEDDING_DIMENSION
            print(f"未能自动获取向量维度，使用默认值: {embedding_dimension}")
    finally:
        # 无论成功还是失败，都要重置加载状态
        model_loading = False
    
    return model

def get_model() -> SentenceTransformer:
    """返回加载的模型实例，如果需要就加载模型"""
    global model
    if model is None:
        load_model()
    return model


def get_embedding_dimension() -> int:
    """返回向量维度"""
    global embedding_dimension, model
    # 如果模型未加载，先加载模型
    if model is None:
        load_model()

    return embedding_dimension


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
        return embeddings

    # 缓存未命中，计算向量
    model_instance = get_model()
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
    cache_instance = diskcache.Cache(
        directory=cache_dir, size_limit=config.MAX_CACHE_SIZE_GB
    )

    embeddings = cache_instance.get(cache_key)
    if embeddings is not None:
        print(f"图像向量从缓存获取: {cache_key}")
        return embeddings

    # 缓存未命中，计算向量
    model_instance = get_model()
    # 处理单个PIL图像或路径
    if isinstance(image_input, (Image.Image, str)):
        images_to_encode = [image_input]
    else:
        images_to_encode = image_input

    embeddings = model_instance.encode(images_to_encode, normalize_embeddings=True)

    if isinstance(image_input, (Image.Image, str)):
        # 单个向量情况，缓存结果
        cache_instance.set(cache_key, embeddings[0])
    else:
        cache_instance.set(cache_key, embeddings)

    # 如果输入是单个对象，返回单个向量
    if isinstance(image_input, (Image.Image, str)):
        return embeddings[0]
    return embeddings

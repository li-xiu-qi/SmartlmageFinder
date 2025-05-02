from sentence_transformers import SentenceTransformer
from PIL import Image
import numpy as np
from typing import List, Union
import os
import diskcache
import hashlib
from .config import settings  # 导入配置

# 全局变量，用于保存加载的模型
model = None

def get_text_cache_key(text: Union[str, List[str]]) -> str:
    """生成文本的缓存键"""
    if isinstance(text, list):
        # 对于文本列表，连接所有文本再生成哈希
        combined = "".join(text)
        return hashlib.md5(combined.encode('utf-8')).hexdigest()
    else:
        # 对于单个文本字符串
        return hashlib.md5(text.encode('utf-8')).hexdigest()

def get_image_cache_key(image_input: Union[Image.Image, List[Image.Image], str, List[str]]) -> str:
    """生成图像的缓存键"""
    if isinstance(image_input, str):
        # 对于图像路径，使用文件内容的哈希
        if os.path.exists(image_input):
            with open(image_input, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        else:
            raise FileNotFoundError(f"图像文件不存在: {image_input}")
    
    elif isinstance(image_input, Image.Image):
        # 对于PIL图像对象，转换为字节再生成哈希
        img_bytes = np.array(image_input).tobytes()
        return hashlib.md5(img_bytes).hexdigest()
    
    elif isinstance(image_input, list):
        # 对于列表，递归处理每个元素并组合哈希
        combined = ""
        for item in image_input:
            combined += get_image_cache_key(item)
        return hashlib.md5(combined.encode('utf-8')).hexdigest()
    
    else:
        raise TypeError(f"不支持的图像输入类型: {type(image_input)}")

def load_model():
    """加载设置中指定的SentenceTransformer模型。如果AI功能被禁用，返回None。"""
    global model
    
    # 检查AI功能是否启用
    if not settings.AI_ENABLED:
        print("AI功能已在配置中禁用，不加载模型")
        return None
        
    if model is None:
        print(f"正在加载模型: {settings.MODEL_PATH}")
        try:
            model = SentenceTransformer(
                settings.MODEL_PATH,
                trust_remote_code=settings.TRUST_REMOTE_CODE
            )
            print("模型加载成功。")
        except Exception as e:
            print(f"加载模型时出错: {e}")
            # 适当处理错误，可能抛出异常或退出
            raise

def get_model() -> SentenceTransformer:
    """返回加载的模型实例，如果需要就加载模型。如果AI功能被禁用，抛出异常。"""
    # 检查AI功能是否启用
    if not settings.AI_ENABLED:
        raise RuntimeError("AI功能已在配置中禁用")
        
    if model is None:
        load_model()
    if model is None: # 再次检查，以防加载失败
        raise RuntimeError("模型无法加载。")
    return model

def encode_text(text: Union[str, List[str]], cache_dir=None) -> np.ndarray:
    """将文本或文本列表编码成向量。"""
    if not settings.USE_CACHE:
        # 如果禁用缓存，直接计算向量
        model_instance = get_model()
        return model_instance.encode(text, normalize_embeddings=True)
    
    # 使用缓存
    cache_dir = cache_dir or settings.TEXT_VECTOR_CACHE_DIR
    
    # 先尝试从缓存获取
    cache_key = get_text_cache_key(text)
    cache_instance = diskcache.Cache(directory=cache_dir)
    
    embeddings = cache_instance.get(cache_key)
    if embeddings is not None:
        print(f"文本向量从缓存获取: {cache_key}")
        return embeddings
    
    # 缓存未命中，计算向量
    model_instance = get_model()
    embeddings = model_instance.encode(text, normalize_embeddings=True)
    
    cache_instance.set(cache_key, embeddings)
    
    return embeddings

def encode_image(image_input: Union[Image.Image, List[Image.Image], str, List[str]], cache_dir=None) -> np.ndarray:
    """将图像(PIL Image、路径)或图像列表编码成向量。"""
    if not settings.USE_CACHE:
        # 如果禁用缓存，直接计算向量
        model_instance = get_model()
        if isinstance(image_input, (Image.Image, str)):
            images_to_encode = [image_input]
            embeddings = model_instance.encode(images_to_encode, normalize_embeddings=True)
            return embeddings[0]
        else:
            return model_instance.encode(image_input, normalize_embeddings=True)
    
    # 使用缓存
    cache_dir = cache_dir or settings.IMAGE_VECTOR_CACHE_DIR
    
    # 先尝试从缓存获取
    try:
        cache_key = get_image_cache_key(image_input)
        cache_instance = diskcache.Cache(directory=cache_dir)
        
        embeddings = cache_instance.get(cache_key)
        if embeddings is not None:
            return embeddings

    except Exception as e:
        print(f"获取图像缓存时出错: {e}")
    
    # 缓存未命中，计算向量
    model_instance = get_model()
    # 处理单个PIL图像或路径
    if isinstance(image_input, (Image.Image, str)):
        images_to_encode = [image_input]
    else:
        images_to_encode = image_input

    embeddings = model_instance.encode(images_to_encode, normalize_embeddings=True)

    # 尝试缓存结果
    try:
        if isinstance(image_input, (Image.Image, str)):
            # 单个向量情况，缓存结果
            cache_instance.set(cache_key, embeddings[0])
        else:
            cache_instance.set(cache_key, embeddings)
    except Exception as e:
        print(f"缓存图像向量时出错: {e}")
        # 忽略缓存错误，仍然返回计算的向量

    # 如果输入是单个对象，返回单个向量
    if isinstance(image_input, (Image.Image, str)):
        return embeddings[0]
    return embeddings

from sentence_transformers import SentenceTransformer
from PIL import Image
import numpy as np
from typing import List, Union, Dict, Any
import os
import hashlib

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

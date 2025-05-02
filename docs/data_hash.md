# SmartImageFinder 文件哈希计算

## 概述

文件哈希计算是 SmartImageFinder 系统的重要组件，用于生成图片文件的唯一标识符，支持重复检测、缓存键生成以及文件完整性验证。本文档详述了哈希计算的策略、实现方法和应用场景。

## 哈希计算策略

系统采用两种哈希计算策略，根据不同场景和性能需求灵活选择：

### 文本哈希计算

用于处理文本内容或元数据的哈希计算：

```python
import hashlib

def get_text_hash(text: str) -> str:
    """
    计算文本内容的SHA-256哈希值
    
    参数:
        text: 需要计算哈希值的文本字符串
        
    返回:
        文本内容的16进制哈希值字符串
    """
    if not text:
        return ""
    
    # 使用utf-8编码将文本转换为字节，然后计算SHA-256哈希值
    hash_obj = hashlib.sha256(text.encode('utf-8'))
    return hash_obj.hexdigest()
```

### 图片文件哈希计算

针对图片文件的高效哈希计算方式：

```python
import os
import hashlib

def get_image_hash(image_path: str) -> str:
    """
    计算图片文件的部分内容哈希值，用于快速识别
    
    通过读取文件的前8K和后8K内容生成哈希值，对于小于16K的文件直接读取全部内容
    
    参数:
        image_path: 图片文件的路径
        
    返回:
        图片文件的16进制哈希值字符串
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"文件不存在: {image_path}")
    
    hash_obj = hashlib.sha256()
    file_size = os.path.getsize(image_path)
    
    with open(image_path, 'rb') as f:
        # 如果文件小于16K，直接读取全部内容
        if file_size <= 16 * 1024:
            hash_obj.update(f.read())
        else:
            # 读取前8K
            front_chunk = f.read(8 * 1024)
            hash_obj.update(front_chunk)
            
            # 移动到文件末尾前8K的位置
            f.seek(-8 * 1024, os.SEEK_END)
            
            # 读取后8K
            rear_chunk = f.read(8 * 1024)
            hash_obj.update(rear_chunk)
    
    return hash_obj.hexdigest()
```

## 性能考量

- **文本哈希**：对于短文本，SHA-256 提供了良好的安全性和性能平衡
- **图片哈希**：通过仅读取文件首尾部分内容，大幅提高了处理大型图片文件的速度
  - 前8K和后8K内容通常包含文件格式信息和元数据
  - 对于大多数图片而言，这种方法能有效区分不同文件
  - 与完整文件哈希相比，性能提升显著，特别是对于GB级别的图片集合

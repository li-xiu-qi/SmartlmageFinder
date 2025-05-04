# SmartImageFinder 配置指南

## 概述

SmartImageFinder系统采用灵活的配置管理机制，所有配置项集中存储在YAML文件中，便于维护和修改。配置系统支持热加载、自动目录创建和配置项覆盖等特性，为系统提供了高度的可配置性。

## 配置文件位置

系统默认配置文件位置：`backend/config/config.yaml`

如果配置文件不存在，系统会在首次运行时自动创建默认配置文件。

## 主要配置项

### 模型相关配置

- **MODEL_PATH**: CLIP模型路径，用于向量编码
- **VECTOR_DIM**: 向量维度，默认为1024
- **VISION_MODEL**: 当前使用的视觉模型，如"Qwen/Qwen2.5-VL-32B-Instruct"
- **AVAILABLE_VISION_MODELS**: 可用视觉模型列表

### 存储相关配置

- **UPLOAD_DIR**: 上传图片存储目录
- **DB_PATH**: SQLite数据库路径
- **TITLE_INDEX_PATH**: 标题向量索引文件路径
- **DESCRIPTION_INDEX_PATH**: 描述向量索引文件路径
- **IMAGE_INDEX_PATH**: 图像向量索引文件路径
- **UUID_MAP_PATH**: UUID映射文件路径

### 缓存配置

- **TEXT_VECTOR_CACHE_DIR**: 文本向量缓存目录
- **IMAGE_VECTOR_CACHE_DIR**: 图像向量缓存目录
- **USE_CACHE**: 是否启用缓存功能，布尔值
- **MAX_CACHE_SIZE_GB**: 最大缓存大小，单位为GB

### API配置

- **OPENAI_API_KEY**: OpenAI API密钥
- **OPENAI_API_BASE**: OpenAI API基础URL
- **AI_ENABLED**: 是否启用AI功能，布尔值

### 服务器配置

- **HOST**: 服务器主机地址
- **PORT**: 服务器端口号

## 配置系统特性

### 单例模式

配置系统采用单例设计模式，确保整个应用中只有一个配置实例，避免冲突和重复加载。

### 自动目录创建

系统会自动检查并创建所有必要的目录结构，确保数据存储、索引和缓存目录都可用。

### 配置重载

支持在运行时重新加载配置，无需重启应用即可应用新的配置项。

```python
from backend.config import settings

# 重新加载配置
settings.reload()
```

### 配置修改与保存

提供API动态修改配置并保存到配置文件：

```python
from backend.config import settings

# 修改单个配置项
settings.set("MAX_CACHE_SIZE_GB", 2.0, auto_save=True)

# 批量修改配置
settings.update({
    "OPENAI_API_KEY": "your_new_api_key",
    "AI_ENABLED": True
}, auto_save=True)
```

## 使用示例

### 获取配置项

```python
from backend.config import settings

# 获取单个配置项
api_key = settings.get("OPENAI_API_KEY")

# 获取配置项并提供默认值
cache_size = settings.get("MAX_CACHE_SIZE_GB", 1.0)

# 直接访问配置属性
upload_dir = settings.UPLOAD_DIR
```

### 修改配置

```python
from backend.config import settings

# 直接修改配置属性
settings.VECTOR_DIM = 1024

# 使用set方法修改配置（可选自动保存）
settings.set("VECTOR_DIM", 1024, auto_save=True)

# 批量更新配置
settings.update({
    "USE_CACHE": True,
    "MAX_CACHE_SIZE_GB": 2.0
})

# 保存配置到文件
settings.save()
```

### 重置配置

```python
from backend.config import settings

# 重置为默认配置
settings.reset_to_default(auto_save=True)
```

## 配置文件示例

```yaml
AI_ENABLED: true
AVAILABLE_VISION_MODELS:
- Qwen/Qwen2.5-VL-32B-Instruct
- openai/gpt-4-vision-preview
DB_PATH: ./data/db/smartimagefinder.db
DESCRIPTION_INDEX_PATH: ./data/faiss/description_vectors.faiss
HOST: 0.0.0.0
IMAGE_INDEX_PATH: ./data/faiss/image_vectors.faiss
IMAGE_VECTOR_CACHE_DIR: ./data/caches/image_vector_cache
MAX_CACHE_SIZE_GB: 1.5
MODEL_PATH: ./models/jina-clip-v2
OPENAI_API_BASE: https://api.openai.com/v1
OPENAI_API_KEY: ''
PORT: 8000
TEXT_VECTOR_CACHE_DIR: ./data/caches/text_vector_cache
TITLE_INDEX_PATH: ./data/faiss/title_vectors.faiss
UPLOAD_DIR: ./data/images
USE_CACHE: true
UUID_MAP_PATH: ./data/faiss/uuid_map.pickle
VECTOR_DIM: 1024
VISION_MODEL: Qwen/Qwen2.5-VL-32B-Instruct
```

## 注意事项

1. **敏感信息**: API密钥等敏感信息不要提交到版本控制系统
2. **配置备份**: 建议定期备份配置文件
3. **权限设置**: 确保配置文件具有适当的访问权限

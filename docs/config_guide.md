# SmartImageFinder 配置指南

## 概述

SmartImageFinder系统采用灵活的配置管理机制，所有配置项集中存储在YAML文件中，便于维护和修改。配置系统使用Pydantic进行配置验证，支持热加载、自动目录创建和配置项覆盖等特性，为系统提供了高度的可配置性。

## 配置文件位置

系统默认配置文件位置：`backend/config_files/config.yaml`

如果配置文件不存在，系统会在首次运行时自动创建默认配置文件，前提是必要的配置项（如MODEL_PATH）已设置。

## 主要配置项

### 模型相关配置

- **MODEL_PATH**: CLIP模型路径，用于向量编码（必需配置，无默认值）
- **EMBEDDING_DIMENSION**: 向量维度，默认为1024
- **VISION_MODEL**: 当前使用的视觉模型，如"Qwen/Qwen2.5-VL-32B-Instruct"
- **AVAILABLE_VISION_MODELS**: 可用视觉模型列表

### 存储相关配置

- **UPLOAD_DIR**: 上传图片存储目录，默认为"./data/images"
- **DB_PATH**: SQLite数据库路径，默认为"./data/db/smartimagefinder.db"
- **TEMP_FILES_DIR**: 临时文件存储目录，用于处理上传的临时文件
- **VECTOR_DB_DRIVER**: 向量数据库驱动文件路径，用于加载自定义的向量数据库实现

### 缓存配置

- **TEXT_VECTOR_CACHE_DIR**: 文本向量缓存目录，默认为"./data/caches/text_vector_cache"
- **IMAGE_VECTOR_CACHE_DIR**: 图像向量缓存目录，默认为"./data/caches/image_vector_cache"
- **USE_CACHE**: 是否启用缓存功能，布尔值，默认为true
- **MAX_CACHE_SIZE_GB**: 最大缓存大小，单位为GB，默认为1.5

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

支持在运行时重新加载配置，无需重启应用即可应用新的配置项。重载过程会自动验证配置，确保所有必需参数都有有效值。

```python
from backend.config import settings

# 重新加载配置
success = settings.reload()
if success:
    print("配置已成功重载")
else:
    print("配置重载失败，将使用默认值")
```

### 配置修改与保存

提供API动态修改配置并保存到配置文件。所有更新都会通过Pydantic验证，确保配置的一致性和有效性。

```python
from backend.config import settings

# 获取当前配置对象，并直接修改属性
config = settings.get_config()
config.MAX_CACHE_SIZE_GB = 2.0

# 批量更新配置并自动保存
settings.update_config({
    "OPENAI_API_KEY": "your_new_api_key",
    "AI_ENABLED": True,
    "MAX_CACHE_SIZE_GB": 2.0
}, auto_save=True)
```

## 使用示例

### 获取配置项

```python
from backend.config import settings

# 获取完整配置对象
config = settings.get_config()

# 通过配置对象访问各项配置
api_key = config.OPENAI_API_KEY
cache_size = config.MAX_CACHE_SIZE_GB
upload_dir = config.UPLOAD_DIR

# 检查可选配置项是否已设置
if config.VISION_MODEL:
    print(f"当前使用的视觉模型: {config.VISION_MODEL}")
```

### 修改配置

```python
from backend.config import settings

# 获取配置对象并修改
config = settings.get_config()
config.EMBEDDING_DIMENSION = 1024  # 注意: 在新版本中是EMBEDDING_DIMENSION而非VECTOR_DIM

# 批量更新配置
settings.update_config({
    "USE_CACHE": True,
    "MAX_CACHE_SIZE_GB": 2.0
})

# 保存配置到文件
settings.save()
```

### 创建必要目录

```python
from backend.config import settings
from backend.config import ensure_directories_exist

# 系统在加载配置后会自动创建必要的目录
# 也可以手动触发目录创建
config = settings.get_config()
ensure_directories_exist(
    file_paths=[config.DB_PATH],
    dir_paths=[config.UPLOAD_DIR, config.TEXT_VECTOR_CACHE_DIR, config.IMAGE_VECTOR_CACHE_DIR]
)
```

## 配置文件示例

下面是一个实际的配置文件示例，展示了系统当前使用的配置项：

```yaml
AVAILABLE_VISION_MODELS:
- Qwen/Qwen2.5-VL-32B-Instruct
- Pro/Qwen/Qwen2.5-VL-7B-Instruct
DB_PATH: ./data/db/smartimagefinder.db
HOST: 0.0.0.0
PORT: 1000
IMAGE_VECTOR_CACHE_DIR: ./data/caches/image_vector_cache
TEXT_VECTOR_CACHE_DIR: ./data/caches/text_vector_cache
MAX_CACHE_SIZE_GB: 1.5
MODEL_PATH: C:\Users\k\Desktop\BaiduSyncdisk\baidu_sync_documents\hf_models\jina-clip-v2
EMBEDDING_DIMENSION: 1024
OPENAI_API_BASE: https://api.siliconflow.cn/v1
OPENAI_API_KEY: sk-**********
TEMP_FILES_DIR: ./data/temp_files
UPLOAD_DIR: ./data/images
USE_CACHE: true
VISION_MODEL: Qwen/Qwen2.5-VL-32B-Instruct
VECTOR_DB_DRIVER: ./backend/config_files/vector_db_driver/vec0.dll
```

> **安全提示**：实际配置文件中的API密钥已部分隐藏，您应该使用您自己的API密钥。

## Pydantic 配置验证

系统使用 Pydantic 进行配置验证，配置模型定义如下：

```python
class AppConfig(BaseModel):
    MODEL_PATH: str  # 不提供默认值，必须在 config.yaml 中提供或通过更新设置
    VECTOR_DB_DRIVER: Optional[str] = None
    EMBEDDING_DIMENSION: Optional[int] = None
    UPLOAD_DIR: str = "./data/images"
    DB_PATH: str = "./data/db/smartimagefinder.db"
    TEXT_VECTOR_CACHE_DIR: str = "./data/caches/text_vector_cache"
    IMAGE_VECTOR_CACHE_DIR: str = "./data/caches/image_vector_cache"
    USE_CACHE: bool = True
    MAX_CACHE_SIZE_GB: float = 1.5
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_API_BASE: Optional[str] = None
    VISION_MODEL: Optional[str] = None
    AVAILABLE_VISION_MODELS: List[str] = Field(
        default_factory=lambda: [
            "Qwen/Qwen2.5-VL-32B-Instruct",
            "Pro/Qwen/Qwen2.5-VL-7B-Instruct",
        ]
    )
    AI_ENABLED: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 1000
```

Pydantic 提供了以下好处：

1. **类型验证**: 确保配置项的值具有正确的数据类型
2. **默认值**: 为可选配置项提供合理的默认值
3. **数据转换**: 自动将YAML中的值转换为正确的Python类型
4. **错误处理**: 提供详细的验证错误信息

## 注意事项

1. **敏感信息**: API密钥等敏感信息不要提交到版本控制系统，可以使用环境变量覆盖或使用配置模板
2. **配置备份**: 建议定期备份配置文件，特别是在修改重要配置项之前
3. **权限设置**: 确保配置文件具有适当的访问权限，特别是包含API密钥等敏感信息时
4. **MODEL_PATH必需**: MODEL_PATH是必需的配置项，没有默认值。如果未设置，某些操作（如自动保存配置）可能会被阻止
5. **路径格式**: 目录路径可以使用相对路径（相对于应用根目录）或绝对路径
6. **自动目录创建**: 系统会自动创建配置中指定的必要目录，无需手动创建

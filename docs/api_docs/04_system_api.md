# 系统管理 API 文档

## 概述

SmartImageFinder 提供了一系列系统管理API，用于监控系统状态、管理配置、清理缓存和获取系统信息。这些API主要供管理员和系统维护人员使用，可以帮助管理员了解系统运行状况并进行必要的维护操作。

## API 端点

### 1. 获取系统状态

获取完整的系统状态信息，包括系统基本信息、组件状态、存储信息和缓存信息等。

**请求**:

- **方法**: GET
- **URL**: `/api/system/status`

**成功响应**:

```json
{
  "status": "success",
  "code": 200,
  "message": "获取系统状态成功",
  "data": {
    "system": {
      "version": "1.0.0",
      "uptime": 86400,
      "status": "healthy",
      "platform": "Windows",
      "python_version": "3.10.4"
    },
    "components": {
      "database": {
        "status": "connected",
        "type": "sqlite",
        "path": "C:/Users/user/SmartImageFinder/data/images.db"
      },
      "vector_db_driver": {
        "status": "available",
        "path": "C:/Users/user/SmartImageFinder/config_files/vector_db_driver/vec0.dll",
        "error": null
      },
      "multimodal_api": {
        "status": "enabled",
        "model": "gpt-4-vision-preview",
        "available_models": ["gpt-4-vision-preview", "gpt-4o"],
        "api_base": "https://api.openai.com/v1"
      }
    },
    "storage": {
      "total_images": 1250,
      "total_size_mb": 4500.75,
      "total_tags": 312,
      "upload_dir": "C:/Users/user/SmartImageFinder/uploads"
    },
    "cache": {
      "enabled": true,
      "max_size_gb": 2.0,
      "text_vector_cache": {
        "path": "C:/Users/user/SmartImageFinder/cache/text_vector_cache",
        "entries": 823,
        "size_mb": 56.4
      },
      "image_vector_cache": {
        "path": "C:/Users/user/SmartImageFinder/cache/image_vector_cache",
        "entries": 1154,
        "size_mb": 187.2
      }
    },
    "models": {
      "embedding_model": "C:/Users/user/SmartImageFinder/models/all-MiniLM-L6-v2"
    },
    "server": {
      "host": "0.0.0.0",
      "port": 8000
    }
  },
  "metadata": {},
  "error": null,
  "timestamp": "2025-05-16T10:30:45.123456",
  "request_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### 2. 获取系统配置

获取当前系统配置信息，主要包括API配置、存储配置、模型配置和向量数据库配置。

**请求**:

- **方法**: GET
- **URL**: `/api/system/config`

**成功响应**:

```json
{
  "status": "success",
  "code": 200,
  "message": "获取系统配置成功",
  "data": {
    "api": {
      "apiKey": "sk-*********************",
      "baseUrl": "https://api.openai.com/v1"
    },
    "storage": {
      "rootDirectory": "C:/Users/user/SmartImageFinder/uploads",
      "cacheDirectory": "C:/Users/user/SmartImageFinder/cache",
      "maxCacheSize": 2.0
    },
    "model": {
      "vectorModel": "all-MiniLM-L6-v2",
      "visionModel": "gpt-4-vision-preview"
    },
    "vectorDb": {
      "driverPath": "C:/Users/user/SmartImageFinder/config_files/vector_db_driver/vec0.dll"
    }
  },
  "metadata": {},
  "error": null,
  "timestamp": "2025-05-16T10:31:45.123456",
  "request_id": "550e8400-e29b-41d4-a716-446655440001"
}
```

### 3. 更新系统配置

更新系统配置，可以修改API密钥、存储路径、模型配置等。

**请求**:

- **方法**: POST
- **URL**: `/api/system/update-config`
- **内容类型**: `application/json`
- **请求体**:

```json
{
  "api": {
    "apiKey": "sk-new-api-key",
    "baseUrl": "https://api.openai.com/v1"
  },
  "storage": {
    "rootDirectory": "D:/new-uploads",
    "cacheDirectory": "D:/new-cache",
    "maxCacheSize": 3.0
  },
  "model": {
    "vectorModel": "all-MiniLM-L6-v2",
    "visionModel": "gpt-4o"
  },
  "vectorDb": {
    "driverPath": "D:/new-path/vec0.dll"
  }
}
```

**成功响应**:

```json
{
  "status": "success",
  "code": 200,
  "message": "更新系统配置成功",
  "data": {
    "message": "配置已更新并保存到文件"
  },
  "metadata": {},
  "error": null,
  "timestamp": "2025-05-16T10:32:45.123456",
  "request_id": "550e8400-e29b-41d4-a716-446655440002"
}
```

**错误响应**:

```json
{
  "status": "error",
  "code": 400,
  "message": "配置更新失败",
  "data": null,
  "error": {
    "code": "CONFIG_UPDATE_ERROR",
    "message": "配置更新失败，无法写入配置文件",
    "details": null
  },
  "metadata": {},
  "timestamp": "2025-05-16T10:33:45.123456",
  "request_id": "550e8400-e29b-41d4-a716-446655440003"
}
```

### 4. 获取缓存统计信息

获取系统缓存的详细统计信息，包括文本向量缓存和图像向量缓存的条目数和大小。

**请求**:

- **方法**: GET
- **URL**: `/api/system/cache-stats`

**成功响应**:

```json
{
  "status": "success",
  "code": 200,
  "message": "获取缓存统计信息成功",
  "data": {
    "text_vector_cache": {
      "entries": 823,
      "size_mb": 56.4
    },
    "image_vector_cache": {
      "entries": 1154,
      "size_mb": 187.2
    }
  },
  "metadata": {},
  "error": null,
  "timestamp": "2025-05-16T10:34:45.123456",
  "request_id": "550e8400-e29b-41d4-a716-446655440004"
}
```

### 5. 清除系统缓存

清除系统的文本向量缓存和图像向量缓存。

**请求**:

- **方法**: POST
- **URL**: `/api/system/clear-cache`

**成功响应**:

```json
{
  "status": "success",
  "code": 200,
  "message": "清除缓存成功",
  "data": {
    "text_vector_cache": {
      "cleared": true,
      "entries_removed": 823,
      "size_freed_mb": 56.4,
      "error": null
    },
    "image_vector_cache": {
      "cleared": true,
      "entries_removed": 1154,
      "size_freed_mb": 187.2,
      "error": null
    }
  },
  "metadata": {},
  "error": null,
  "timestamp": "2025-05-16T10:35:45.123456",
  "request_id": "550e8400-e29b-41d4-a716-446655440005"
}
```

## 数据模型

### 系统状态模型

系统状态信息由多个子模型组成，包括：

#### SystemInfo（系统信息）

| 字段 | 类型 | 说明 |
|------|------|------|
| version | string | 系统版本号 |
| uptime | integer | 系统运行时间(秒) |
| status | string | 系统健康状态 |
| platform | string | 操作系统平台 |
| python_version | string | Python版本 |

#### ComponentsStatus（组件状态）

| 字段 | 类型 | 说明 |
|------|------|------|
| database | object | 数据库状态信息 |
| vector_db_driver | object | 向量数据库驱动状态 |
| multimodal_api | object | 多模态API状态 |

#### VectorDbDriverStatus（向量数据库驱动状态）

| 字段 | 类型 | 说明 |
|------|------|------|
| status | string | 状态(available/missing/error) |
| path | string | 驱动路径 |
| error | string | 错误信息(如果有) |

#### StorageInfo（存储信息）

| 字段 | 类型 | 说明 |
|------|------|------|
| total_images | integer | 总图片数量 |
| total_size_mb | float | 总大小(MB) |
| total_tags | integer | 总标签数量 |
| upload_dir | string | 上传目录路径 |

#### CacheInfo（缓存信息）

| 字段 | 类型 | 说明 |
|------|------|------|
| enabled | boolean | 是否启用缓存 |
| max_size_gb | float | 最大缓存大小(GB) |
| text_vector_cache | object | 文本向量缓存信息 |
| image_vector_cache | object | 图像向量缓存信息 |

### 缓存统计模型

#### CacheStats（缓存统计信息）

| 字段 | 类型 | 说明 |
|------|------|------|
| entries | integer | 缓存条目数量 |
| size_mb | float | 缓存大小(MB) |

#### CacheClearResult（缓存清除结果）

| 字段 | 类型 | 说明 |
|------|------|------|
| cleared | boolean | 是否成功清除 |
| entries_removed | integer | 移除的条目数 |
| size_freed_mb | float | 释放的空间大小(MB) |
| error | string | 错误信息(如果有) |

### 系统配置模型

#### FrontendConfig（前端所需的系统配置）

| 字段 | 类型 | 说明 |
|------|------|------|
| api | object | API配置 |
| storage | object | 存储配置 |
| model | object | 模型配置 |
| vectorDb | object | 向量数据库配置 |

#### ApiConfig（API配置）

| 字段 | 类型 | 说明 |
|------|------|------|
| apiKey | string | OpenAI API密钥(部分隐藏) |
| baseUrl | string | OpenAI API基础URL |

#### StorageConfig（存储配置）

| 字段 | 类型 | 说明 |
|------|------|------|
| rootDirectory | string | 上传根目录 |
| cacheDirectory | string | 缓存目录 |
| maxCacheSize | float | 最大缓存大小(GB) |

#### ModelConfig（模型配置）

| 字段 | 类型 | 说明 |
|------|------|------|
| vectorModel | string | 向量模型名称 |
| visionModel | string | 视觉模型名称 |

## 错误代码

| 错误代码 | 说明 |
|----------|------|
| CONFIG_UPDATE_ERROR | 配置更新失败 |
| CACHE_CLEAR_ERROR | 缓存清除失败 |
| SYSTEM_STATUS_ERROR | 获取系统状态失败 |

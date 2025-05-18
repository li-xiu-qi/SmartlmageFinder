# 系统管理 API 文档

## 概述

SmartImageFinder 提供了一系列系统管理API，用于监控系统状态、管理配置和清理缓存。这些API主要供管理员和系统维护人员使用，可以帮助管理员了解系统运行状况并进行必要的维护操作。

## API 端点

### 系统状态相关接口

#### 1. 获取基本系统信息

获取基本系统信息，不包括数据库和缓存等详细信息。适用于仅需了解系统运行状态的场景。

**请求**:

- **方法**: GET
- **URL**: `/api/v1/system/info`

**成功响应**:

```json
{
  "status": "success",
  "code": 200,
  "message": "获取系统信息成功",
  "data": {
    "version": "1.0.0",
    "app_uptime": 3600,
    "app_uptime_formatted": "1小时 0分钟 0秒",
    "status": "healthy",
    "platform": "Windows",
    "python_version": "3.10.4"
  },
  "metadata": {},
  "error": null,
  "timestamp": "2025-05-18T10:28:45.123456",
  "request_id": "550e8400-e29b-41d4-a716-446655440010"
}
```

#### 2. 获取系统运行时间信息

获取系统当前运行时间信息，可用于监控系统是否正常运行。此接口适合高频调用（如每秒一次）来验证系统响应状态。

**请求**:

- **方法**: GET
- **URL**: `/api/v1/system/runtime`

**成功响应**:

```json
{
  "status": "success",
  "code": 200,
  "message": "获取运行时间信息成功",
  "data": {
    "app_uptime_formatted": "1天 0小时 0分钟 0秒",
    "current_time": "2025-05-18T10:36:45.123456"
  },
  "metadata": {},
  "error": null,
  "timestamp": "2025-05-18T10:36:45.123456",
  "request_id": "550e8400-e29b-41d4-a716-446655440006"
}
```

### 数据库状态相关接口

#### 1. 获取数据库状态信息

获取完整的数据库状态信息，包括连接状态、版本、表信息等。

**请求**:

- **方法**: GET
- **URL**: `/api/v1/system/database`

**成功响应**:

```json
{
  "status": "success",
  "code": 200,
  "message": "获取数据库状态成功",
  "data": {
    "status": "connected",
    "type": "sqlite",
    "path": "C:/Users/user/SmartImageFinder/data/db/smartimagefinder.db",
    "image_count": 1250,
    "total_size": 4718592000,
    "tag_count": 312,
    "vector_status": true,
    "db_version": "3.39.4",
    "tables_info": {
      "images": 1250,
      "tags": 312,
      "image_tags": 4560
    },
    "error": null
  },
  "metadata": {},
  "error": null,
  "timestamp": "2025-05-18T10:37:45.123456",
  "request_id": "550e8400-e29b-41d4-a716-446655440007"
}
```

#### 2. 获取存储信息

获取存储相关统计信息，包括图像总数、总大小和标签信息。

**请求**:

- **方法**: GET
- **URL**: `/api/v1/system/storage`

**成功响应**:

```json
{
  "status": "success",
  "code": 200,
  "message": "获取存储信息成功",
  "data": {
    "total_images": 1250,
    "total_size_mb": 4500.75,
    "total_tags": 312,
    "upload_dir": "C:/Users/user/SmartImageFinder/data/images"
  },
  "metadata": {},
  "error": null,
  "timestamp": "2025-05-18T10:38:45.123456",
  "request_id": "550e8400-e29b-41d4-a716-446655440008"
}
```

### 缓存相关接口

#### 1. 获取缓存统计信息

获取系统缓存的统计信息，包括文本和图像向量缓存的条目数和大小。

**请求**:

- **方法**: GET
- **URL**: `/api/v1/system/cache`

**成功响应**:

```json
{
  "status": "success",
  "code": 200,
  "message": "获取缓存统计信息成功",
  "data": {
    "enabled": true,
    "max_size_gb": 2.0,
    "total_entries": 1977,
    "total_size_mb": 243.6,
    "text_vector_cache": {
      "path": "C:/Users/user/SmartImageFinder/data/caches/text_vector_cache",
      "entries": 823,
      "size_mb": 56.4
    },
    "image_vector_cache": {
      "path": "C:/Users/user/SmartImageFinder/data/caches/image_vector_cache",
      "entries": 1154,
      "size_mb": 187.2
    }
  },
  "metadata": {},
  "error": null,
  "timestamp": "2025-05-18T10:39:45.123456",
  "request_id": "550e8400-e29b-41d4-a716-446655440009"
}
```

#### 2. 清除系统缓存

清除系统的文本向量缓存和图像向量缓存。

**请求**:

- **方法**: POST
- **URL**: `/api/v1/system/cache/clear`
- **查询参数**:
  - `text_cache`: 布尔值，是否清除文本缓存，默认为true
  - `image_cache`: 布尔值，是否清除图像缓存，默认为true

**请求示例**:

```
POST /api/v1/system/cache/clear?text_cache=true&image_cache=true
```

**成功响应**:

```json
{
  "status": "success",
  "code": 200,
  "message": "清除缓存成功",
  "data": {
    "cleared": true,
    "text_cache_entries_removed": 823,
    "image_cache_entries_removed": 1154,
    "total_size_freed_mb": 243.6
  },
  "metadata": {},
  "error": null,
  "timestamp": "2025-05-18T10:40:45.123456",
  "request_id": "550e8400-e29b-41d4-a716-446655440005"
}
```

### 配置相关接口

#### 1. 获取系统配置

获取当前系统配置信息，主要包括API配置、存储配置、模型配置和向量数据库配置。

**请求**:

- **方法**: GET
- **URL**: `/api/v1/system/config`

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
      "rootDirectory": "C:/Users/user/SmartImageFinder/data/images",
      "cacheDirectory": "C:/Users/user/SmartImageFinder/data/caches",
      "maxCacheSize": 2.0
    },
    "model": {
      "vectorModel": "all-MiniLM-L6-v2",
      "visionModel": "gpt-4-vision-preview"
    },
    "vectorDb": {
      "driverPath": "C:/Users/user/SmartImageFinder/backend/tests/vec0.dll"
    }
  },
  "metadata": {},
  "error": null,
  "timestamp": "2025-05-18T10:31:45.123456",
  "request_id": "550e8400-e29b-41d4-a716-446655440001"
}
```

#### 2. 更新系统配置

更新系统配置，可以修改API密钥、存储路径、模型配置等。

**请求**:

- **方法**: POST
- **URL**: `/api/v1/system/config/update`
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
  "timestamp": "2025-05-18T10:32:45.123456",
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
    "message": "配置更新失败，无法写入配置文件"
  },
  "metadata": {},
  "timestamp": "2025-05-18T10:33:45.123456",
  "request_id": "550e8400-e29b-41d4-a716-446655440003"
}
```

# 系统管理 API

## 简介

系统管理API提供了一系列接口，用于获取和管理SmartImageFinder系统的状态、配置和资源。这些API主要用于系统管理员和开发人员监控系统运行状况、查看资源使用情况以及更新系统配置。

## 接口详情

### 获取基本系统信息

**请求方式**: GET

**路径**: `/api/v1/system/info`

**说明**: 获取基本系统信息，不包括数据库和缓存等详细信息

#### 响应

```json
{
  "status": "success",
  "code": 200,
  "message": "操作成功",
  "data": {
    "version": "1.0.0",
    "app_uptime": 878415,
    "app_uptime_formatted": "10天 3小时 20分钟 15秒",
    "status": "healthy",
    "platform": "Windows",
    "python_version": "3.10.0"
  },
  "timestamp": "2023-05-19T12:34:56.789Z",
  "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

### 获取系统运行时信息

**请求方式**: GET

**路径**: `/api/v1/system/runtime`

**说明**: 获取系统运行时间和资源使用情况信息

#### 响应

```json
{
  "status": "success",
  "code": 200,
  "message": "操作成功",
  "data": {
    "app_uptime_formatted": "10天 3小时 20分钟 15秒",
    "current_time": "2023-05-19T12:34:56.789Z"
  },
  "timestamp": "2023-05-19T12:34:56.789Z",
  "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

### 获取数据库状态信息

**请求方式**: GET

**路径**: `/api/v1/system/database`

**说明**: 获取数据库状态和统计信息

#### 响应

```json
{
  "status": "success",
  "code": 200,
  "message": "操作成功",
  "data": {
    "status": "connected",
    "type": "sqlite",
    "path": "c:\\\\Users\\\\k\\\\Documents\\\\project\\\\programming_project\\\\python_project\\\\importance\\\\SmartImageFinder\\\\data\\\\db\\\\smartimagefinder.db",
    "image_count": 100,
    "total_size": 10485760, // 单位: 字节
    "tag_count": 50,
    "vector_status": true,
    "db_version": "3.39.4",
    "error": null
  },
  "timestamp": "2023-05-19T12:34:56.789Z",
  "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

### 获取存储状态信息

**请求方式**: GET

**路径**: `/api/v1/system/storage`

**说明**: 获取存储状态信息，包括图像和标签统计

#### 响应

```json
{
  "status": "success",
  "code": 200,
  "message": "操作成功",
  "data": {
    "total_images": 100,
    "total_size_mb": 10.00,
    "total_tags": 50,
    "upload_dir": "c:\\\\Users\\\\k\\\\Documents\\\\project\\\\programming_project\\\\python_project\\\\importance\\\\SmartImageFinder\\\\data\\\\images"
  },
  "timestamp": "2023-05-19T12:34:56.789Z",
  "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

### 获取缓存状态信息

**请求方式**: GET

**路径**: `/api/v1/system/cache`

**说明**: 获取缓存统计信息

#### 响应

```json
{
  "status": "success",
  "code": 200,
  "message": "操作成功",
  "data": {
    "enabled": true,
    "max_size_gb": 1.0,
    "total_entries": 120,
    "total_size_mb": 5.5,
    "text_vector_cache": {
      "path": "c:\\\\Users\\\\k\\\\Documents\\\\project\\\\programming_project\\\\python_project\\\\importance\\\\SmartImageFinder\\\\data\\\\caches\\\\text_vector_cache",
      "entries": 100,
      "size_mb": 5.0
    },
    "image_vector_cache": {
      "path": "c:\\\\Users\\\\k\\\\Documents\\\\project\\\\programming_project\\\\python_project\\\\importance\\\\SmartImageFinder\\\\data\\\\caches\\\\image_vector_cache",
      "entries": 20,
      "size_mb": 0.5
    }
  },
  "timestamp": "2023-05-19T12:34:56.789Z",
  "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

### 清除系统缓存

**请求方式**: POST

**路径**: `/api/v1/system/cache/clear`

**说明**: 清除系统缓存。此操作会清除所有文本和图像向量缓存。查询参数 `text_cache` 和 `image_cache` 控制响应中是否报告相应缓存类型的清除条目数，但不会阻止缓存被清除。`total_size_freed_mb` 始终反映所有缓存释放的总空间。

#### 查询参数

| 参数名 | 类型 | 必填 | 默认值 | 描述 |
|-------|------|------|-------|-----|
| text_cache | boolean | 否 | true | 是否清除文本缓存 |
| image_cache | boolean | 否 | true | 是否清除图像缓存 |

#### 响应

```json
{
  "status": "success",
  "code": 200,
  "message": "操作成功",
  "data": {
    "cleared": true,
    "text_cache_entries_removed": 100,
    "image_cache_entries_removed": 20,
    "total_size_freed_mb": 5.5
  },
  "timestamp": "2023-05-19T12:34:56.789Z",
  "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

### 获取系统配置

**请求方式**: GET

**路径**: `/api/v1/system/config`

**说明**: 获取系统配置信息

#### 响应

```json
{
  "status": "success",
  "code": 200,
  "message": "操作成功",
  "data": {
    "api": {
      "apiKey": "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
      "baseUrl": "https://api.openai.com/v1"
    },
    "storage": {
      "rootDirectory": "c:\\\\Users\\\\k\\\\Documents\\\\project\\\\programming_project\\\\python_project\\\\importance\\\\SmartImageFinder\\\\data\\\\images",
      "cacheDirectory": "c:\\\\Users\\\\k\\\\Documents\\\\project\\\\programming_project\\\\python_project\\\\importance\\\\SmartImageFinder\\\\data\\\\caches\\\\text_vector_cache",
      "maxCacheSize": 1.0
    },
    "model": {
      "vectorModel": "X:\\\\models\\\\bge-large-zh-v1.5",
      "visionModel": "gpt-4-vision-preview",
      "availableModels": ["gpt-4-vision-preview", "gemini-pro-vision"]
    },
    "vectorDb": {
      "driverPath": "c:\\\\Users\\\\k\\\\Documents\\\\project\\\\programming_project\\\\python_project\\\\importance\\\\SmartImageFinder\\\\backend\\\\config_files\\\\vector_db_driver\\\\vec.dll"
    }
  },
  "timestamp": "2023-05-19T12:34:56.789Z",
  "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

### 更新系统配置

**请求方式**: POST

**路径**: `/api/v1/system/config/update`

**说明**: 更新系统配置

#### 请求体

```json
{
  "storage": {
    "rootDirectory": "/new/path/to/uploads",
    "cacheDirectory": "/new/path/to/caches_base",
    "maxCacheSize": 20.0
  },
  "api": {
    "apiKey": "new-api-key",
    "baseUrl": "https://new.api.base/url"
  },
  "model": {
    "visionModel": "new-vision-model",
    "vectorModel": "/new/path/to/vector/model.bin"
  },
  "vectorDb": {
    "driverPath": "/new/path/to/driver.dll"
  }
}
```

> **注意**: 只需要包含要更新的配置字段，未提供的字段将保持不变。

#### 响应

```json
{
  "status": "success",
  "code": 200,
  "message": "操作成功",
  "data": {
    "message": "系统配置已更新"
  },
  "timestamp": "2023-05-19T12:34:56.789Z",
  "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

## 错误代码

| 错误代码 | HTTP状态码 | 描述 |
|---------|-----------|-----|
| CONFIG_UPDATE_ERROR | 400 | 配置更新错误 |
| DATABASE_ERROR | 500 | 数据库操作错误 |
| PERMISSION_DENIED | 403 | 权限不足 |
| INTERNAL_SERVER_ERROR | 500 | 内部服务器错误 |

## 最佳实践

1. 系统管理API主要用于管理和监控目的，应该限制只有管理员才能访问。

2. 定期检查系统状态信息可以帮助预防潜在问题，特别是存储空间和数据库状态。

3. 在系统负载较低的时间执行缓存清理操作，避免影响用户体验。

4. 更新系统配置时，应该只包含需要修改的字段，而不是整个配置对象，以避免意外覆盖其他设置。

5. 如果发现系统性能下降，可以通过查看数据库状态和缓存命中率等指标来诊断问题原因。

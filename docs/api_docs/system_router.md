# 系统管理 API

系统管理API提供系统状态、配置和缓存管理功能。

## 基础信息

- **Base URL**: `/api/v1/system`
- **Content-Type**: `application/json`

## 端点列表

### 1. 获取基本系统信息

GET `/api/v1/system/info`

获取基本系统信息，不包括数据库和缓存等详细信息。

#### 请求参数

无

#### 响应示例

**成功响应 (200)**
```json
{
  "status": "success",
  "code": 200,
  "message": "操作成功",
  "data": {
    "name": "SmartImageFinder",
    "version": "1.0.0",
    "description": "智能图片搜索和管理系统",
    "uptime": "2天3小时15分钟"
  },
  "error": null
}
```

### 2. 获取系统运行时间

GET `/api/v1/system/runtime`

获取系统运行时间信息。

#### 请求参数

无

#### 响应示例

**成功响应 (200)**
```json
{
  "status": "success",
  "code": 200,
  "message": "操作成功",
  "data": {
    "start_time": "2024-01-15T10:00:00",
    "uptime_seconds": 183000,
    "uptime_human": "2天3小时15分钟"
  },
  "error": null
}
```

### 3. 获取数据库状态

GET `/api/v1/system/database`

获取数据库状态信息。

#### 请求参数

无

#### 响应示例

**成功响应 (200)**
```json
{
  "status": "success",
  "code": 200,
  "message": "操作成功",
  "data": {
    "status": "healthy",
    "tables": [
      {
        "name": "images",
        "row_count": 1500,
        "size_mb": 15.5
      },
      {
        "name": "tags",
        "row_count": 250,
        "size_mb": 2.1
      }
    ],
    "total_size_mb": 17.6,
    "connection_status": "connected"
  },
  "error": null
}
```

### 4. 获取存储状态

GET `/api/v1/system/storage`

获取存储状态信息，包括图像和标签统计。

#### 请求参数

无

#### 响应示例

**成功响应 (200)**
```json
{
  "status": "success",
  "code": 200,
  "message": "操作成功",
  "data": {
    "total_images": 1500,
    "total_size_mb": 2048.5,
    "average_image_size_mb": 1.37,
    "total_tags": 250,
    "unique_tags": 85,
    "storage_path": "/uploads",
    "available_space_gb": 456.7,
    "used_space_gb": 2.05
  },
  "error": null
}
```

### 5. 获取缓存状态

GET `/api/v1/system/cache`

获取缓存统计信息。

#### 请求参数

无

#### 响应示例

**成功响应 (200)**
```json
{
  "status": "success",
  "code": 200,
  "message": "操作成功",
  "data": {
    "text_cache": {
      "size": 45,
      "max_size": 1000,
      "hit_rate": 0.85,
      "entries": 45
    },
    "image_cache": {
      "size": 12,
      "max_size": 100,
      "hit_rate": 0.92,
      "entries": 12
    },
    "total_cache_entries": 57,
    "total_cache_size_mb": 3.2
  },
  "error": null
}
```

### 6. 清除系统缓存

POST `/api/v1/system/cache/clear`

清除系统缓存。

#### 请求参数

| 参数 | 类型 | 必填 | 描述 | 示例 |
|---|---|---|---|---|
| text_cache | boolean | 否 | 是否清除文本缓存，默认为true | true |
| image_cache | boolean | 否 | 是否清除图像缓存，默认为true | true |

#### 响应示例

**成功响应 (200)**
```json
{
  "status": "success",
  "code": 200,
  "message": "操作成功",
  "data": {
    "cleared": true,
    "text_cache_entries_removed": 45,
    "image_cache_entries_removed": 12,
    "total_size_freed_mb": 3.2
  },
  "error": null
}
```

### 7. 获取系统配置

GET `/api/v1/system/config`

获取系统配置信息。

#### 请求参数

无

#### 响应示例

**成功响应 (200)**
```json
{
  "status": "success",
  "code": 200,
  "message": "操作成功",
  "data": {
    "upload_dir": "/uploads",
    "max_file_size": 10485760,
    "allowed_extensions": [".jpg", ".jpeg", ".png", ".webp"],
    "max_batch_upload": 100,
    "vector_model": "jina-clip-v2",
    "cache_config": {
      "text_cache_size": 1000,
      "image_cache_size": 100,
      "cache_ttl": 3600
    }
  },
  "error": null
}
```

### 8. 更新系统配置

POST `/api/v1/system/config/update`

更新系统配置。

#### 请求格式

`application/json`

#### 请求体

```json
{
  "max_file_size": 20971520,
  "allowed_extensions": [".jpg", ".jpeg", ".png", ".webp", ".gif"],
  "cache_config": {
    "text_cache_size": 2000
  }
}
```

#### 响应示例

**成功响应 (200)**
```json
{
  "status": "success",
  "code": 200,
  "message": "配置更新成功",
  "data": {
    "message": "配置已成功更新"
  },
  "error": null
}
```

**错误响应 (400)**
```json
{
  "status": "error",
  "code": 400,
  "message": "配置更新失败：无效的配置参数",
  "error": {
    "code": "CONFIG_UPDATE_ERROR",
    "message": "配置更新失败：无效的配置参数"
  }
}
```

### 9. 获取向量数据库驱动状态

GET `/api/v1/system/vector-driver`

获取向量数据库驱动状态信息。

#### 请求参数

无

#### 响应示例

**成功响应 (200)**
```json
{
  "status": "success",
  "code": 200,
  "message": "操作成功",
  "data": {
    "driver": "sqlite-vec",
    "version": "v0.1.1",
    "status": "loaded",
    "vector_dimensions": 512,
    "total_vectors": 1500,
    "index_size_mb": 7.8,
    "performance": {
      "average_query_time_ms": 45.2,
      "cache_hit_rate": 0.88
    }
  },
  "error": null
}
```

## 错误代码

| 错误代码 | 描述 | HTTP状态码 |
|---|---|---|
| CONFIG_UPDATE_ERROR | 配置更新失败 | 400 |

## 缓存类型说明

### 文本缓存
- 存储文本搜索的向量计算结果
- 最大容量：1000条记录
- TTL：3600秒

### 图像缓存
- 存储图像特征向量
- 最大容量：100条记录
- TTL：3600秒

## 监控建议

建议定期调用以下端点进行系统监控：

1. **系统健康检查**: `GET /api/v1/system/info`
2. **数据库状态**: `GET /api/v1/system/database`
3. **存储空间**: `GET /api/v1/system/storage`
4. **缓存状态**: `GET /api/v1/system/cache`
5. **向量数据库状态**: `GET /api/v1/system/vector-driver`

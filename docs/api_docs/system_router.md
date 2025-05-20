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
    "system": {
      "name": "SmartImageFinder",
      "version": "1.0.0",
      "environment": "production",
      "python_version": "3.10.6",
      "os": "Windows 11"
    },
    "features": {
      "ai_enabled": true,
      "vector_search_enabled": true,
      "advanced_filters_enabled": true
    },
    "api": {
      "version": "v1",
      "endpoints_count": 28
    }
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
    "uptime": {
      "days": 10,
      "hours": 5,
      "minutes": 30,
      "seconds": 15,
      "total_seconds": 878415
    },
    "resources": {
      "cpu_usage_percent": 25.4,
      "memory_usage_mb": 512.7,
      "memory_available_mb": 7680.3,
      "memory_percent": 6.3
    },
    "requests": {
      "total": 12500,
      "per_minute": 4.5,
      "average_response_time_ms": 150
    }
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
    "database_type": "SQLite",
    "version": "3.39.4",
    "file_size_mb": 256.5,
    "connection_pool": {
      "active_connections": 3,
      "idle_connections": 5,
      "max_connections": 20
    },
    "statistics": {
      "tables_count": 12,
      "indices_count": 28,
      "last_vacuum": "2023-05-15T00:00:00Z"
    },
    "performance": {
      "average_query_time_ms": 12.5,
      "slow_queries_count": 5
    }
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
    "images": {
      "total_count": 10000,
      "total_size_mb": 5120,
      "average_size_kb": 512,
      "by_month": [
        { "month": "2023-05", "count": 1250 },
        { "month": "2023-04", "count": 1300 },
        { "month": "2023-03", "count": 1150 }
      ]
    },
    "tags": {
      "unique_tags": 500,
      "most_used": [
        { "tag": "自然", "count": 1250 },
        { "tag": "风景", "count": 1100 },
        { "tag": "城市", "count": 950 }
      ]
    },
    "disk": {
      "total_gb": 500,
      "used_gb": 120,
      "available_gb": 380,
      "usage_percent": 24
    }
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
    "text_cache": {
      "items": 5000,
      "size_mb": 25.8,
      "hit_rate": 0.85,
      "miss_rate": 0.15
    },
    "image_cache": {
      "items": 1200,
      "size_mb": 450.5,
      "hit_rate": 0.78,
      "miss_rate": 0.22
    },
    "vector_cache": {
      "items": 8000,
      "size_mb": 120.3,
      "hit_rate": 0.92,
      "miss_rate": 0.08
    },
    "total": {
      "size_mb": 596.6,
      "hit_rate": 0.85
    }
  },
  "timestamp": "2023-05-19T12:34:56.789Z",
  "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

### 清除系统缓存

**请求方式**: POST

**路径**: `/api/v1/system/cache/clear`

**说明**: 清除系统缓存

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
    "text_cache_entries_removed": 5000,
    "image_cache_entries_removed": 1200,
    "total_size_freed_mb": 596.6
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
    "frontend": {
      "theme": "light",
      "language": "zh-CN",
      "items_per_page": 20,
      "thumbnail_size": "medium",
      "features": {
        "enable_ai_analysis": true,
        "enable_vector_search": true
      }
    },
    "upload": {
      "max_file_size_mb": 10,
      "allowed_extensions": ["jpg", "jpeg", "png", "gif", "webp"],
      "auto_generate_thumbnails": true
    },
    "search": {
      "default_search_mode": "text",
      "min_score_threshold": 0.5,
      "max_results": 100
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
  "frontend": {
    "theme": "dark",
    "language": "en-US",
    "items_per_page": 30
  },
  "upload": {
    "max_file_size_mb": 20
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

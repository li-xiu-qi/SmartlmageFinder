# 系统管理 API

系统管理API提供系统状态、配置和缓存管理功能。

## 基础信息

- **Base URL**: `/api/v1/system`
- **Content-Type**: `application/json`

## 端点列表

### 1. 获取基本系统信息

GET `/api/v1/system/info`

获取基本系统信息，不包括数据库和缓存等详细信息。

请求参数: 无

响应示例:

成功响应 200:
  
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

请求参数: 无

响应示例:

成功响应 200:
  
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

请求参数: 无

响应示例:

成功响应 200:
  
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

请求参数: 无

响应示例:

成功响应 200:
  
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

获取最新缓存统计信息（仅统计大小，不再统计条目数）。

请求参数: 无

#### 响应字段（data）

| 字段 | 类型 | 说明 |
|------|------|------|
| enabled | boolean | 是否启用缓存 |
| max_size_gb | number | 最大缓存限制（GB） |
| total_size_mb | number | 当前缓存占用总大小（MB，目录递归统计） |
| text_vector_cache.path | string | 文本向量缓存目录 |
| text_vector_cache.size_mb | number | 文本向量缓存目录总大小 |
| text_vector_cache.db_file_size_mb | number | 底层 cache.db 文件大小（可选） |
| image_vector_cache.path | string | 图像向量缓存目录 |
| image_vector_cache.size_mb | number | 图像向量缓存目录总大小 |
| image_vector_cache.db_file_size_mb | number | 底层 cache.db 文件大小（可选） |
| last_scan | number | 最近一次扫描时间戳 (UNIX 秒) |

  
成功响应 200:

```json
{
  "status": "success",
  
  "code": 200,
  "message": "操作成功",
  "data": {
    "enabled": true,
    "max_size_gb": 1.5,
    "total_size_mb": 3.21,
  
    "text_vector_cache": {
      "path": "./data/caches/text_vector_cache",
      "size_mb": 2.95,
      "db_file_size_mb": 2.40
    },
    "image_vector_cache": {
      "path": "./data/caches/image_vector_cache",
      "size_mb": 0.26,
      "db_file_size_mb": 0.21
    },
    "last_scan": 1723257600
  },
  "error": null
}
```

  
### 6. 精简缓存状态（轮询）

GET `/api/v1/system/cache/brief`

返回一个精简的缓存状态（仅大小与 last_scan），用于前端清除缓存后的快速轮询刷新。

成功 data 示例：

```json
{ "enabled": true, "total_size_mb": 0.12, "last_scan": 1723257615 }
```

### 7. 清除系统缓存

POST `/api/v1/system/cache/clear`

清除系统缓存。

查询参数:

| 参数 | 类型 | 必填 | 描述 | 默认 |
|---|---|---|---|---|
| text_cache | boolean | 否 | 是否清除文本缓存 | true |
| image_cache | boolean | 否 | 是否清除图像缓存 | true |

响应示例:

成功响应 200:

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

### 8. 获取系统配置

GET `/api/v1/system/config`

获取系统配置信息。

  
请求参数: 无

响应示例:

成功响应 200:

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

### 9. 更新系统配置

POST `/api/v1/system/config/update`

更新系统配置。

请求体示例:

```json
{
  "max_file_size": 20971520,
  "allowed_extensions": [".jpg", ".jpeg", ".png", ".webp", ".gif"],
  "cache_config": {
    "text_cache_size": 2000
  }
}
```

响应示例:

成功响应 200:

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

错误响应 400:

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

### 10. 获取向量数据库驱动状态

GET `/api/v1/system/vector-driver`

获取向量数据库驱动状态信息。

请求参数: 无

响应示例:

成功响应 200:

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

- 存储文本向量计算结果（如标题/描述嵌入）
- 当前对外只暴露目录总大小与底层 cache.db 文件大小
- 不再展示条目计数（避免误导），清除后通过 brief 接口快速轮询确认 size 是否归零

### 图像缓存

- 存储图像特征向量（如 CLIP 图像嵌入）
- 统计同上，仅展示大小，无条目数
- 若需要更细粒度指标（命中率等）建议在后续单独增加 profiling 端点

## 监控建议

建议定期调用以下端点进行系统监控：

1. **系统健康检查**: `GET /api/v1/system/info`
2. **数据库状态**: `GET /api/v1/system/database`
3. **存储空间**: `GET /api/v1/system/storage`
4. **缓存状态**: `GET /api/v1/system/cache`
5. **向量数据库状态**: `GET /api/v1/system/vector-driver`

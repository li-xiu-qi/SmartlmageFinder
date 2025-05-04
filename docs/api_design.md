# SmartImageFinder API 设计文档

## 概述

SmartImageFinder 提供了一套完整的 RESTful API，用于管理图片、执行搜索、处理标签和元数据等操作。本文档详细描述了所有 API 端点、参数要求、请求/响应格式以及错误处理机制。

所有 API 返回标准 JSON 格式，统一使用 `ResponseModel` 封装，包含 `success`、`data` 和 `metadata` 三个主要字段。错误响应包含 `code` 和 `message` 字段以提供详细的错误信息。

## 基本信息

- **基础URL**: `/api` (默认)
- **API版本**: v1
- **内容类型**: `application/json` (POST/PUT 请求可能包含 `multipart/form-data`)
- **认证方式**: 无需认证 (开发中可能添加)

## 标准响应格式

### 成功响应

```json
{
  "success": true,
  "data": {
    // 具体响应数据
  },
  "metadata": {
    // 元数据信息，如分页、总数等
  }
}
```

### 错误响应

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "详细错误信息"
  }
}
```

## API 端点总览

| 模块 | 路径 | 描述 |
|------|------|------|
| 图片管理 | `/images/*` | 图片上传、获取、编辑和删除 |
| 搜索功能 | `/search/*` | 文本搜索、图像搜索和相似图片搜索 |
| 标签管理 | `/tags/*` | 获取、创建、编辑和删除标签 |
| 元数据管理 | `/metadata/*` | 获取和管理图片元数据字段 |
| AI功能 | `/ai/*` | AI辅助分析图片内容 |
| 系统管理 | `/system/*` | 系统配置、状态和维护 |

## 1. 图片管理 API

### 1.1 获取图片列表

```
GET /images
```

获取系统中的图片列表，支持分页、排序和过滤。

**查询参数:**
- `page`: 页码 (默认: 1)
- `page_size`: 每页条数 (默认: 20, 最大: 100)
- `sort_by`: 排序字段 (默认: "created_at")
- `order`: 排序方向 (可选值: "asc", "desc", 默认: "desc")
- `start_date`: 开始日期过滤 (可选, 格式: YYYY-MM-DD)
- `end_date`: 结束日期过滤 (可选, 格式: YYYY-MM-DD)
- `tags`: 标签过滤 (可选, 格式: 逗号分隔的标签名)

**响应:**
```json
{
  "success": true,
  "data": {
    "images": [
      {
        "uuid": "550e8400-e29b-41d4-a716-446655440000",
        "title": "山顶风景",
        "description": "山顶俯瞰城市的全景照片",
        "filepath": "data/images/2023/05/550e8400-e29b-41d4-a716-446655440000.jpg",
        "file_size": 2453120,
        "file_type": "jpg", 
        "width": 1920,
        "height": 1080,
        "created_at": "2023-05-15T10:30:00",
        "updated_at": "2023-05-15T10:30:00",
        "tags": ["风景", "城市", "天空"]
      },
      // 更多图片...
    ]
  },
  "metadata": {
    "page": 1,
    "page_size": 20,
    "total_count": 157,
    "total_pages": 8
  }
}
```

### 1.2 获取单张图片详情

```
GET /images/{uuid}
```

获取指定UUID的图片详细信息。

**路径参数:**
- `uuid`: 图片的UUID标识符

**响应:**
```json
{
  "success": true,
  "data": {
    "uuid": "550e8400-e29b-41d4-a716-446655440000",
    "title": "山顶风景",
    "description": "山顶俯瞰城市的全景照片，天空湛蓝",
    "filepath": "data/images/2023/05/550e8400-e29b-41d4-a716-446655440000.jpg",
    "filename": "mountain_view.jpg",
    "file_size": 2453120,
    "file_type": "jpg",
    "width": 1920,
    "height": 1080,
    "created_at": "2023-05-15T10:30:00",
    "updated_at": "2023-05-15T10:30:00",
    "hash_value": "a1b2c3d4e5f6...",
    "metadata": {
      "camera": "Canon EOS R5",
      "location": "华山",
      "aperture": "f/8.0",
      "exposure": "1/250"
    },
    "tags": ["风景", "城市", "天空"]
  }
}
```

### 1.3 上传图片

```
POST /images/upload
```

上传一张或多张新图片。

**请求体** (multipart/form-data):
- `images`: 要上传的图片文件 (支持多文件)
- `analyze` (可选): 是否使用AI分析图片内容 (true/false, 默认: false)
- `tags` (可选): 要添加的标签，逗号分隔
- `metadata` (可选): JSON格式的元数据

**响应:**
```json
{
  "success": true,
  "data": {
    "uploaded": [
      {
        "uuid": "550e8400-e29b-41d4-a716-446655440000",
        "filename": "mountain_view.jpg",
        "filepath": "data/images/2023/05/550e8400-e29b-41d4-a716-446655440000.jpg",
        "title": "山顶风景",
        "description": "山顶俯瞰城市的全景照片",
        "tags": ["风景", "城市", "天空"]
      },
      // 如果有多个文件上传
    ]
  },
  "metadata": {
    "total_uploaded": 1,
    "failed": 0
  }
}
```

### 1.4 更新图片信息

```
PUT /images/{uuid}
```

更新指定UUID图片的信息。

**路径参数:**
- `uuid`: 图片的UUID标识符

**请求体** (JSON):
```json
{
  "title": "新标题",
  "description": "新描述内容",
  "tags": ["新标签1", "新标签2"],
  "metadata": {
    "location": "华山山顶"
  }
}
```

**响应:**
```json
{
  "success": true,
  "data": {
    "uuid": "550e8400-e29b-41d4-a716-446655440000",
    "title": "新标题",
    "description": "新描述内容", 
    "tags": ["新标签1", "新标签2"],
    "updated_at": "2023-05-16T14:30:00"
  }
}
```

### 1.5 删除图片

```
DELETE /images/{uuid}
```

删除指定UUID的图片。

**路径参数:**
- `uuid`: 图片的UUID标识符

**响应:**
```json
{
  "success": true,
  "data": {
    "uuid": "550e8400-e29b-41d4-a716-446655440000",
    "message": "图片已成功删除"
  }
}
```

## 2. 搜索功能 API

### 2.1 文本搜索

```
GET /search/text
```

使用文本查询相似图片。

**查询参数:**
- `q`: 搜索查询文本
- `search_type`: 搜索类型 (可选值: "text", "vector", "hybrid", 默认: "hybrid")
- `text_match_mode`: 文本匹配模式 (可选值: "title", "description", "combined", 默认: "combined")
- `vector_match_mode`: 向量匹配模式 (可选值: "title", "description", "combined", 默认: "combined")
- `limit`: 返回结果数量 (默认: 20)
- `start_date`: 开始日期过滤 (可选)
- `end_date`: 结束日期过滤 (可选)
- `tags`: 标签过滤，逗号分隔 (可选)

**响应:**
```json
{
  "success": true,
  "data": {
    "results": [
      {
        "uuid": "550e8400-e29b-41d4-a716-446655440000",
        "title": "山顶风景",
        "description": "山顶俯瞰城市的全景照片，天空湛蓝",
        "filepath": "data/images/2023/05/550e8400-e29b-41d4-a716-446655440000.jpg",
        "score": 0.92,
        "tags": ["风景", "城市", "天空"]
      },
      // 更多结果...
    ]
  },
  "metadata": {
    "query": "山顶城市风景",
    "search_type": "hybrid",
    "text_match_mode": "combined",
    "vector_match_mode": "combined",
    "total": 15,
    "time_ms": 124
  }
}
```

### 2.2 图像搜索

```
POST /search/image
```

使用上传的图片搜索相似图像。

**请求体** (multipart/form-data):
- `image`: 要搜索的参考图片文件
- `search_type`: 搜索类型 (可选值: "image", "title", "description", "combined", 默认: "image")
- `match_modes`: 匹配模式数组，可多选 (可选值: "image", "title", "description", "combined")
- `weights`: 各匹配模式的权重，逗号分隔 (可选)
- `limit`: 返回结果数量 (默认: 20)
- `start_date`: 开始日期过滤 (可选)
- `end_date`: 结束日期过滤 (可选)
- `tags`: 标签过滤，逗号分隔 (可选)

**响应:**
```json
{
  "success": true,
  "data": {
    "results": [
      {
        "uuid": "660f9511-f30c-42e5-b817-557766551111",
        "title": "海边日落",
        "description": "金色的阳光洒在海面上，形成美丽的日落景色",
        "filepath": "data/images/2023/06/660f9511-f30c-42e5-b817-557766551111.jpg",
        "score": 0.87,
        "similarity_components": {
          "image": 0.91,
          "title": 0.72
        },
        "tags": ["日落", "海洋", "风景"]
      },
      // 更多结果...
    ]
  },
  "metadata": {
    "search_type": "image",
    "match_modes": ["image", "title"],
    "weights": {
      "image": 0.7,
      "title": 0.3
    },
    "total": 12,
    "time_ms": 267
  }
}
```

### 2.3 相似图像搜索

```
GET /search/similar/{uuid}
```

使用系统中已有图片UUID搜索相似图像。

**路径参数:**
- `uuid`: 参考图片的UUID

**查询参数:**
- `match_modes`: 匹配模式数组，可多选 (可选值: "image", "title", "description", "combined", 默认: ["image"])
- `weights`: 各匹配模式的权重，逗号分隔 (可选)
- `limit`: 返回结果数量 (默认: 20)
- `start_date`: 开始日期过滤 (可选)
- `end_date`: 结束日期过滤 (可选)
- `tags`: 标签过滤，逗号分隔 (可选)

**响应:**
```json
{
  "success": true,
  "data": {
    "results": [
      {
        "uuid": "770a8611-d31d-42f6-b928-668877662222",
        "title": "雪山风景",
        "description": "白雪皑皑的高山，天空蔚蓝",
        "filepath": "data/images/2023/07/770a8611-d31d-42f6-b928-668877662222.jpg",
        "score": 0.79,
        "similarity_components": {
          "image": 0.86,
          "description": 0.65
        },
        "tags": ["雪山", "自然", "风景"]
      },
      // 更多结果...
    ]
  },
  "metadata": {
    "reference_uuid": "550e8400-e29b-41d4-a716-446655440000",
    "match_modes": ["image", "description"],
    "weights": {
      "image": 0.7,
      "description": 0.3
    },
    "total": 10,
    "time_ms": 158
  }
}
```

## 3. 标签管理 API

### 3.1 获取热门标签

```
GET /tags/popular
```

获取系统中使用最多的标签列表。

**查询参数:**
- `limit`: 返回标签的数量 (默认: 50)

**响应:**
```json
{
  "success": true,
  "data": {
    "tags": [
      {
        "name": "风景",
        "count": 156
      },
      {
        "name": "自然",
        "count": 120
      },
      {
        "name": "城市",
        "count": 89
      },
      // 更多标签...
    ]
  },
  "metadata": {
    "total": 534
  }
}
```

### 3.2 标签自动完成

```
GET /tags/autocomplete
```

根据前缀获取标签建议，用于输入自动完成。

**查询参数:**
- `prefix`: 标签前缀
- `limit`: 返回建议的数量 (默认: 10)

**响应:**
```json
{
  "success": true,
  "data": {
    "suggestions": ["自然", "自驾游", "自由行"]
  }
}
```

### 3.3 为图片添加标签

```
POST /tags/add/{uuid}
```

为指定图片添加一个或多个标签。

**路径参数:**
- `uuid`: 图片的UUID

**请求体** (JSON):
```json
{
  "tags": ["新标签1", "新标签2"]
}
```

**响应:**
```json
{
  "success": true,
  "data": {
    "uuid": "550e8400-e29b-41d4-a716-446655440000",
    "added_tags": ["新标签1", "新标签2"],
    "all_tags": ["风景", "城市", "天空", "新标签1", "新标签2"]
  }
}
```

### 3.4 从图片删除标签

```
DELETE /tags/remove/{uuid}/{tag}
```

从指定图片删除特定标签。

**路径参数:**
- `uuid`: 图片的UUID
- `tag`: 要删除的标签名

**响应:**
```json
{
  "success": true,
  "data": {
    "uuid": "550e8400-e29b-41d4-a716-446655440000",
    "removed_tag": "城市",
    "remaining_tags": ["风景", "天空", "新标签1", "新标签2"]
  }
}
```

### 3.5 批量标签操作

```
POST /tags/batch
```

批量添加、删除或重命名标签。

**请求体** (JSON):
```json
{
  "operation": "rename",
  "source_tag": "旧标签",
  "target_tag": "新标签",
  "images": ["uuid1", "uuid2", "uuid3"]  // 可选，不提供则对所有图片生效
}
```

**响应:**
```json
{
  "success": true,
  "data": {
    "affected_images": 25,
    "message": "已将标签 '旧标签' 重命名为 '新标签'"
  }
}
```

## 4. 元数据管理 API

### 4.1 获取元数据字段统计

```
GET /metadata/fields
```

获取系统中使用的元数据字段统计信息。

**查询参数:**
- `limit`: 返回字段的数量 (默认: 50)

**响应:**
```json
{
  "success": true,
  "data": {
    "fields": [
      {
        "name": "location",
        "count": 230,
        "type": "string"
      },
      {
        "name": "camera",
        "count": 156,
        "type": "string"
      },
      {
        "name": "aperture",
        "count": 142,
        "type": "string"
      },
      // 更多字段...
    ]
  }
}
```

### 4.2 更新图片元数据

```
PUT /metadata/{uuid}
```

更新指定图片的元数据。

**路径参数:**
- `uuid`: 图片的UUID

**请求体** (JSON):
```json
{
  "metadata": {
    "location": "新地点",
    "camera": "Sony A7IV",
    "aperture": "f/2.8"
  }
}
```

**响应:**
```json
{
  "success": true,
  "data": {
    "uuid": "550e8400-e29b-41d4-a716-446655440000",
    "updated_metadata": {
      "location": "新地点",
      "camera": "Sony A7IV",
      "aperture": "f/2.8"
    }
  }
}
```

### 4.3 批量更新元数据

```
POST /metadata/batch
```

批量更新多个图片的元数据。

**请求体** (JSON):
```json
{
  "uuids": ["uuid1", "uuid2", "uuid3"],
  "metadata": {
    "location": "同一地点",
    "event": "同一事件"
  }
}
```

**响应:**
```json
{
  "success": true,
  "data": {
    "updated_count": 3,
    "failed_count": 0,
    "updated_uuids": ["uuid1", "uuid2", "uuid3"]
  }
}
```

## 5. AI功能 API

### 5.1 分析图片内容

```
POST /ai/analyze/{uuid}
```

使用AI分析指定图片内容，生成标题、描述和标签。

**路径参数:**
- `uuid`: 图片的UUID

**查询参数:**
- `model`: 使用的模型名称 (可选，默认使用系统配置的模型)
- `detail`: 分析细节级别 (可选值: "low", "high", "auto", 默认: "low")

**响应:**
```json
{
  "success": true,
  "data": {
    "uuid": "550e8400-e29b-41d4-a716-446655440000",
    "analysis": {
      "title": "山顶城市景观",
      "description": "高山之巅俯瞰城市全景，蓝天白云映衬下的现代都市",
      "tags": ["山顶", "城市", "全景", "俯视"]
    },
    "model_used": "Qwen/Qwen2.5-VL-32B-Instruct",
    "processing_time": 2.45
  }
}
```

### 5.2 获取可用AI模型

```
GET /ai/models
```

获取系统中可用的AI视觉模型列表。

**响应:**
```json
{
  "success": true,
  "data": {
    "available_models": [
      "Qwen/Qwen2.5-VL-32B-Instruct",
      "openai/gpt-4-vision-preview"
    ],
    "current_model": "Qwen/Qwen2.5-VL-32B-Instruct"
  }
}
```

### 5.3 批量AI分析

```
POST /ai/batch
```

批量分析多张图片。

**请求体** (JSON):
```json
{
  "uuids": ["uuid1", "uuid2", "uuid3"],
  "model": "Qwen/Qwen2.5-VL-32B-Instruct",
  "detail": "low",
  "apply_results": true
}
```

**响应:**
```json
{
  "success": true,
  "data": {
    "processed": 3,
    "applied": 3,
    "failed": 0,
    "results": [
      {
        "uuid": "uuid1", 
        "title": "自动生成的标题1",
        "success": true
      },
      {
        "uuid": "uuid2",
        "title": "自动生成的标题2",
        "success": true
      },
      {
        "uuid": "uuid3",
        "title": "自动生成的标题3",
        "success": true
      }
    ]
  }
}
```

## 6. 系统管理 API

### 6.1 获取系统状态

```
GET /system/status
```

获取系统当前运行状态和信息。

**响应:**
```json
{
  "success": true,
  "data": {
    "version": "1.0.0",
    "total_images": 5721,
    "total_tags": 534,
    "storage_used": "42.5 GB",
    "vector_indices_size": "3.2 GB",
    "vector_search_available": true,
    "ai_enabled": true,
    "uptime": "5 days, 4 hours, 31 minutes"
  }
}
```

### 6.2 获取系统配置

```
GET /system/config
```

获取当前系统配置项。

**响应:**
```json
{
  "success": true,
  "data": {
    "config": {
      "HOST": "0.0.0.0",
      "PORT": 8000,
      "UPLOAD_DIR": "./data/images",
      "MODEL_PATH": "./models/jina-clip-v2",
      "VECTOR_DIM": 1024,
      "USE_CACHE": true,
      "MAX_CACHE_SIZE_GB": 1.5,
      "AI_ENABLED": true,
      "VISION_MODEL": "Qwen/Qwen2.5-VL-32B-Instruct"
    }
  }
}
```

### 6.3 更新系统配置

```
PUT /system/config
```

更新系统配置项。

**请求体** (JSON):
```json
{
  "config": {
    "MAX_CACHE_SIZE_GB": 2.0,
    "AI_ENABLED": true,
    "VISION_MODEL": "openai/gpt-4-vision-preview"
  }
}
```

**响应:**
```json
{
  "success": true,
  "data": {
    "updated_config": {
      "MAX_CACHE_SIZE_GB": 2.0,
      "AI_ENABLED": true,
      "VISION_MODEL": "openai/gpt-4-vision-preview"
    },
    "restart_required": false
  }
}
```

### 6.4 重建索引

```
POST /system/rebuild-indices
```

重建向量索引。

**请求体** (JSON):
```json
{
  "indices": ["image", "title", "description"],  // 需要重建的索引，可选
  "clear_existing": true                        // 是否清除已有索引，默认true
}
```

**响应:**
```json
{
  "success": true,
  "data": {
    "job_id": "rebuild-20230515-123456",
    "status": "started",
    "estimated_time_minutes": 15
  }
}
```

### 6.5 检查索引重建状态

```
GET /system/rebuild-status/{job_id}
```

检查索引重建任务的状态。

**路径参数:**
- `job_id`: 重建任务ID

**响应:**
```json
{
  "success": true,
  "data": {
    "job_id": "rebuild-20230515-123456",
    "status": "in_progress",
    "progress": 45.2,
    "processed_images": 2587,
    "total_images": 5721,
    "elapsed_time_minutes": 6.5,
    "estimated_remaining_minutes": 8.2
  }
}
```

## 错误代码

系统使用以下标准错误代码：

| 错误代码 | 描述 |
|---------|------|
| `BAD_REQUEST` | 请求格式不正确或参数无效 |
| `NOT_FOUND` | 请求的资源不存在 |
| `CONFLICT` | 资源冲突，例如上传的文件已存在 |
| `INVALID_FILE` | 上传的文件格式不正确或文件损坏 |
| `PROCESSING_ERROR` | 处理请求时发生错误 |
| `SERVICE_UNAVAILABLE` | 服务当前不可用，如AI功能关闭 |
| `SYSTEM_ERROR` | 系统内部错误 |
| `INVALID_PARAM` | 参数值无效 |
| `NO_VECTOR` | 找不到向量索引 |

## API 使用示例

### 文本搜索示例

```javascript
// 使用文本搜索API查询与"山顶风景"相关的图片
fetch('/api/search/text?q=山顶风景&search_type=hybrid&limit=10')
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      console.log(`找到${data.metadata.total}张匹配图片`);
      data.data.results.forEach(image => {
        console.log(`${image.title} (相似度: ${image.score})`);
      });
    }
  });
```

### 图片上传示例

```javascript
// 上传图片并请求AI分析内容
const formData = new FormData();
formData.append('images', imageFile);
formData.append('analyze', 'true');
formData.append('tags', '风景,旅行');

fetch('/api/images/upload', {
  method: 'POST',
  body: formData
})
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      console.log(`成功上传${data.metadata.total_uploaded}张图片`);
    }
  });
```

### 错误处理示例

```javascript
fetch('/api/images/550e8400-e29b-41d4-a716-446655440000')
  .then(response => response.json())
  .then(data => {
    if (!data.success) {
      console.error(`错误: ${data.error.code} - ${data.error.message}`);
      // 处理错误...
    } else {
      // 处理成功响应...
    }
  });
```

## 安全建议

1. **API密钥**: 考虑为生产环境添加API密钥认证机制
2. **请求限制**: 实现请求频率限制，防止API滥用
3. **输入验证**: 确保所有API端点实施严格的输入验证
4. **CORS策略**: 配置适当的CORS策略，限制允许访问API的域名

## 未来扩展

1. **认证与授权**: 添加用户认证和基于角色的访问控制
2. **WebSocket支持**: 为长时间运行的任务添加实时进度更新
3. **批量操作**: 增强批量处理功能，提高效率
4. **API版本控制**: 实施API版本控制机制，确保向后兼容性
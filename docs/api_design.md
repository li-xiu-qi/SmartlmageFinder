# SmartImageFinder API接口设计

## 概述

SmartImageFinder系统的API接口基于RESTful架构设计，采用FastAPI框架实现。本文档详细定义了系统所有API端点的请求/响应格式和错误处理机制，以确保前端和后端的无缝集成。

## API架构

### 基础信息

- **基础路径**: `/api/v1`（可通过`API_V1_PREFIX`配置项修改）
- **响应格式**: JSON
- **身份验证**: 无需身份验证，直接访问
- **跨域支持**: 默认允许来自`http://localhost:3000`的请求（可通过`BACKEND_CORS_ORIGINS`配置）

### 通用响应格式

为保持一致性，所有API响应遵循统一的格式：

```json
{
    "status": "success",  // 或 "error"
    "data": { ... },      // 成功时返回的数据
    "error": null,        // 成功时为null，失败时包含错误信息
    "metadata": {         // 元数据，如分页信息
        "page": 1,
        "page_size": 20,
        "total": 100
    }
}
```

错误响应示例：

```json
{
    "status": "error",
    "data": null,
    "error": {
        "code": "NOT_FOUND",
        "message": "请求的资源不存在"
    },
    "metadata": {}
}
```

## API端点列表

### 1. 图片管理API

#### 1.1 获取图片列表

- **端点**: `GET /images`
- **描述**: 分页获取图片列表，支持多种过滤和排序
- **查询参数**:
    - `page`: 页码，默认1
    - `page_size`: 每页数量，默认20
    - `sort_by`: 排序字段，可选值：`created_at`、`title`等
    - `order`: 排序方向，可选值：`asc`、`desc`
    - `start_date`: 开始日期过滤，格式：YYYY-MM-DD
    - `end_date`: 结束日期过滤，格式：YYYY-MM-DD
    - `tags`: 标签过滤，逗号分隔的标签列表
    - `metadata`: JSON格式的元数据过滤条件
- **响应示例**:
    ```json
    {
        "status": "success",
        "data": {
            "images": [
                {
                    "uuid": "550e8400e29b41d4a716446655440000",
                    "title": "海滩日落",
                    "description": "美丽的海滩日落景观，金色的阳光洒在海面上",
                    "filepath": "/images/2023/04/30/550e8400e29b41d4a716446655440000.jpg",
                    "created_at": "2023-04-30T15:30:45",
                    "tags": ["自然", "日落", "海滩"]
                },
                // ... 更多图片
            ]
        },
        "error": null,
        "metadata": {
            "page": 1,
            "page_size": 20,
            "total": 156,
            "total_pages": 8
        }
    }
    ```

#### 1.2 获取图片详情

- **端点**: `GET /images/{uuid}`
- **描述**: 获取指定UUID的图片详细信息
- **路径参数**:
    - `uuid`: 图片的唯一标识
- **响应示例**:
    ```json
    {
        "status": "success",
        "data": {
            "uuid": "550e8400e29b41d4a716446655440000",
            "title": "海滩日落",
            "description": "美丽的海滩日落景观，金色的阳光洒在海面上",
            "filename": "sunset.jpg",
            "filepath": "/images/2023/04/30/550e8400e29b41d4a716446655440000.jpg",
            "file_size": 2458000,
            "file_type": "jpg",
            "width": 1920,
            "height": 1080,
            "created_at": "2023-04-30T15:30:45",
            "updated_at": "2023-05-01T10:15:22",
            "tags": ["自然", "日落", "海滩"],
            "metadata": {
                "拍摄地点": "三亚",
                "相机型号": "Canon EOS R5",
                "拍摄时间": "2023-04-25 18:30"
            }
        },
        "error": null,
        "metadata": {}
    }
    ```

#### 1.3 上传图片

- **端点**: `POST /images/upload`
- **描述**: 上传单张或多张图片
- **内容类型**: `multipart/form-data`
- **请求参数**:
    - `files`: 文件数组，包含要上传的图片
    - `metadata`: (可选) JSON字符串，包含所有图片的通用元数据
    - `title`: (可选) 字符串，图片标题
    - `description`: (可选) 字符串，图片描述
    - `tags`: (可选) JSON数组字符串，图片标签列表
    - `generate_metadata`: (可选) 布尔值，是否自动生成元数据，默认为`false`
- **响应示例**:
    ```json
    {
        "status": "success",
        "data": {
            "uploaded": [
                {
                    "uuid": "550e8400e29b41d4a716446655440000",
                    "original_filename": "sunset.jpg",
                    "file_size": 2458000,
                    "stored_path": "/images/2023/04/30/550e8400e29b41d4a716446655440000.jpg"
                },
                // ... 更多成功上传的图片
            ],
            "failed": [
                {
                    "filename": "toolarge.tiff",
                    "error": "文件大小超过限制(50MB)"
                }
                // ... 更多上传失败的图片
            ]
        },
        "error": null,
        "metadata": {
            "total": 5,
            "success": 4,
            "failed": 1
        }
    }
    ```

#### 1.4 更新图片信息

- **端点**: `PATCH /images/{uuid}`
- **描述**: 更新图片的元数据、标题、描述或标签
- **路径参数**:
    - `uuid`: 图片的唯一标识
- **请求体**:
    ```json
    {
        "title": "三亚海滩日落",
        "description": "更新的描述文本",
        "tags": ["自然", "日落", "海滩", "三亚"],
        "metadata": {
            "拍摄地点": "三亚湾",
            "天气": "晴朗"
        }
    }
    ```
- **响应示例**:
    ```json
    {
        "status": "success",
        "data": {
            "uuid": "550e8400e29b41d4a716446655440000",
            "title": "三亚海滩日落",
            "updated_at": "2023-05-01T10:15:22"
        },
        "error": null,
        "metadata": {}
    }
    ```

#### 1.5 删除图片

- **端点**: `DELETE /images/{uuid}`
- **描述**: 删除指定的图片及其所有元数据
- **路径参数**:
    - `uuid`: 图片的唯一标识
- **响应示例**:
    ```json
    {
        "status": "success",
        "data": {
            "message": "图片已成功删除"
        },
        "error": null,
        "metadata": {}
    }
    ```

#### 1.6 批量删除图片

- **端点**: `DELETE /images`
- **描述**: 批量删除多张图片
- **请求体**:
    ```json
    {
        "uuids": [
            "550e8400e29b41d4a716446655440000",
            "660e8400e29b41d4a71644665544f0f0",
            // ... 更多图片UUID
        ]
    }
    ```
- **响应示例**:
    ```json
    {
        "status": "success",
        "data": {
            "deleted": 3,
            "failed": 0,
            "details": []
        },
        "error": null,
        "metadata": {}
    }
    ```

### 2. 搜索API

#### 2.1 文本搜索图片

- **端点**: `GET /search/text`
- **描述**: 使用文本查询相似图片
- **查询参数**:
    - `q`: 搜索查询文本
    - `mode`: 搜索模式，可选值：`vector`(向量相似度)、`text`(文本匹配)、`hybrid`(混合)，默认为`vector`
    - `field`: 搜索字段，可选值：`title`、`description`、`all`，默认为`all`
    - `limit`: 返回结果数量限制，默认20
    - `filter`: (可选) JSON格式的过滤条件
    - `start_date`: (可选) 开始日期过滤
    - `end_date`: (可选) 结束日期过滤
    - `tags`: (可选) 标签过滤，逗号分隔
- **响应示例**:
    ```json
    {
        "status": "success",
        "data": {
            "results": [
                {
                    "uuid": "550e8400e29b41d4a716446655440000",
                    "title": "海滩日落",
                    "description": "美丽的海滩日落景观，金色的阳光洒在海面上",
                    "filepath": "/images/2023/04/30/550e8400e29b41d4a716446655440000.jpg",
                    "score": 0.95,
                    "tags": ["自然", "日落", "海滩"]
                },
                // ... 更多结果
            ]
        },
        "error": null,
        "metadata": {
            "query": "海边日落",
            "mode": "vector",
            "total": 15,
            "time_ms": 120
        }
    }
    ```

#### 2.2 图片搜索图片

- **端点**: `POST /search/image`
- **描述**: 上传图片搜索相似图片
- **内容类型**: `multipart/form-data`
- **请求参数**:
    - `image`: 要搜索的参考图片文件
    - `limit`: 返回结果数量限制，默认20
    - `filter`: (可选) JSON格式的过滤条件
    - `start_date`: (可选) 开始日期过滤
    - `end_date`: (可选) 结束日期过滤
    - `tags`: (可选) 标签过滤，逗号分隔
- **响应格式**: 与文本搜索响应格式相同

#### 2.3 UUID图片搜索

- **端点**: `GET /search/similar/{uuid}`
- **描述**: 根据系统中已存在的图片UUID搜索相似图片
- **路径参数**:
    - `uuid`: 参考图片的唯一标识
- **查询参数**:
    - `limit`: 返回结果数量限制，默认20
    - `filter`: (可选) JSON格式的过滤条件
    - `start_date`: (可选) 开始日期过滤
    - `end_date`: (可选) 结束日期过滤
    - `tags`: (可选) 标签过滤，逗号分隔
- **响应格式**: 与文本搜索响应格式相同

### 3. 标签管理API

#### 3.1 获取所有标签

- **端点**: `GET /tags`
- **描述**: 获取系统中所有已使用标签及其使用频率
- **响应示例**:
    ```json
    {
        "status": "success",
        "data": {
            "tags": [
                {"name": "风景", "count": 120},
                {"name": "海滩", "count": 85},
                {"name": "日落", "count": 64},
                {"name": "建筑", "count": 54},
                // ... 更多标签
            ]
        },
        "error": null,
        "metadata": {
            "total": 45
        }
    }
    ```

#### 3.2 添加图片标签

- **端点**: `POST /images/{uuid}/tags`
- **描述**: 为指定图片添加一个或多个标签
- **路径参数**:
    - `uuid`: 图片的唯一标识
- **请求体**:
    ```json
    {
    "tags": ["新标签1", "新标签2"]
  }
  ```
- **响应示例**:
  ```json
  {
    "status": "success",
    "data": {
      "uuid": "550e8400e29b41d4a716446655440000",
      "tags": ["自然", "日落", "海滩", "新标签1", "新标签2"]
    },
    "error": null,
    "metadata": {}
  }
  ```

#### 3.3 删除图片标签

- **端点**: `DELETE /images/{uuid}/tags/{tag}`
- **描述**: 从指定图片中删除标签
- **路径参数**:
  - `uuid`: 图片的唯一标识
  - `tag`: 要删除的标签
- **响应示例**:
  ```json
  {
    "status": "success",
    "data": {
      "uuid": "550e8400e29b41d4a716446655440000",
      "tags": ["自然", "海滩"]
    },
    "error": null,
    "metadata": {}
  }
  ```

### 4. 元数据管理API

#### 4.1 获取元数据字段

- **端点**: `GET /metadata/fields`
- **描述**: 获取系统中所有已使用的元数据字段及其使用频率
- **响应示例**:
  ```json
  {
    "status": "success",
    "data": {
      "fields": [
        {"name": "拍摄地点", "count": 245, "type": "string"},
        {"name": "相机型号", "count": 210, "type": "string"},
        {"name": "拍摄时间", "count": 198, "type": "string"},
        {"name": "光圈值", "count": 150, "type": "string"},
        // ... 更多字段
      ]
    },
    "error": null,
    "metadata": {
      "total": 28
    }
  }
  ```

#### 4.2 更新图片元数据

- **端点**: `PATCH /images/{uuid}/metadata`
- **描述**: 更新指定图片的元数据
- **路径参数**:
  - `uuid`: 图片的唯一标识
- **请求体**:
  ```json
  {
    "metadata": {
      "拍摄地点": "三亚湾",
      "天气": "晴朗",
      "拍摄时间": "2023-04-25 18:30"
    }
  }
  ```
- **响应示例**:
  ```json
  {
    "status": "success",
    "data": {
      "uuid": "550e8400e29b41d4a716446655440000",
      "updated_at": "2023-05-01T10:25:22"
    },
    "error": null,
    "metadata": {}
  }
  ```

### 5. 多模态内容生成API

#### 5.1 为图片生成描述

- **端点**: `POST /ai/generate/{uuid}`
- **描述**: 使用多模态模型为指定图片生成标题、描述和标签
- **路径参数**:
  - `uuid`: 图片的唯一标识
- **请求参数**:
  - `generate_title`: (可选) 布尔值，是否生成标题，默认为`true`
  - `generate_description`: (可选) 布尔值，是否生成描述，默认为`true`
  - `generate_tags`: (可选) 布尔值，是否生成标签，默认为`true`
  - `detail`: (可选) 字符串，细节级别，可选值：`low`、`high`，默认为`low`
- **响应示例**:
  ```json
  {
    "status": "success",
    "data": {
      "uuid": "550e8400e29b41d4a716446655440000",
      "generated": {
        "title": "三亚海滩日落",
        "description": "金色的阳光洒在海面上，远处的帆船剪影点缀着橙红色的天际线",
        "tags": ["海滩", "日落", "三亚", "自然风光", "晚霞"]
      },
      "applied": true
    },
    "error": null,
    "metadata": {
      "model": "gpt-4-vision-preview",
      "time_ms": 2450
    }
  }
  ```

#### 5.2 批量生成内容

- **端点**: `POST /ai/batch-generate`
- **描述**: 批量为多张图片生成内容
- **请求体**:
  ```json
  {
    "uuids": [
      "550e8400e29b41d4a716446655440000",
      "660e8400e29b41d4a71644665544f0f0",
      // ... 更多图片UUID
    ],
    "options": {
      "generate_title": true,
      "generate_description": true,
      "generate_tags": true,
      "detail": "low"
    }
  }
  ```
- **响应示例**:
  ```json
  {
    "status": "success",
    "data": {
      "task_id": "task-123-456-789",
      "total_images": 3,
      "status": "processing"
    },
    "error": null,
    "metadata": {}
  }
  ```

#### 5.3 查询批量任务状态

- **端点**: `GET /ai/tasks/{task_id}`
- **描述**: 查询批量生成任务的状态
- **路径参数**:
  - `task_id`: 任务ID
- **响应示例**:
  ```json
  {
    "status": "success",
    "data": {
      "task_id": "task-123-456-789",
      "status": "completed",
      "progress": {
        "total": 3,
        "processed": 3,
        "succeeded": 2,
        "failed": 1
      },
      "results": [
        {
          "uuid": "550e8400e29b41d4a716446655440000",
          "status": "success"
        },
        {
          "uuid": "660e8400e29b41d4a71644665544f0f0",
          "status": "success"
        },
        {
          "uuid": "770e8400e29b41d4a71644665544abcd",
          "status": "error",
          "error": "无法处理图像"
        }
      ]
    },
    "error": null,
    "metadata": {
      "start_time": "2023-05-01T10:30:00",
      "end_time": "2023-05-01T10:32:15",
      "duration_ms": 135000
    }
  }
  ```

### 6. 系统管理API

#### 6.1 获取系统状态

- **端点**: `GET /system/status`
- **描述**: 获取系统当前状态，包括模型加载状态和数据库连接状态
- **响应示例**:
  ```json
  {
    "status": "success",
    "data": {
      "system": {
        "version": "1.0.0",
        "uptime": 86400,
        "status": "healthy"
      },
      "components": {
        "model": {
          "status": "loaded",
          "name": "jina-clip-v2",
          "load_time": "2023-04-30T00:00:00"
        },
        "database": {
          "status": "connected",
          "type": "milvus",
          "version": "2.2.3"
        },
        "multimodal_api": {
          "status": "available",
          "model": "gpt-4-vision-preview"
        }
      },
      "storage": {
        "total_images": 1567,
        "total_size_mb": 12500
      }
    },
    "error": null,
    "metadata": {}
  }
  ```

#### 6.2 清除缓存

- **端点**: `POST /system/clear-cache`
- **描述**: 清除系统缓存
- **请求体**:
  ```json
  {
    "cache_types": ["vector", "image_analysis", "all"]
  }
  ```
- **响应示例**:
  ```json
  {
    "status": "success",
    "data": {
      "message": "缓存已清除",
      "details": {
        "vector_cache": {
          "cleared": true,
          "entries_removed": 1250,
          "size_freed_mb": 450
        },
        "image_analysis_cache": {
          "cleared": true,
          "entries_removed": 780,
          "size_freed_mb": 15
        }
      }
    },
    "error": null,
    "metadata": {}
  }
  ```

## 状态码和错误处理

### 状态码使用

API使用标准HTTP状态码表示请求状态：

- `200 OK`: 请求成功
- `201 Created`: 资源创建成功
- `204 No Content`: 请求成功但无内容返回（如删除操作）
- `400 Bad Request`: 请求参数错误
- `404 Not Found`: 请求的资源不存在
- `422 Unprocessable Entity`: 请求格式正确但语义无效
- `500 Internal Server Error`: 服务器内部错误
- `503 Service Unavailable`: 服务暂时不可用（如模型加载中）

### 错误响应格式

错误响应遵循统一的格式，包含错误代码和详细描述：

```json
{
  "status": "error",
  "data": null,
  "error": {
    "code": "ERROR_CODE",
    "message": "人类可读的错误描述",
    "details": {
      // 可选的详细错误信息
    }
  },
  "metadata": {}
}
```

### 错误代码列表

系统定义了以下标准错误代码：

| 错误代码 | 描述 |
|---------|------|
| `INVALID_REQUEST` | 请求参数无效 |
| `NOT_FOUND` | 请求的资源不存在 |
| `UNAUTHORIZED` | 未授权访问 |
| `FORBIDDEN` | 禁止访问 |
| `VALIDATION_ERROR` | 数据验证错误 |
| `DATABASE_ERROR` | 数据库操作错误 |
| `MODEL_ERROR` | 模型加载或推理错误 |
| `API_ERROR` | 第三方API调用错误 |
| `FILE_ERROR` | 文件处理错误 |
| `SYSTEM_ERROR` | 系统内部错误 |

## 性能和限制

- **请求大小限制**：单次上传文件不超过50MB（可配置）
- **批处理限制**：批处理端点最大允许处理50个项目
- **请求频率限制**：默认每分钟200个请求，图像生成API每分钟20个请求
- **搜索结果限制**：单次搜索最多返回100条结果

## API版本控制

系统采用URI路径版本控制策略：

1. **当前版本**: `/api/v1/*`
2. **未来版本**: 当API有不兼容更改时，将增加新版本，如`/api/v2/*`
3. **版本兼容性**:
   - 次要更新保持同一版本前缀
   - 主要更新使用新版本前缀
   - 旧版本API将保持至少6个月兼容期

## API文档和开发工具

- **API文档**: 系统集成了Swagger UI，可通过`/docs`访问交互式API文档
- **OpenAPI规范**: 通过`/openapi.json`提供完整的OpenAPI规范文件
- **客户端生成**: 可从OpenAPI规范自动生成多种语言的API客户端

## 安全性考虑

由于系统设计为个人使用的本地环境应用，采用较简单的安全策略：

1. **认证**:
   - 系统使用基于API密钥的简单认证
   - 密钥通过HTTP头`X-API-Key`传递
   - 本地环境可配置禁用认证

2. **数据验证**:
   - 所有API输入均进行严格验证
   - 使用Pydantic模型定义请求/响应架构
   - 文件上传包含类型和大小验证

3. **错误消息安全**:
   - 生产环境中隐藏敏感的错误详情
   - 仅返回必要的错误信息，防止信息泄露

4. **跨域资源共享(CORS)**:
   - 默认仅允许本地前端访问
   - 通过配置项`BACKEND_CORS_ORIGINS`定制允许的来源
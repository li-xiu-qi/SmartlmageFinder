# API 简介与概述

## 概述

SmartImageFinder 提供了一套完整的 RESTful API，用于管理图片、执行搜索、处理标签和元数据等操作。本文档详细描述了所有 API 端点、参数要求、请求/响应格式以及错误处理机制。

所有 API 返回标准 JSON 格式，统一使用 `ResponseModel` 封装，包含 `status`、`code`、`message`、`data`、`error`、`metadata`、`timestamp` 和 `request_id` 字段。错误响应包含 `error` 对象，其中含有 `code`、`message` 和可选的 `details` 字段以提供详细的错误信息。

## 基本信息

- **基础URL**: `/api/v1` (默认)
- **内容类型**: `application/json` (POST/PUT/PATCH 请求可能包含 `multipart/form-data`)
- **认证方式**: 无需认证 (开发中可能添加)

## 标准响应格式

系统采用统一的 `ResponseModel` 封装所有 API 响应，确保前端接收到结构一致的数据。

### 响应模型字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| status | string | 响应状态，"success" 或 "error" |
| code | int | HTTP 状态码，如 200 (成功)、400 (请求错误)、404 (资源不存在) 等 |
| message | string | 响应消息或错误描述 |
| data | object | 响应的主体数据，错误响应中为 null |
| error | object | 错误信息对象，成功响应中为 null |
| metadata | object | 附加元数据，如分页信息、统计数据等 |
| timestamp | datetime | 响应时间戳 |
| request_id | string | 请求唯一标识，用于跟踪和调试 |

### 成功响应示例

```json
{
  "status": "success",
  "code": 200,
  "message": "获取数据成功",
  "data": {
    // 具体响应数据
  },
  "metadata": {
    // 元数据信息，如分页、总数等
  },
  "error": null,
  "timestamp": "2025-05-16T10:30:45.123456",
  "request_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### 错误响应示例

```json
{
  "status": "error",
  "code": 404,
  "message": "请求的资源不存在",
  "data": null,
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "请求的图片ID不存在",
    "details": {
      "image_id": "invalid_id_123",
      "resource_type": "image"
    }
  },
  "metadata": {},
  "timestamp": "2025-05-16T10:31:22.123456",
  "request_id": "550e8400-e29b-41d4-a716-446655440001"
}
```

### 分页响应

对于返回列表数据的 API，系统提供标准分页功能。分页信息包含在 `metadata.pagination` 对象中：

```json
{
  "status": "success",
  "code": 200,
  "message": "获取图片列表成功",
  "data": [
    // 分页后的数据列表
  ],
  "metadata": {
    "pagination": {
      "page": 1,
      "page_size": 10,
      "total_items": 120,
      "total_pages": 12
    }
  }
}
```



## API 端点总览

| 模块 | 路径 | 描述 |
|------|------|------|
| 图片管理 | `/api/v1/images/*` | 图片上传、获取、编辑和删除 |
| 搜索功能 | `/api/v1/search/*` | 文本搜索、图像搜索和相似图片搜索 |
| 标签管理 | `/api/v1/tags/*`, `/api/v1/images/{uuid}/tags*` | 获取标签、为图片添加/删除标签 |
| 元数据管理 | `/api/v1/metadata/*` | 获取和管理图片元数据字段 |
| AI功能 | `/api/v1/ai/*` | AI辅助分析图片内容、生成标题、描述和标签 |
| 系统管理 | `/api/v1/system/*` | 系统配置、状态和缓存管理 |

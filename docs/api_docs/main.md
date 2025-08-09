# SmartImageFinder API 文档

## 简介

SmartImageFinder是一个智能图片管理和搜索系统，提供了一系列API用于图片上传、管理、搜索和分析。本文档提供了系统中所有可用API端点的详细说明。

## API 概览

系统API基于RESTful架构，使用HTTP协议进行通信。所有API的基础URL路径为：`/api/v1/`。

### 主要模块

1. [图片管理 API](images_router.md) - 图片上传、获取、更新和删除

1. [搜索 API](search_router.md) - 统一搜索 / 图片搜索 / 向量搜索 / 相似搜索

1. [AI 分析 API](ai_router.md) - 图片AI分析功能

1. [标签管理 API](tags_router.md) - 图片标签的获取和管理

1. [元数据管理 API](metadata_router.md) - 图片元数据的管理

1. [系统管理 API](system_router.md) - 系统状态和配置管理

## 认证

目前系统API不要求认证即可访问。在未来版本中可能会引入JWT或API密钥等认证机制。

## 响应格式

所有API响应均使用统一的JSON格式：

```json
{
  "status": "success", // 或 "error"
  "code": 200, // HTTP状态码
  "message": "操作成功", // 响应消息
  "data": null, // 响应数据，根据不同API返回不同内容
  "error": null, // 错误信息，成功时为null
  "metadata": {}, // 附加元数据
  "timestamp": "2023-05-19T12:34:56.789Z", // 响应时间戳
  "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890" // 请求ID
}
```

## 分页

支持分页的API使用以下查询参数：

- `page`: 页码，从1开始
- `page_size`: 每页记录数，默认为20

分页响应中包含以下元数据：

```json
"metadata": {
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_items": 100,
    "total_pages": 5
  }
}
```

## 错误处理

当发生错误时，API返回的响应中包含详细的错误信息：

```json
{
  "status": "error",
  "code": 400, // HTTP错误码
  "message": "请求参数错误",
  "data": null,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "图片格式不支持",
    "details": {
      "supported_formats": ["jpg", "png", "webp"]
    }
  },
  "metadata": {},
  "timestamp": "2023-05-19T12:34:56.789Z",
  "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

## 常见错误代码

| 错误代码 | 描述 |
|---------|-----|
| VALIDATION_ERROR | 请求参数验证失败 |
| NOT_FOUND | 请求的资源不存在 |
| INTERNAL_SERVER_ERROR | 服务器内部错误 |
| SERVICE_UNAVAILABLE | 服务暂时不可用 |
| DATABASE_ERROR | 数据库操作错误 |
| AI_PROCESSING_ERROR | AI处理过程中出错 |

请参考各个具体API的文档了解特定于该API的错误代码。

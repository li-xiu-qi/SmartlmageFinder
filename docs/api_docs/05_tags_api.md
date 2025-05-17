# 标签管理 API 文档

## 概述

SmartImageFinder 系统提供了一套完整的标签管理 API，用于获取、搜索和更新图片标签。标签是系统中的重要元数据，可以帮助用户有效地组织和查找图片。本文档详细介绍了标签管理相关的 API 端点、参数和使用方法。

## API 端点

### 1. 获取热门标签

获取系统中所有已使用标签及其使用频率，按使用频率排序。

**请求**:

- **方法**: GET
- **URL**: `/api/v1/tags/`
- **参数**:
  - `limit`: (可选) 返回标签数量，默认 50，范围 1-200

**成功响应**:

```json
{
  "status": "success",
  "code": 200,
  "message": "成功获取标签列表",
  "data": [
    {
      "tag": "自然",
      "count": 145
    },
    {
      "tag": "风景",
      "count": 120
    },
    {
      "tag": "城市",
      "count": 87
    },
    // ... 更多标签
  ],
  "metadata": {
    "total": 562
  },
  "error": null,
  "timestamp": "2025-05-16T10:30:45.123456",
  "request_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### 2. 搜索标签

搜索符合关键字的标签，主要用于前端的标签自动完成功能。

**请求**:

- **方法**: GET
- **URL**: `/api/v1/tags/search`
- **参数**:
  - `query`: (必需) 标签搜索关键字
  - `limit`: (可选) 返回标签数量，默认 20，范围 1-100

**示例请求**:

```
GET /api/v1/tags/search?query=风景&limit=10
```

**成功响应**:

```json
{
  "status": "success",
  "code": 200,
  "message": "成功搜索标签",
  "data": [
    "风景",
    "自然风景",
    "城市风景",
    "山水风景",
    "夜景"
  ],
  "metadata": {
    "total": 5
  },
  "error": null,
  "timestamp": "2025-05-16T10:31:22.123456",
  "request_id": "550e8400-e29b-41d4-a716-446655440001"
}
```

### 3. 根据标签获取图片

获取包含指定标签的所有图片，支持分页。

**请求**:

- **方法**: GET
- **URL**: `/api/v1/tags/by-tag/{tag}`
- **路径参数**:
  - `tag`: (必需) 标签名称
- **查询参数**:
  - `page`: (可选) 页码，默认 1
  - `page_size`: (可选) 每页数量，默认 20，范围 1-100

**示例请求**:

```
GET /api/v1/tags/by-tag/风景?page=1&page_size=10
```

**成功响应**:

```json
{
  "status": "success",
  "code": 200,
  "message": "成功获取标签 '风景' 的图片列表",
  "data": [
    {
      "id": 42,
      "filename": "mountains.jpg",
      "filepath": "/path/to/mountains.jpg",
      "title": "高山湖泊风景",
      "description": "这是一张拍摄于阿尔卑斯山的美丽山水风景照片，展示了湖泊和山脉的壮丽景色。",
      "file_size": 1542000,
      "file_type": "image/jpeg",
      "width": 1920,
      "height": 1080,
      "created_at": "2023-05-15 10:30:00",
      "updated_at": "2023-05-15 10:30:00",
      "metadata": {"camera": "Canon EOS R5", "exposure": "1/250"},
      "tags": ["山水", "自然", "风景", "湖泊"]
    },
    // ... 更多图片
  ],
  "metadata": {
    "pagination": {
      "page": 1,
      "page_size": 10,
      "total_items": 120,
      "total_pages": 12
    },
    "tag": "风景"
  },
  "error": null,
  "timestamp": "2025-05-16T10:32:15.123456",
  "request_id": "550e8400-e29b-41d4-a716-446655440002"
}
```

### 4. 根据多个标签获取图片

获取同时包含多个指定标签的图片，支持两种匹配模式：任一标签匹配（OR）或所有标签都匹配（AND）。

**请求**:

- **方法**: GET
- **URL**: `/api/v1/tags/by-multiple-tags`
- **参数**:
  - `tags`: (必需) 多个标签，以逗号分隔
  - `mode`: (可选) 匹配模式，可选值：
    - `or`: 匹配任一标签（默认）
    - `and`: 匹配所有标签
  - `page`: (可选) 页码，默认 1
  - `page_size`: (可选) 每页数量，默认 20，范围 1-100

**示例请求**:

```
GET /api/v1/tags/by-multiple-tags?tags=风景,自然,山水&mode=and&page=1&page_size=10
```

**成功响应**:

```json
{
  "status": "success",
  "code": 200,
  "message": "成功获取满足所有标签的图片列表",
  "data": [
    {
      "id": 42,
      "filename": "mountains.jpg",
      "filepath": "/path/to/mountains.jpg",
      "title": "高山湖泊风景",
      "description": "这是一张拍摄于阿尔卑斯山的美丽山水风景照片，展示了湖泊和山脉的壮丽景色。",
      "file_size": 1542000,
      "file_type": "image/jpeg",
      "width": 1920,
      "height": 1080,
      "created_at": "2023-05-15 10:30:00",
      "updated_at": "2023-05-15 10:30:00",
      "metadata": {"camera": "Canon EOS R5", "exposure": "1/250"},
      "tags": ["山水", "自然", "风景", "湖泊"]
    },
    // ... 更多图片
  ],
  "metadata": {
    "pagination": {
      "page": 1,
      "page_size": 10,
      "total_items": 45,
      "total_pages": 5
    },
    "tags": ["风景", "自然", "山水"],
    "mode": "and"
  },
  "error": null,
  "timestamp": "2025-05-16T10:33:45.123456",
  "request_id": "550e8400-e29b-41d4-a716-446655440003"
}
```

**错误响应** (无效的标签列表):

```json
{
  "status": "error",
  "code": 400,
  "message": "请提供有效的标签列表",
  "data": null,
  "error": {
    "code": "INVALID_TAGS",
    "message": "请提供有效的标签列表",
    "details": null
  },
  "metadata": {},
  "timestamp": "2025-05-16T10:34:15.123456",
  "request_id": "550e8400-e29b-41d4-a716-446655440004"
}
```

## 数据模型

### 标签信息

| 字段 | 类型 | 说明 |
|------|------|------|
| tag | string | 标签名称 |
| count | integer | 标签使用次数 |

### 更新标签请求

| 字段 | 类型 | 说明 |
|------|------|------|
| tags | array | 标签列表，包含字符串类型的标签名称 |

## 错误代码

| 错误代码 | HTTP 状态码 | 说明 |
|---------|------------|------|
| INVALID_TAGS | 400 | 提供的标签列表无效或为空 |
| NOT_FOUND | 404 | 指定的图片不存在 |

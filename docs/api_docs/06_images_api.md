# 图片管理 API 文档

## 概述

SmartImageFinder 系统提供了一套完整的图片管理 API，用于上传、获取、更新和删除图片。图片是系统的核心资源，本文档详细介绍了图片管理相关的 API 端点、参数和使用方法。

## API 端点

### 1. 获取图片列表

获取系统中的图片列表，支持分页、排序和多种过滤条件。

**请求**:

- **方法**: GET
- **URL**: `/api/images/`
- **参数**:
  - `page`: (可选) 页码，默认为 1
  - `page_size`: (可选) 每页数量，默认为 20，范围 1-100
  - `sort_by`: (可选) 排序字段，默认为 "created_at"
  - `order`: (可选) 排序方向，"asc" 或 "desc"，默认为 "desc"
  - `start_date`: (可选) 开始日期过滤，ISO 格式
  - `end_date`: (可选) 结束日期过滤，ISO 格式
  - `tags`: (可选) 标签过滤，可以是逗号分隔的字符串或数组

**成功响应**:

```json
{
  "status": "success",
  "code": 200,
  "message": "获取图片列表成功",
  "data": [
    {
      "id": 1,
      "filename": "sunset.jpg",
      "filepath": "/data/images/sunset.jpg",
      "title": "美丽的夕阳",
      "description": "这是一张夕阳的照片，拍摄于海边",
      "file_size": 1024000,
      "file_type": "image/jpeg",
      "width": 1920,
      "height": 1080,
      "created_at": "2025-05-10T14:30:00",
      "updated_at": "2025-05-10T14:30:00",
      "tags": ["夕阳", "海边", "自然"],
      "metadata": {
        "camera": "Canon EOS R5",
        "location": "三亚海滩"
      }
    },
    // 更多图片...
  ],
  "metadata": {
    "pagination": {
      "page": 1,
      "page_size": 20,
      "total_items": 150,
      "total_pages": 8
    }
  },
  "timestamp": "2025-05-16T12:00:00",
  "request_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**失败响应**:

```json
{
  "status": "error",
  "code": 500,
  "message": "获取图片列表失败",
  "error": {
    "code": "IMAGE_LIST_ERROR",
    "message": "获取图片列表失败: 数据库连接错误",
    "details": null
  },
  "metadata": {
    "pagination": {
      "page": 1,
      "page_size": 20,
      "total_items": 0,
      "total_pages": 0
    }
  },
  "timestamp": "2025-05-16T12:00:00",
  "request_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### 2. 获取单张图片

通过ID获取单张图片的详细信息。

**请求**:

- **方法**: GET
- **URL**: `/api/images/{image_id}`
- **路径参数**:
  - `image_id`: 图片ID

**成功响应**:

```json
{
  "status": "success",
  "code": 200,
  "message": "获取图片信息成功",
  "data": {
    "id": 1,
    "filename": "sunset.jpg",
    "filepath": "/data/images/sunset.jpg",
    "title": "美丽的夕阳",
    "description": "这是一张夕阳的照片，拍摄于海边",
    "file_size": 1024000,
    "file_type": "image/jpeg",
    "width": 1920,
    "height": 1080,
    "created_at": "2025-05-10T14:30:00",
    "updated_at": "2025-05-10T14:30:00",
    "tags": ["夕阳", "海边", "自然"],
    "metadata": {
      "camera": "Canon EOS R5",
      "location": "三亚海滩"
    }
  },
  "timestamp": "2025-05-16T12:00:00",
  "request_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**失败响应 - 图片不存在**:

```json
{
  "status": "error",
  "code": 404,
  "message": "图片不存在",
  "error": {
    "code": "IMAGE_NOT_FOUND",
    "message": "未找到ID为1234的图片",
    "details": null
  },
  "timestamp": "2025-05-16T12:00:00",
  "request_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### 3. 上传图片

上传一张或多张图片文件并存储到系统中。

**请求**:

- **方法**: POST
- **URL**: `/api/images/upload`
- **内容类型**: `multipart/form-data`
- **参数**:
  - `files`: (必需) 图片文件，可以上传多个文件
  - `title`: (可选) 图片标题
  - `description`: (可选) 图片描述
  - `tags`: (可选) 图片标签，JSON数组字符串，例如：`["自然", "风景"]`
  - `metadata`: (可选) 图片元数据，JSON字符串，例如：`{"location": "北京", "event": "旅行"}`

**成功响应**:

```json
{
  "status": "success",
  "code": 200,
  "message": "成功上传 2 个文件",
  "data": [
    {
      "id": 123,
      "filename": "mountain.jpg",
      "filepath": "/data/images/mountain.jpg",
      "title": "山脉风景",
      "description": "高山风景照",
      "file_size": 2048000,
      "file_type": "image/jpeg",
      "width": 3840,
      "height": 2160,
      "created_at": "2025-05-16T12:00:00",
      "updated_at": "2025-05-16T12:00:00",
      "tags": ["山", "自然", "风景"],
      "metadata": {
        "location": "黄山",
        "camera": "Sony A7R IV"
      }
    },
    {
      "id": 124,
      "filename": "lake.jpg",
      "filepath": "/data/images/lake.jpg",
      "title": "湖泊风景",
      "description": "平静的湖面",
      "file_size": 1536000,
      "file_type": "image/jpeg",
      "width": 2560,
      "height": 1440,
      "created_at": "2025-05-16T12:00:00",
      "updated_at": "2025-05-16T12:00:00",
      "tags": ["湖", "自然", "风景"],
      "metadata": {
        "location": "杭州西湖",
        "camera": "Canon EOS R5"
      }
    }
  ],
  "timestamp": "2025-05-16T12:00:00",
  "request_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**失败响应**:

```json
{
  "status": "error",
  "code": 500,
  "message": "上传图片失败",
  "error": {
    "code": "UPLOAD_ERROR",
    "message": "上传图片失败: 格式不支持",
    "details": {
      "file": "document.pdf",
      "supported_formats": ["jpg", "jpeg", "png", "gif", "webp"]
    }
  },
  "timestamp": "2025-05-16T12:00:00",
  "request_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### 4. 更新图片信息

更新已有图片的元信息，如标题、描述、标签和元数据。

**请求**:

- **方法**: PATCH
- **URL**: `/api/images/{image_id}`
- **内容类型**: `multipart/form-data`
- **路径参数**:
  - `image_id`: 图片ID
- **表单参数**:
  - `title`: (可选) 图片标题
  - `description`: (可选) 图片描述
  - `tags`: (可选) 图片标签，JSON数组字符串，例如：`["自然", "风景"]`
  - `metadata`: (可选) 图片元数据，JSON字符串，例如：`{"location": "北京", "event": "旅行"}`

**成功响应**:

```json
{
  "status": "success",
  "code": 200,
  "message": "图片信息更新成功",
  "data": {
    "id": 123,
    "filename": "mountain.jpg",
    "filepath": "/data/images/mountain.jpg",
    "title": "黄山日出",
    "description": "黄山日出美景，云海壮观",
    "file_size": 2048000,
    "file_type": "image/jpeg",
    "width": 3840,
    "height": 2160,
    "created_at": "2025-05-16T12:00:00",
    "updated_at": "2025-05-16T13:30:00",
    "tags": ["日出", "黄山", "云海", "自然", "风景"],
    "metadata": {
      "location": "安徽黄山",
      "camera": "Sony A7R IV",
      "time": "日出时分"
    }
  },
  "timestamp": "2025-05-16T13:30:00",
  "request_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**失败响应 - 无效的更新数据**:

```json
{
  "status": "error",
  "code": 400,
  "message": "无效的更新数据",
  "error": {
    "code": "INVALID_UPDATE_DATA",
    "message": "没有提供任何要更新的数据",
    "details": null
  },
  "timestamp": "2025-05-16T13:30:00",
  "request_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**失败响应 - 图片不存在**:

```json
{
  "status": "error",
  "code": 404,
  "message": "图片不存在",
  "error": {
    "code": "IMAGE_NOT_FOUND",
    "message": "未找到ID为1234的图片",
    "details": null
  },
  "timestamp": "2025-05-16T13:30:00",
  "request_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### 5. 删除图片

删除系统中的一张图片及其相关数据。

**请求**:

- **方法**: DELETE
- **URL**: `/api/images/{image_id}`
- **路径参数**:
  - `image_id`: 图片ID

**成功响应**:

```json
{
  "status": "success",
  "code": 200,
  "message": "图片删除成功",
  "data": {
    "id": 123,
    "filename": "mountain.jpg"
  },
  "timestamp": "2025-05-16T14:00:00",
  "request_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**失败响应 - 图片不存在**:

```json
{
  "status": "error",
  "code": 404,
  "message": "图片不存在",
  "error": {
    "code": "IMAGE_NOT_FOUND",
    "message": "未找到ID为1234的图片",
    "details": null
  },
  "timestamp": "2025-05-16T14:00:00",
  "request_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

## 实现说明

图片管理API由以下组件支持：

1. **文件处理**：系统会对上传的图片文件进行处理，包括格式验证、大小调整、缩略图生成等。
2. **向量索引**：对图片内容、标题和描述生成向量表示，用于后续的语义搜索。
3. **数据库存储**：图片元数据存储在数据库中，包括文件信息、用户提供的标题和描述等。
4. **文件系统存储**：实际图片文件保存在服务器文件系统中，使用结构化目录进行组织。

## 错误代码列表

| 错误代码 | 描述 | HTTP状态码 |
| --- | --- | --- |
| IMAGE_LIST_ERROR | 获取图片列表失败 | 500 |
| IMAGE_NOT_FOUND | 未找到指定的图片 | 404 |
| UPLOAD_ERROR | 上传图片失败 | 500 |
| FILE_TYPE_ERROR | 不支持的文件类型 | 400 |
| FILE_SIZE_ERROR | 文件大小超出限制 | 400 |
| INVALID_UPDATE_DATA | 无效的更新数据 | 400 |
| DELETE_ERROR | 删除图片失败 | 500 |

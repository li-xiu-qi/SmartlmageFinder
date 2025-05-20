# 标签管理 API

## 简介

标签管理API提供了一系列接口，用于获取、搜索和管理图片标签。标签是SmartImageFinder系统中组织和分类图片的重要方式，通过这些API可以实现标签的查询、过滤和更新操作。

## 接口详情

### 获取所有标签

**请求方式**: GET

**路径**: `/api/v1/tags/`

**说明**: 获取系统中所有已使用标签及其使用频率

#### 查询参数

| 参数名 | 类型 | 必填 | 默认值 | 描述 |
|-------|------|------|-------|-----|
| limit | integer | 否 | 50 | 返回标签数量，最大值为200 |

#### 响应

```json
{
  "status": "success",
  "code": 200,
  "message": "成功获取标签列表",
  "data": [
    {
      "tag": "风景",
      "count": 125
    },
    {
      "tag": "自然",
      "count": 98
    },
    {
      "tag": "城市",
      "count": 87
    },
    // ...更多标签
  ],
  "metadata": {
    "total": 500
  },
  "timestamp": "2023-05-19T12:34:56.789Z",
  "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

### 搜索标签

**请求方式**: GET

**路径**: `/api/v1/tags/search`

**说明**: 搜索符合关键字的标签，用于自动完成功能

#### 查询参数

| 参数名 | 类型 | 必填 | 默认值 | 描述 |
|-------|------|------|-------|-----|
| query | string | 是 | - | 标签搜索关键字 |
| limit | integer | 否 | 20 | 返回标签数量，最大值为100 |

#### 响应

```json
{
  "status": "success",
  "code": 200,
  "message": "成功搜索标签",
  "data": [
    "自然风景",
    "自然光",
    "自然色彩",
    "自然美",
    // ...更多匹配的标签
  ],
  "metadata": {
    "total": 15
  },
  "timestamp": "2023-05-19T12:34:56.789Z",
  "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

### 获取具有特定标签的图片

**请求方式**: GET

**路径**: `/api/v1/tags/by-tag/{tag}`

**说明**: 根据标签获取图片列表

#### 路径参数

| 参数名 | 类型 | 必填 | 描述 |
|-------|------|------|-----|
| tag | string | 是 | 标签名称 |

#### 查询参数

| 参数名 | 类型 | 必填 | 默认值 | 描述 |
|-------|------|------|-------|-----|
| page | integer | 否 | 1 | 页码，从1开始 |
| page_size | integer | 否 | 20 | 每页数量，最大值为100 |

#### 响应

```json
{
  "status": "success",
  "code": 200,
  "message": "成功获取标签 '自然' 的图片列表",
  "data": [
    {
      "id": 1,
      "filename": "example.jpg",
      "title": "森林风景",
      "description": "美丽的自然森林风景",
      "tags": ["自然", "森林", "风景"],
      "url": "/api/v1/images/1/file",
      "thumbnail_url": "/api/v1/images/1/thumbnail",
      "created_at": "2023-05-19T12:34:56.789Z",
      "updated_at": "2023-05-20T10:15:30.123Z",
      "metadata": {
        "width": 1920,
        "height": 1080,
        "size_kb": 2500
      }
    },
    // ...更多图片
  ],
  "metadata": {
    "pagination": {
      "page": 1,
      "page_size": 20,
      "total_items": 98,
      "total_pages": 5
    },
    "tag": "自然"
  },
  "timestamp": "2023-05-19T12:34:56.789Z",
  "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

### 获取具有多个标签的图片

**请求方式**: GET

**路径**: `/api/v1/tags/by-multiple-tags`

**说明**: 根据多个标签获取图片列表

#### 查询参数

| 参数名 | 类型 | 必填 | 默认值 | 描述 |
|-------|------|------|-------|-----|
| tags | string | 是 | - | 多个标签，以逗号分隔 |
| mode | string | 否 | "or" | 匹配模式：'or'表示匹配任一标签，'and'表示匹配所有标签 |
| page | integer | 否 | 1 | 页码，从1开始 |
| page_size | integer | 否 | 20 | 每页数量，最大值为100 |

#### 响应

```json
{
  "status": "success",
  "code": 200,
  "message": "成功获取满足任一标签的图片列表",
  "data": [
    {
      "id": 1,
      "filename": "example.jpg",
      "title": "森林风景",
      "description": "美丽的自然森林风景",
      "tags": ["自然", "森林", "风景"],
      "url": "/api/v1/images/1/file",
      "thumbnail_url": "/api/v1/images/1/thumbnail",
      "created_at": "2023-05-19T12:34:56.789Z",
      "updated_at": "2023-05-20T10:15:30.123Z",
      "metadata": {
        "width": 1920,
        "height": 1080,
        "size_kb": 2500
      }
    },
    // ...更多图片
  ],
  "metadata": {
    "pagination": {
      "page": 1,
      "page_size": 20,
      "total_items": 150,
      "total_pages": 8
    },
    "tags": ["自然", "风景"],
    "mode": "or"
  },
  "timestamp": "2023-05-19T12:34:56.789Z",
  "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

### 更新图片标签

**请求方式**: POST

**路径**: `/api/v1/tags/{image_id}/update`

**说明**: 为图片添加标签

#### 路径参数

| 参数名 | 类型 | 必填 | 描述 |
|-------|------|------|-----|
| image_id | integer | 是 | 图片ID |

#### 请求体

```json
{
  "tags": ["自然", "风景", "山脉"]
}
```

#### 响应

```json
{
  "status": "success",
  "code": 200,
  "message": "标签添加成功",
  "data": {
    "tags": ["自然", "风景", "山脉"]
  },
  "timestamp": "2023-05-19T12:34:56.789Z",
  "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

## 错误代码

| 错误代码 | HTTP状态码 | 描述 |
|---------|-----------|-----|
| INVALID_TAGS | 400 | 无效的标签列表 |
| IMAGE_NOT_FOUND | 404 | 指定ID的图片不存在 |
| DATABASE_ERROR | 500 | 数据库操作错误 |

## 最佳实践

1. 标签应该简洁明了，使用常见词汇，便于搜索和分类。

2. 推荐使用2-4个标签为每张图片分类，过多的标签可能会降低搜索精度。

3. 使用多标签搜索时，"and"模式（匹配所有标签）通常会提供更精确的结果，而"or"模式（匹配任一标签）会返回更多相关结果。

4. 标签搜索API可以用于实现自动完成功能，提高用户体验。

5. 定期分析热门标签可以了解用户兴趣和内容趋势。

6. 更新图片标签时，提供完整的标签列表，而不仅仅是要添加的新标签，因为API会替换而不是追加标签。

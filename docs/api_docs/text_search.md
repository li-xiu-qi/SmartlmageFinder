# 文本搜索 API

## 简介

文本搜索API允许通过文本关键词或描述搜索图片，支持多种搜索模式，包括标题匹配、描述匹配和向量语义搜索。

## 接口详情

### 文本搜索

**请求方式**: GET

**路径**: `/api/v1/search/text`

**说明**: 根据输入的文本内容搜索相关图片

#### 请求参数

| 参数名 | 类型 | 必填 | 默认值 | 描述 |
|-------|------|------|-------|-----|
| q | string | 是 | - | 搜索文本 |
| search_type | string | 否 | "both" | 搜索类型：<br>- title: 仅搜索标题<br>- description: 仅搜索描述<br>- both: 搜索标题和描述<br>- vector: 使用向量语义搜索 |
| vector_targets | array | 否 | ["title", "description", "image"] | 向量搜索目标，仅在search_type为vector时有效。可选值：<br>- title: 标题<br>- description: 描述<br>- image: 图片内容 |
| page | integer | 否 | 1 | 页码，从1开始 |
| page_size | integer | 否 | 20 | 每页返回的结果数量 |
| min_score | float | 否 | 0.0 | 搜索结果的最低相似度分数 (0.0-1.0) |
| sort_by | string | 否 | "score" | 排序字段 |
| order | string | 否 | "desc" | 排序方向：asc(升序)或desc(降序) |
| start_date | string | 否 | null | 开始日期过滤（ISO格式：YYYY-MM-DD） |
| end_date | string | 否 | null | 结束日期过滤（ISO格式：YYYY-MM-DD） |
| tags | array | 否 | null | 标签过滤，例如：tags[]=风景&tags[]=自然 |

#### 响应

```json
{
  "status": "success",
  "code": 200,
  "message": "搜索成功",
  "data": [
    {
      "id": 1,
      "filename": "example.jpg",
      "title": "风景照片",
      "description": "美丽的自然风景",
      "tags": ["风景", "自然", "户外"],
      "url": "/api/v1/images/1/file",
      "thumbnail_url": "/api/v1/images/1/thumbnail",
      "score": 0.95,
      "created_at": "2023-05-19T12:34:56.789Z",
      "updated_at": "2023-05-20T10:15:30.123Z",
      "metadata": {
        "width": 1920,
        "height": 1080,
        "size_kb": 2500
      }
    },
    // ...更多结果
  ],
  "metadata": {
    "pagination": {
      "page": 1,
      "page_size": 20,
      "total_items": 100,
      "total_pages": 5
    },
    "search_info": {
      "query": "风景",
      "search_type": "vector",
      "time_ms": 150
    }
  },
  "timestamp": "2023-05-19T12:34:56.789Z",
  "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

#### 响应字段说明

| 字段 | 类型 | 描述 |
|-----|------|-----|
| id | integer | 图片ID |
| filename | string | 文件名 |
| title | string | 图片标题 |
| description | string | 图片描述 |
| tags | array | 图片标签 |
| url | string | 图片URL |
| thumbnail_url | string | 缩略图URL |
| score | float | 搜索相似度分数 (0.0-1.0) |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |
| metadata | object | 图片元数据 |

#### 错误代码

| 错误代码 | HTTP状态码 | 描述 |
|---------|-----------|-----|
| TEXT_SEARCH_ERROR | 500 | 文本搜索处理错误 |
| VALIDATION_ERROR | 400 | 请求参数验证失败 |
| DATABASE_ERROR | 500 | 数据库操作错误 |

#### 示例

**基本文本匹配搜索**:

```
GET /api/v1/search/text?q=风景照片&search_type=both
```

**向量语义搜索**:

```
GET /api/v1/search/text?q=山水风景&search_type=vector&vector_targets[]=title&vector_targets[]=description
```

**带标签过滤的文本搜索**:

```
GET /api/v1/search/text?q=自然&search_type=both&tags[]=风景&tags[]=自然
```

## 最佳实践

1. 使用`search_type=vector`进行语义搜索时，能够找到与查询文本在语义上相似的图片，即使图片的标题和描述中不包含完全匹配的关键词。

2. 使用`search_type=title`或`search_type=description`进行精确匹配搜索，当您确切知道图片的标题或描述中包含的关键词时更为有效。

3. 使用标签过滤可以缩小搜索范围，提高搜索精度。

4. 对于较大的图片集合，适当调整`page_size`参数以平衡响应时间和结果数量。

# 过滤搜索 API

## 简介

过滤搜索API提供了一种基于多种条件组合过滤图片的方法，无需提供搜索关键词。该API允许用户通过日期范围、标签、元数据等多种条件进行图片筛选。

## 接口详情

### 过滤搜索

**请求方式**: GET

**路径**: `/api/v1/search/filtered`

**说明**: 根据各种过滤条件搜索图片

#### 请求参数

| 参数名 | 类型 | 必填 | 默认值 | 描述 |
|-------|------|------|-------|-----|
| page | integer | 否 | 1 | 页码，从1开始 |
| page_size | integer | 否 | 20 | 每页返回的结果数量 |
| start_date | string | 否 | null | 开始日期过滤（ISO格式：YYYY-MM-DD） |
| end_date | string | 否 | null | 结束日期过滤（ISO格式：YYYY-MM-DD） |
| tags | array | 否 | null | 标签过滤，例如：tags[]=风景&tags[]=自然 |
| sort_by | string | 否 | "created_at" | 排序字段 |
| order | string | 否 | "desc" | 排序方向：asc(升序)或desc(降序) |
| min_width | integer | 否 | null | 最小宽度（像素） |
| min_height | integer | 否 | null | 最小高度（像素） |
| max_width | integer | 否 | null | 最大宽度（像素） |
| max_height | integer | 否 | null | 最大高度（像素） |

> **注意**: 至少需要提供一个过滤条件，否则将返回错误。

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
      "title": "冬日雪景",
      "description": "冬季森林中的雪景",
      "tags": ["冬季", "雪", "森林", "自然"],
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
      "filters": {
        "tags": ["冬季", "雪"],
        "start_date": "2023-01-01",
        "end_date": "2023-12-31"
      },
      "time_ms": 120
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
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |
| metadata | object | 图片元数据 |

#### 错误代码

| 错误代码 | HTTP状态码 | 描述 |
|---------|-----------|-----|
| FILTER_SEARCH_ERROR | 500 | 过滤搜索处理错误 |
| NO_FILTERS | 400 | 未提供任何过滤条件 |
| VALIDATION_ERROR | 400 | 请求参数验证失败 |
| DATABASE_ERROR | 500 | 数据库操作错误 |

#### 示例

**按标签和日期范围过滤**:

```
GET /api/v1/search/filtered?tags[]=自然&tags[]=风景&start_date=2023-01-01&end_date=2023-12-31
```

**按图片尺寸过滤**:

```
GET /api/v1/search/filtered?min_width=1920&min_height=1080&tags[]=高清
```

**按创建时间排序**:

```
GET /api/v1/search/filtered?tags[]=人物&sort_by=created_at&order=desc
```

## 最佳实践

1. 过滤搜索API非常适合浏览和探索图片库，而不是查找特定的图片。

2. 组合多个过滤条件可以缩小结果范围，例如同时使用标签过滤和日期范围。

3. 使用`sort_by`和`order`参数可以控制结果的排序方式，有助于更有效地浏览结果。

4. 对于高分辨率图片的筛选，使用`min_width`和`min_height`参数很有帮助。

5. 根据UI需求调整`page_size`参数，以便在单页显示适量的结果。

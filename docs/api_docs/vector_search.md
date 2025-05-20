# 向量搜索 API

## 简介

向量搜索API提供了一种高级搜索功能，它允许您通过文本查询，在系统的向量索引中查找相似的图片。这种搜索方式基于语义相似性，而不仅仅是关键词匹配。

## 接口详情

### 向量搜索

**请求方式**: GET

**路径**: `/api/v1/search/by-vector`

**说明**: 将输入文本转换为向量，然后在指定向量类型中搜索相似图片

#### 请求参数

| 参数名 | 类型 | 必填 | 默认值 | 描述 |
|-------|------|------|-------|-----|
| q | string | 是 | - | 搜索文本，将转换为向量 |
| vector_type | string | 否 | "image" | 要搜索的向量类型，可选值：<br>- title: 在标题向量中搜索<br>- description: 在描述向量中搜索<br>- image: 在图片内容向量中搜索 |
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
      "title": "城市天际线",
      "description": "现代城市的夜景天际线",
      "tags": ["城市", "夜景", "建筑"],
      "url": "/api/v1/images/1/file",
      "thumbnail_url": "/api/v1/images/1/thumbnail",
      "score": 0.87,
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
      "query": "城市景观",
      "vector_type": "image",
      "time_ms": 180
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
| score | float | 相似度分数 (0.0-1.0) |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |
| metadata | object | 图片元数据 |

#### 错误代码

| 错误代码 | HTTP状态码 | 描述 |
|---------|-----------|-----|
| VECTOR_SEARCH_ERROR | 500 | 向量搜索处理错误 |
| VALIDATION_ERROR | 400 | 请求参数验证失败 |
| DATABASE_ERROR | 500 | 数据库操作错误 |

#### 示例

**在图片向量中搜索**:

```
GET /api/v1/search/by-vector?q=城市夜景&vector_type=image
```

**在标题向量中搜索**:

```
GET /api/v1/search/by-vector?q=美丽的山景&vector_type=title&tags[]=风景&tags[]=山
```

**在描述向量中搜索并限制结果数量**:

```
GET /api/v1/search/by-vector?q=沙滩度假&vector_type=description&page_size=10
```

## 最佳实践

1. 向量搜索基于语义理解，所以您可以使用自然语言描述来搜索，不仅限于关键词。例如，"夕阳西下的海滩"会返回与这个场景相似的图片，即使图片的标题和描述中没有完全匹配的词语。

2. 根据搜索需求选择合适的`vector_type`：
   - 使用`image`查找视觉内容相似的图片
   - 使用`title`查找主题相似的图片
   - 使用`description`查找详细内容相似的图片

3. 使用标签过滤可以缩小搜索范围，提高相关性。

4. 调整`min_score`参数可以控制结果的质量，较高的值会返回相似度更高的结果，但数量可能会减少。

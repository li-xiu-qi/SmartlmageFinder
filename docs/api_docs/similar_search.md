# 相似搜索 API

## 简介

相似搜索API允许用户根据已存在于系统中的图片ID，查找与其相似的其他图片。这种搜索方式非常适合发现与用户已经喜欢的图片相似的内容。

## 接口详情

### 相似图片搜索

**请求方式**: GET

**路径**: `/api/v1/search/similar/{image_id}`

**说明**: 根据指定图片ID查找相似图片

#### 路径参数

| 参数名 | 类型 | 必填 | 描述 |
|-------|------|------|-----|
| image_id | integer | 是 | 图片ID，用于查找相似图片 |

#### 查询参数

| 参数名 | 类型 | 必填 | 默认值 | 描述 |
|-------|------|------|-------|-----|
| vector_type | string | 否 | "image" | 搜索目标向量类型，可选值：<br>- image: 使用图片视觉特征<br>- title: 使用标题文本特征<br>- description: 使用描述文本特征 |
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
      "id": 2,
      "filename": "similar_example.jpg",
      "title": "山脉风景",
      "description": "壮观的山脉全景",
      "tags": ["山", "自然", "风景"],
      "url": "/api/v1/images/2/file",
      "thumbnail_url": "/api/v1/images/2/thumbnail",
      "score": 0.92,
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
      "total_items": 50,
      "total_pages": 3
    },
    "search_info": {
      "source_image_id": 1,
      "vector_type": "image",
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
| score | float | 相似度分数 (0.0-1.0) |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |
| metadata | object | 图片元数据 |

#### 错误代码

| 错误代码 | HTTP状态码 | 描述 |
|---------|-----------|-----|
| SIMILAR_SEARCH_ERROR | 500 | 相似搜索处理错误 |
| IMAGE_NOT_FOUND | 404 | 指定ID的图片不存在 |
| VALIDATION_ERROR | 400 | 请求参数验证失败 |
| DATABASE_ERROR | 500 | 数据库操作错误 |

#### 示例

**基于图片ID查找视觉相似的图片**:

```
GET /api/v1/search/similar/1?vector_type=image
```

**查找标题相似的图片并过滤标签**:

```
GET /api/v1/search/similar/1?vector_type=title&tags[]=自然&tags[]=风景
```

**查找描述相似的图片并自定义分页**:

```
GET /api/v1/search/similar/1?vector_type=description&page=2&page_size=10
```

## 最佳实践

1. 相似搜索API是实现"相关图片"或"您可能也喜欢"等功能的理想选择。

2. 根据不同需求选择合适的`vector_type`：
   - 使用`image`寻找视觉上相似的图片
   - 使用`title`寻找主题相似的图片
   - 使用`description`寻找内容描述相似的图片

3. 在图片详情页面可以集成该API，向用户展示相关图片，增强用户体验。

4. 搜索结果默认不包含源图片本身（exclude_self=True），这样可以避免在结果中显示用户正在查看的图片。

5. 结合标签过滤可以进一步提高相似搜索结果的相关性。

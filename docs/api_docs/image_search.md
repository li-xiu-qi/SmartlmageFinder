# 图片搜索 API

## 简介

图片搜索API允许用户通过上传一张图片来搜索数据库中相似的图片。系统会分析上传的图片，并根据视觉特征找到相似的图片。

## 接口详情

### 图片搜索

**请求方式**: POST

**路径**: `/api/v1/search/image`

**说明**: 通过上传图片搜索相似图片

#### 请求参数

| 参数名 | 类型 | 必填 | 默认值 | 描述 |
|-------|------|------|-------|-----|
| file | file | 是 | - | 要搜索的图片文件 |
| search_targets | array | 否 | ["image"] | 搜索目标类型，可选值：<br>- image: 搜索视觉上相似的图片<br>- title: 搜索标题相似的图片<br>- description: 搜索描述相似的图片 |
| page | integer | 否 | 1 | 页码，从1开始 |
| page_size | integer | 否 | 20 | 每页返回的结果数量 |
| min_score | float | 否 | 0.0 | 搜索结果的最低相似度分数 (0.0-1.0) |
| tags | array | 否 | null | 标签过滤，例如：tags=风景&tags=自然 |
| start_date | string | 否 | null | 开始日期过滤（ISO格式：YYYY-MM-DD） |
| end_date | string | 否 | null | 结束日期过滤（ISO格式：YYYY-MM-DD） |

> **注意**: 由于此API使用POST方法并包含文件上传，请使用`multipart/form-data`格式发送请求。

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
      "title": "海滩风景",
      "description": "美丽的海滩日落场景",
      "tags": ["海滩", "日落", "自然"],
      "url": "/api/v1/images/1/file",
      "thumbnail_url": "/api/v1/images/1/thumbnail",
      "score": 0.89,
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
      "filename": "uploaded_image.jpg",
      "search_targets": ["image"],
      "time_ms": 250
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
| IMAGE_SEARCH_ERROR | 500 | 图片搜索处理错误 |
| INVALID_FILE | 400 | 无效的文件格式或损坏的图片文件 |
| FILE_TOO_LARGE | 400 | 上传文件太大 |
| DATABASE_ERROR | 500 | 数据库操作错误 |

#### 示例

**使用cURL进行请求**:

```bash
curl -X POST "http://example.com/api/v1/search/image" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/image.jpg" \
  -F "search_targets=image" \
  -F "page=1" \
  -F "page_size=20" \
  -F "tags=风景" \
  -F "tags=自然"
```

**使用JavaScript Fetch API**:

```javascript
const formData = new FormData();
formData.append('file', imageFile);
formData.append('search_targets', 'image');
formData.append('tags', '风景');
formData.append('tags', '自然');

fetch('http://example.com/api/v1/search/image', {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(data => console.log(data))
.catch(error => console.error('Error:', error));
```

## 最佳实践

1. 上传的图片文件应该保持合理的大小，通常建议不超过10MB，以避免上传时间过长。

2. 系统支持常用的图片格式，包括JPEG、PNG、WebP、GIF等。对于最佳结果，推荐使用JPEG或PNG格式。

3. 通过组合不同的`search_targets`可以获得更全面的搜索结果：
   - 仅使用`image`可以找到视觉上相似的图片
   - 添加`title`和`description`可以扩展搜索结果，包括内容上相关的图片

4. 使用标签过滤可以缩小搜索范围，提高结果的相关性。例如，当搜索"海滩"图片时，可以添加"日落"、"海洋"等标签进行过滤。

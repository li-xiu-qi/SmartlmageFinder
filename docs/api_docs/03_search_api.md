# 搜索功能 API 文档

## 概述

SmartImageFinder 系统提供了强大的图片搜索功能，支持多种搜索模式，包括文本搜索、图像搜索和相似图片搜索。搜索系统基于向量数据库和传统文本匹配技术，能够实现高效、准确的图片检索。本文档详细介绍搜索API的使用方法和技术实现。

## 技术基础

搜索系统结合了两种核心技术：

1. **文本匹配搜索**：基于传统的数据库文本模糊匹配（LIKE 查询）实现，主要用于标题和描述的纯文本搜索。

2. **向量相似度搜索**：基于深度学习模型生成的向量嵌入，通过计算向量之间的距离来查找相似内容。系统分别为图像、标题和描述生成向量表示，存储在专用的向量表中。结果中会返回距离（distance，越小越相似）和相似度评分（score，范围为0-1，计算方式为1-distance，值越高表示越相似）。

## API 端点

### 1. 文本搜索

通过文本关键词搜索图片，可以选择搜索范围和过滤条件。

**请求**:

- **方法**: GET
- **URL**: `/api/search/text`
- **参数**:
  - `q`: (必需) 搜索关键词
  - `search_type`: (可选) 搜索类型，可选值：
    - `title`: 仅搜索标题
    - `description`: 仅搜索描述
    - `both`: 同时搜索标题和描述（默认）
    - `vector`: 使用向量搜索
    - `hybrid`: 使用混合搜索（结合向量和文本）
  - `vector_targets`: (可选) 向量搜索目标，当 search_type 为 vector 或 hybrid 时有效，可选值（可多选）：
    - `title`: 标题向量
    - `description`: 描述向量
    - `image`: 图像向量
  - `filename`: (可选) 按文件名过滤
  - `tags`: (可选) 按标签过滤，可提供多个标签
  - `start_date`: (可选) 开始日期，格式：YYYY-MM-DD HH:MM:SS
  - `end_date`: (可选) 结束日期，格式：YYYY-MM-DD HH:MM:SS
  - `limit`: (可选) 返回结果数量限制，默认20
  - `offset`: (可选) 分页偏移，默认0

**示例请求**:

```http
GET /api/search/text?q=山水风景&search_type=hybrid&vector_targets=title&vector_targets=description&tags=自然&tags=风景&limit=10
```

**成功响应**:

```json
{
  "status": "success",
  "code": 200,
  "message": "文本搜索成功",
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
      "tags": ["山水", "自然", "风景", "湖泊"],
      "distance": 0.11,
      "score": 0.89
    }
  ],
  "metadata": {
    "pagination": {
      "page": 1,
      "page_size": 10,
      "total_items": 57,
      "total_pages": 6
    }
  },
  "error": null,
  "timestamp": "2025-05-16T10:30:45.123456",
  "request_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### 2. 图像搜索

上传一张图片，查找数据库中相似的图片。

**请求**:

- **方法**: POST
- **URL**: `/api/search/image`
- **内容类型**: `multipart/form-data`
- **参数**:
  - `file`: (必需) 用于搜索的图片文件
  - `search_targets`: (可选) 搜索目标，可选值（可多选）：
    - `image`: 图像向量（默认）
    - `title`: 标题向量
    - `description`: 描述向量
  - `search_type`: (可选) 搜索类型，可选值：
    - `vector`: 仅向量搜索（默认）
    - `hybrid`: 混合搜索
  - `filename`: (可选) 按文件名过滤
  - `tags`: (可选) 按标签过滤，可提供多个标签
  - `start_date`: (可选) 开始日期，格式：YYYY-MM-DD HH:MM:SS
  - `end_date`: (可选) 结束日期，格式：YYYY-MM-DD HH:MM:SS
  - `limit`: (可选) 返回结果数量限制，默认20
  - `offset`: (可选) 分页偏移，默认0

**成功响应**:

```json
{
  "status": "success",
  "code": 200,
  "message": "图像搜索成功",
  "data": [
    {
      "id": 28,
      "filename": "sunset_beach.jpg",
      "filepath": "/path/to/sunset_beach.jpg",
      "title": "夕阳海滩",
      "description": "日落时分的海滩美景，金色的阳光洒在沙滩上",
      "file_size": 1024000,
      "file_type": "image/jpeg",
      "width": 1920,
      "height": 1080,
      "created_at": "2023-06-10 18:30:00",
      "updated_at": "2023-06-10 18:30:00",
      "metadata": {"camera": "Sony A7III", "exposure": "1/125"},
      "tags": ["海滩", "日落", "风景"],
      "distance": 0.15,
      "score": 0.85
    }
  ],
  "metadata": {
    "pagination": {
      "page": 1,
      "page_size": 20,
      "total_items": 35,
      "total_pages": 2
    }
  },
  "error": null,
  "timestamp": "2025-05-16T11:45:22.123456",
  "request_id": "550e8400-e29b-41d4-a716-446655440012"
}
```

### 3. 相似图片搜索

通过图片ID查找数据库中相似的其他图片。

**请求**:

- **方法**: GET
- **URL**: `/api/search/similar/{image_id}`
- **路径参数**:
  - `image_id`: (必需) 用于搜索的图片ID
- **查询参数**:
  - `search_targets`: (可选) 搜索目标，可选值（可多选）：
    - `image`: 图像向量（默认）
    - `title`: 标题向量
    - `description`: 描述向量
  - `search_type`: (可选) 搜索类型，可选值：
    - `vector`: 仅向量搜索（默认）
    - `hybrid`: 混合搜索
  - `filename`: (可选) 按文件名过滤
  - `tags`: (可选) 按标签过滤，可提供多个标签
  - `start_date`: (可选) 开始日期，格式：YYYY-MM-DD HH:MM:SS
  - `end_date`: (可选) 结束日期，格式：YYYY-MM-DD HH:MM:SS
  - `limit`: (可选) 返回结果数量限制，默认20
  - `offset`: (可选) 分页偏移，默认0

**示例请求**:

```http
GET /api/search/similar/42?search_targets=image&search_type=hybrid&limit=5
```

**成功响应**:

```json
{
  "status": "success",
  "code": 200,
  "message": "相似图像搜索成功",
  "data": [
    {
      "id": 45,
      "filename": "alpine_lake.jpg",
      "filepath": "/path/to/alpine_lake.jpg",
      "title": "高山湖泊",
      "description": "阿尔卑斯山脉中的清澈湖泊，被雪山环绕",
      "file_size": 1348000,
      "file_type": "image/jpeg",
      "width": 2048,
      "height": 1365,
      "created_at": "2023-05-20 14:15:00",
      "updated_at": "2023-05-20 14:15:00",
      "metadata": {"camera": "Nikon Z7", "exposure": "1/200"},
      "tags": ["山水", "湖泊", "自然"],
      "distance": 0.12,
      "score": 0.88
    }
  ],
  "metadata": {
    "pagination": {
      "page": 1,
      "page_size": 5,
      "total_items": 23,
      "total_pages": 5
    }
  },
  "error": null,
  "timestamp": "2025-05-16T12:15:33.123456",
  "request_id": "550e8400-e29b-41d4-a716-446655440024"
}
```

## 搜索类型详解

### 文本匹配搜索

当设置 `search_type` 为 `title`, `description` 或 `both` 时，系统使用传统的 SQL LIKE 匹配进行搜索。这种搜索方式速度快，但语义理解能力有限。

```sql
SELECT * FROM images 
WHERE title LIKE '%山水%' OR description LIKE '%山水%'
ORDER BY created_at DESC
LIMIT 20 OFFSET 0
```

### 向量搜索

当设置 `search_type` 为 `vector` 时，系统使用向量相似度进行搜索：

1. 将查询文本或图像转换为向量表示
2. 在指定的向量表（标题向量、描述向量或图像向量）中查找最相似的向量
3. 计算距离并转换为相似度得分（score = 1 - distance）
4. 返回相似度最高的结果

向量搜索能够理解语义相似性，例如"海滩日落"的查询可能会匹配到描述为"黄昏时的沙滩"的图片。

### 混合搜索

当设置 `search_type` 为 `hybrid` 时，系统综合使用向量搜索和文本匹配，为每个结果计算综合得分，提供更准确的搜索结果。混合搜索的步骤包括：

1. 对每个搜索目标类型分别执行向量搜索
2. 合并结果并计算综合得分
3. 去除重复项，保留得分最高的结果
4. 按得分排序并返回

## 过滤机制

所有搜索端点都支持以下过滤条件：

- **文件名过滤**：按文件名进行模糊匹配
- **标签过滤**：只返回包含指定标签的图片
- **时间范围过滤**：按图片创建时间过滤

过滤条件会在执行向量搜索或文本搜索前应用，以减少需要搜索的数据量，提高效率。系统使用 `basic_search.py` 中的 `get_filtered_image_ids` 函数实现这一功能。

## 技术实现

### 基本搜索流程

1. 根据过滤条件筛选出符合条件的图片ID列表
2. 根据搜索类型执行对应的搜索算法
3. 处理结果，包括排序、去重和分页
4. 返回最终结果，包括距离和得分信息

### 向量搜索实现

系统使用SQLite和向量扩展实现向量搜索，关键SQL示例：

```sql
SELECT
    img.id,
    img.filename,
    img.filepath,
    img.title,
    img.description,
    img.file_size,
    img.file_type,
    img.width,
    img.height,
    img.created_at,
    img.updated_at,
    img.metadata,
    img.tags,
    vec.distance
FROM
    {vector_table} AS vec
JOIN
    images AS img ON vec.image_id = img.id
WHERE
    vec.image_id IN ({filtered_ids_str})
    AND vec.embedding MATCH ? AND k = ?;
```

其中：
- `{vector_table}` 可以是 `image_vectors`、`title_vectors` 或 `description_vectors`
- `MATCH` 和 `k` 是向量搜索扩展的特殊语法，用于执行K近邻（KNN）搜索
- 搜索返回的 `distance` 表示向量之间的距离，越小表示越相似

### 基于图像ID的搜索

通过图像ID查找相似图像的实现利用了SQL的WITH子句，先获取指定ID的向量，然后再用这个向量进行搜索：

```sql
WITH query_vector AS (
    SELECT embedding 
    FROM {vector_table}
    WHERE image_id = ?
)
SELECT 
    img.id,
    -- 其他字段
    res.distance
FROM (
    SELECT 
        image_id,
        distance
    FROM 
        {vector_table}
    WHERE 
        image_id IN ({filtered_ids_str})
        AND embedding MATCH (SELECT embedding FROM query_vector)
        AND k = ?
) AS res
JOIN 
    images AS img ON res.image_id = img.id
ORDER BY 
    res.distance ASC
```

### 混合搜索实现

混合搜索会对每个搜索目标（图像、标题、描述）分别执行向量搜索，然后将结果合并，计算综合得分：

1. 对每个目标类型执行向量搜索
2. 将所有结果合并到一个集合中
3. 对于同一个图像在多个搜索目标中出现的情况，保留最高得分
4. 计算每个结果的综合得分（1 - 距离）
5. 根据得分排序结果

## 使用建议

1. **搜索类型选择**：
   - 简单关键词匹配使用 `both` 类型
   - 需要语义理解使用 `vector` 类型
   - 需要最全面的结果使用 `hybrid` 类型

2. **搜索目标选择**：
   - 查找视觉相似图片，使用 `image` 目标
   - 查找内容相似但外观可能不同的图片，使用 `title` 和 `description` 目标
   - 组合多个目标可以获得更全面的结果

3. **性能考虑**：
   - 向量搜索比文本匹配更耗费资源
   - 合理设置 `limit` 参数，避免返回过多结果
   - 使用过滤条件缩小搜索范围

## 错误代码

| HTTP 状态码 | 错误代码 | 错误描述 | 可能原因 |
|------------|---------|---------|---------|
| 400 | INVALID_SEARCH_TYPE | 不支持的搜索类型 | 提供了无效的 search_type 值 |
| 404 | IMAGE_NOT_FOUND | 未找到图像 | 提供的 image_id 不存在 |
| 500 | DATABASE_ERROR | 数据库错误 | 数据库连接或查询问题 |
| 500 | SEARCH_ERROR | 搜索失败 | 一般性搜索错误 |
| 500 | IMAGE_SEARCH_ERROR | 图像搜索失败 | 图片处理或向量生成失败 |
| 500 | VECTOR_SEARCH_ERROR | 向量搜索错误 | 向量搜索过程中的错误 |
| 500 | SIMILAR_SEARCH_ERROR | 相似搜索失败 | 相似图像搜索过程中的错误 |

# 搜索 API

## 简介

SmartImageFinder提供了多种强大的搜索功能，使用户能够通过不同方式查找所需的图片。搜索API是系统的核心功能之一，支持文本搜索、图片搜索、向量搜索、过滤搜索和相似图片搜索等多种方式。

## 搜索API概览

所有搜索API的基础路径为：`/api/v1/search`

| 搜索类型 | 说明 | 详细文档 |
|---------|-----|---------|
| 文本搜索 | 通过关键词、描述等文本信息搜索图片 | [文本搜索API](text_search.md) |
| 图片搜索 | 通过上传图片搜索相似的图片 | [图片搜索API](image_search.md) |
| 向量搜索 | 基于向量相似度的高级搜索功能 | [向量搜索API](vector_search.md) |
| 过滤搜索 | 结合多种过滤条件的复合搜索 | [过滤搜索API](filtered_search.md) |
| 相似搜索 | 查找与指定图片ID相似的其他图片 | [相似搜索API](similar_search.md) |

## 通用搜索参数

所有搜索API都支持以下通用参数：

| 参数名 | 类型 | 默认值 | 描述 |
|-------|------|-------|-----|
| page | int | 1 | 页码，从1开始 |
| page_size | int | 20 | 每页返回的结果数量 |
| min_score | float | 0.0 | 搜索结果的最低相似度分数 (0.0-1.0) |

## 搜索结果格式

所有搜索API返回的结果格式统一如下：

```json
{
  "status": "success",
  "code": 200,
  "message": "搜索成功",
  "data": [
    {
      "id": 1,
      "filename": "example.jpg",
      "title": "示例图片",
      "description": "这是一个示例图片",
      "tags": ["示例", "测试"],
      "url": "/api/v1/images/1/file",
      "thumbnail_url": "/api/v1/images/1/thumbnail",
      "score": 0.95, // 搜索相似度分数
      "metadata": {}  // 图片的附加元数据
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
      "query": "搜索查询",
      "time_ms": 150  // 搜索耗时(毫秒)
    }
  },
  "timestamp": "2023-05-19T12:34:56.789Z",
  "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

## 搜索结果排序

搜索结果默认按相似度分数(score)降序排列。部分搜索API可能支持自定义排序。

## 搜索结果过滤

部分搜索API支持结合标签、日期范围或其他元数据进行过滤，具体请参考各个搜索API的详细文档。

# 搜索 API (Search API)

提供统一的多模态图片搜索与相似检索接口，涵盖文本 → 向量、图片 → 向量、直接向量、以及基于已有图片的相似性检索。所有返回均使用统一响应模型，并包含分页 `metadata.pagination`。

## 基础信息

- Base Path: `/api/v1/search`
- 默认分页: `limit=20, offset=0`
- 统一过滤参数支持：`filename`, `title`, `description`, `tags / tags[]`, `start_date`, `end_date`

标签过滤同时兼容：

```text
?tags=风景,自然  或  ?tags[]=风景&tags[]=自然
```

## 公共查询 / 过滤参数

| 参数 | 位置 | 类型 | 必填 | 说明 | 示例 |
|------|------|------|------|------|------|
| filename | query | string | 否 | 按文件名模糊匹配 | cat | 
| title | query | string | 否 | 标题文本匹配 | 日落 |
| description | query | string | 否 | 描述文本匹配 | 海边 |
| tags / tags[] | query | string[] | 否 | 标签过滤，逗号或多值 | tags=风景,自然 |
| start_date | query | string (YYYY-MM-DD HH:MM:SS) | 否 | 开始时间 | 2024-01-01 00:00:00 |
| end_date | query | string | 否 | 结束时间 | 2024-12-31 23:59:59 |
| limit | query/form | int | 否 | 返回条数 (默认20) | 50 |
| offset | query/form | int | 否 | 分页偏移 | 0 |

## 向量目标 (vector targets) 白名单

所有向量检索相关参数只接受以下固定值，系统内部做白名单校验防止构造非法表名：

```text
title, description, image
```

## 1. 统一文本搜索 (仅向量语义检索)

GET `/api/v1/search/unified`

| 参数 | 类型 | 必填 | 说明 | 默认 |
|------|------|------|------|------|
| q | string | 是 | 查询文本 | - |
| search_type | 固定值 "vector" | 否 | 已统一，仅支持多向量语义检索 | vector |
| vector_targets[] | string[] | 否 | 参与向量搜索的目标集合（白名单: title/description/image） | title,description,image |

### 行为说明
 
1. 已移除传统纯 LIKE 模式入口（请使用 /search/fuzzy）
2. 当前仅提供 `search_type=vector`，对查询文本编码后做多向量检索（可指定部分维度）


### 示例

```http
GET /api/v1/search/unified?q=黄昏海边散步的人&search_type=vector&vector_targets[]=title&vector_targets[]=image&limit=30
```

## 2. 统一图片搜索 (上传图片 → 向量)

POST `/api/v1/search/unified/image`

Content-Type: `multipart/form-data`

| 字段 | 类型 | 必填 | 说明 | 示例 |
|------|------|------|------|------|
| file | file | 是 | 待查询图片 | sunset.jpg |
| search_targets | string[] (form) | 否 | 参与检索的向量维度（白名单） | image,title |
| (过滤参数) | form | 否 | 同上表 | - |

示例 (cURL)：

```bash
curl -F "file=@sunset.jpg" -F "search_targets=title" -F "search_targets=image" -F limit=10 http://localhost:8000/api/v1/search/unified/image
```

## 3. 统一向量搜索 (直接提供向量)

POST `/api/v1/search/unified/vector`

Content-Type: `application/x-www-form-urlencoded` 或 `multipart/form-data`

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| query_embedding | float[] | 是 | 查询向量（维度需与模型一致） |
| search_targets | string[] | 否 | 向量检索维度（默认全部） |
| (过滤参数) | form | 否 | 同上 |

示例：

```bash
curl -X POST -F "query_embedding=0.12" -F "query_embedding= ... 多个数值 ..." -F "search_targets=title" http://localhost:8000/api/v1/search/unified/vector
```

## 4. 相似图片搜索 (基于已有图片ID)

GET `/api/v1/search/similar/{image_id}`

| 参数 | 位置 | 类型 | 必填 | 说明 | 默认 |
|------|------|------|------|------|------|
| image_id | path | int | 是 | 参考图片ID | - |
| vector_type | query | enum[title,description,image] | 否 | 指定单一向量类型 | image |
| (过滤参数) | query | - | 否 | 同上 | - |

示例：

```http
GET /api/v1/search/similar/123?vector_type=image&limit=30
```

## 5. 响应数据结构

所有搜索成功响应 `status=success`，核心数据位于 `data.items` / `data.total`：

```json
{
  "status": "success",
  "code": 200,
  "message": "unified_text_search_api成功",
  "data": {
    "items": [
      { "id": 1, "title": "日落海滩", "score": 0.8731, "tags": ["海边","日落"], "distance": 0.1269 }
    ],
    "total": 57
  },
  "metadata": {
    "pagination": { "limit": 20, "offset": 0 }
  },
  "error": null
}
```

字段说明：

| 字段 | 说明 |
|------|------|
| score | 统一相似度分数 (0~1, 越大相关度越高) |
| distance | 距离值（如存在），与 `score` 互补 |
| tags | 标签数组（字符串或对象，视实现而定） |

## 6. 错误示例

```json
{
  "status": "error",
  "code": 400,
  "message": "不支持的搜索类型: xxx",
  "data": null,
  "error": { "code": "UNIFIED_SEARCH_ERROR", "message": "不支持的搜索类型: xxx" },
  "metadata": { "pagination": { "limit": 20, "offset": 0 } }
}
```

## 7. 最佳实践与性能建议

1. 优先使用 `search_type=vector` 以获得更语义化的匹配结果。
2. 结合 `vector_targets` 精简不必要的向量维度可提升吞吐。
3. 大批量翻页建议使用游标或限制最大 `offset`（可在未来版本扩展）。
4. 对高并发部署可考虑将 sqlite-vec 库放置于更快存储并启用 WAL。
5. 对访问最频繁的查询结果可在业务层增加缓存层（命中低变更集合）。

## 8. 版本变更

- 引入统一搜索 (unified) 端点，合并文本/图片/向量路径。
- 新增向量目标白名单校验（防止非法表名注入）。

---

如需了解 AI 推荐对话与流式 SSE 事件，请参考 `ai_router.md`。

# 图片管理 API

图片管理 API 提供图片的上传、获取、更新、删除与批量操作能力，并支持多种过滤与排序。

## 基础信息

- Base URL: `/api/v1/images`
- Content-Type: `application/json`（查询/更新/删除）; `multipart/form-data`（上传）

## 端点列表

### 1. 获取图片列表

GET `/api/v1/images/`

支持分页、排序、文本字段（文件名/标题/描述）与标签、时间范围过滤。

查询参数：

- page: integer，页码（默认 1）
- page_size: integer，每页数量（默认 20，1-100）
- sort_by: string，排序字段（默认 `created_at`）
- order: string，排序方向（`asc`/`desc`，默认 `desc`）
- filename: string，按文件名模糊匹配
- title: string，按标题模糊匹配
- description: string，按描述模糊匹配
- tags: string，标签过滤，逗号分隔（例：`风景,建筑`）
- tags[]: string[]，标签过滤，多值参数，等价于 `tags` 的数组形式；也支持每项内再用逗号分隔
- start_date: string，开始日期（`YYYY-MM-DD`）
- end_date: string，结束日期（`YYYY-MM-DD`）

响应：分页统一格式，data 为图片数组。示例（节选）：

```json
{
  "status": "success",
  "code": 200,
  "message": "获取图片列表成功",
  "data": [
    {
      "id": 1,
      "filename": "a.jpg",
      "filepath": "/uploads/a.jpg",
      "public_url": "/static/uploads/a.jpg",
      "title": "示例",
      "description": "...",
      "file_size": 102400,
      "file_type": "image/jpeg",
      "width": 0,
      "height": 0,
      "created_at": "2024-01-01T12:00:00",
      "updated_at": "2024-01-01T12:00:00",
      "metadata": {},
      "tags": ["风景", "建筑"]
    }
  ],
  "metadata": {
    "pagination": {"page": 1, "page_size": 20, "total_items": 100, "total_pages": 5}
  }
}
```

注意：后端会统一归一化 `tags` 与 `tags[]`，支持混合传入，去重后按“任一标签匹配”过滤。

---

### 2. 获取单个图片信息

GET `/api/v1/images/{image_id}`

路径参数：

- image_id: integer，图片 ID

成功时返回完整图片对象；未找到时返回 `IMAGE_NOT_FOUND` 错误。

---

### 3. 上传图片（支持多文件）

POST `/api/v1/images/upload`

表单字段（multipart/form-data）：

- files: file[]，必填，1..N 张图片
- title: string，可选，默认使用原文件名
- description: string，可选
- auto_analyze: boolean，可选，默认 `true`，上传后自动进行 AI 分析（后台触发）

成功响应：返回已写入数据库并回查的图片数组。示例：

```json
{
  "status": "success",
  "code": 200,
  "message": "成功上传 2 张图片",
  "data": [ { /* 图片对象 */ }, { /* 图片对象 */ } ]
}
```

错误：

- `NO_VALID_IMAGES`：没有有效的图片文件
- `UPLOAD_ERROR`：上传失败

---

### 4. 更新图片信息

PUT `/api/v1/images/{image_id}`

请求体（application/json）：

```json
{
  "title": "新标题",     // 可选
  "description": "新描述" // 可选
}
```

成功时返回更新后的完整图片对象；不存在返回 `IMAGE_NOT_FOUND`。

可能的错误：

- `NO_UPDATE_DATA`：未提供更新字段
- `UPDATE_FAILED`/`UPDATE_ERROR`：更新失败/异常

---

### 5. 删除单张图片

DELETE `/api/v1/images/{image_id}`

成功删除会尝试移除磁盘文件，失败时仍返回删除数据库成功但会在日志打印文件删除异常。

错误：

- `IMAGE_NOT_FOUND`：图片不存在
- `DELETE_FAILED`/`DELETE_ERROR`

---

### 6. 批量删除图片

DELETE `/api/v1/images/batch`

请求体：

```json
{ "image_ids": [1, 2, 3] }
```

响应：

```json
{
  "status": "success",
  "data": { "deleted_count": 2, "deleted_files": ["/path/a.jpg", "/path/b.jpg"] }
}
```

错误：

- `NO_IMAGE_IDS`：未提供 ID 列表
- `BATCH_DELETE_ERROR`

---

### 7. 批量更新图片

POST `/api/v1/images/batch-update`

请求体：

```json
{
  "image_ids": [1, 2, 3],
  "updates": { "title": "统一标题" }
}
```

说明：服务端会补充 `updated_at`，并逐个调用更新；统计成功条数。

响应：

```json
{
  "status": "success",
  "data": { "updated_count": 3, "total_count": 3 }
}
```

错误：

- `NO_IMAGE_IDS` / `NO_UPDATE_DATA`
- `BATCH_UPDATE_ERROR`

## 数据模型（简要）

图片对象 Image：

```json
{
  "id": 1,
  "filename": "a.jpg",
  "filepath": "/uploads/a.jpg",
  "public_url": "/static/uploads/a.jpg",
  "title": "标题",
  "description": "描述",
  "file_size": 102400,
  "file_type": "image/jpeg",
  "width": 0,
  "height": 0,
  "created_at": "2024-01-01T12:00:00",
  "updated_at": "2024-01-01T12:00:00",
  "metadata": {},
  "tags": ["风景", "建筑"]
}
```

## 备注

- 上传时 `metadata`/`tags` 在服务端统一转换为 JSON 存储；读取时统一解析为对象/数组。
- 列表查询的标签过滤支持 `tags` 与 `tags[]` 两种形式，并支持混合输入与去重。
- 删除接口会尝试删除磁盘文件，若文件缺失或权限不足，不影响数据库删除结果。
- `public_url` 为后端根据静态文件服务路径与反向代理前缀拼接生成的对外可访问地址，前端可直接用于 `<img src>` 加载。实际前缀可能因部署而异（例如 Nginx/Dev 代理），请以接口返回为准.

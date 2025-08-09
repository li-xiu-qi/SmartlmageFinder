# AI 分析 API

AI分析API提供图片智能分析功能，包括自动生成标题、描述和标签。

## 基础信息

- **Base URL**: `/api/v1/ai`
- **Content-Type**: `multipart/form-data` (上传图片), `application/json` (其他)

## 端点列表

### 0. AI 智能推荐（文本驱动）

GET `/api/v1/ai/recommend`

基于用户自然语言查询，先进行查询改写（若可用），再进行向量检索并返回推荐结果。

#### 查询参数

| 参数 | 类型 | 必填 | 描述 | 示例 |
|---|---|---|---|---|
| user_query | string | 是 | 用户自然语言查询 | 美丽的自然风景 |
| vector_targets[] | array[string] | 否 | 向量搜索目标，支持 title/description/image，默认三者并用 | vector_targets[]=title&vector_targets[]=description&vector_targets[]=image |
| tags / tags[] | string / array[string] | 否 | 标签过滤（支持逗号分隔或多值） | tags=风景,自然 或 tags[]=风景&tags[]=自然 |
| limit | number | 否 | 返回条数，默认 20 | 20 |

#### 示例请求

```http
GET /api/v1/ai/recommend?user_query=%E7%BE%8E%E4%B8%BD%E7%9A%84%E8%87%AA%E7%84%B6%E9%A3%8E%E6%99%AF&limit=20&vector_targets[]=title&vector_targets[]=description&vector_targets[]=image
```

#### 响应

成功时返回统一响应模型，data 字段内包含推荐结果与改写信息：

```json
{
  "status": "success",
  "code": 200,
  "message": "AI推荐成功",
  "data": {
    "images": [
      { "id": 1, "title": "山水风景", "score": 0.87, "tags": ["风景","自然"] }
    ],
    "query_rewrite": {
      "original_query": "美丽的自然风景",
      "optimized_query": "自然风景 山水风景",
      "rewrite_success": true,
      "error": null
    },
    "total_found": 42,
    "search_time_ms": 0,
    "success": true
  },
  "error": null,
  "metadata": {}
}
```

错误时返回：

```json
{
  "status": "error",
  "code": 500,
  "message": "推荐服务失败",
  "data": null,
  "error": { "code": "AI_RECOMMENDATION_ERROR", "message": "具体错误" },
  "metadata": {}
}
```

### 0.1 AI 对话式推荐（非流式）

POST `/api/v1/ai/recommend/chat`

请求体（application/json）：

```json
{
  "messages": [
    { "role": "user", "content": "想找黄昏海边散步的人" }
  ],
  "state": { "filters": { "tags": ["海边"] } },
  "vector_targets": ["title","description","image"],
  "limit": 20
}
```

响应：统一响应模型，data 内包含 images、query_rewrite、state 等。

### 0.2 AI 对话式推荐（流式 SSE）

POST `/api/v1/ai/recommend/chat/stream`

- Content-Type: `application/json`
- Response: `text/event-stream`（SSE）

事件流说明：

- `rewrite_start`: { original }
- `rewrite_delta`: { delta }
- `rewrite_done`: { optimized }
- `rewrite_skipped`: { reason }
- `search_started`: { query, vector_targets, filters, limit }
- `result`: { index, image }
- `complete`: { total_found, state }
- `error`: { message }

使用示例（前端）：

```ts
const res = await fetch('/api/v1/ai/recommend/chat/stream', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ messages, state, vector_targets, limit, filters })
});
const reader = res.body!.getReader();
const decoder = new TextDecoder('utf-8');
let buffer = '';
while (true) {
  const { value, done } = await reader.read();
  if (done) break;
  buffer += decoder.decode(value, { stream: true });
  const parts = buffer.split('\n\n');
  buffer = parts.pop() || '';
  for (const chunk of parts) {
    const lines = chunk.split('\n');
    const event = lines.find(l => l.startsWith('event: '))?.slice(7).trim();
    const dataLine = lines.find(l => l.startsWith('data: '));
    if (!event || !dataLine) continue;
    const data = JSON.parse(dataLine.slice(6));
    // 根据 event 处理 UI
  }
}
```

### 0.3 上下文记忆与向量白名单说明

对话式推荐内部实现了 64K 字符滚动窗口上下文管理：

```
MAX_CONTEXT_CHARS = 64_000
```

超过窗口的历史消息会从最早开始裁剪（保留 system / 最近消息），保证在多轮对话下仍可保持上下文相关性，同时控制成本。

向量相关工具函数使用固定白名单 `{title, description, image}` 过滤用户传入的 `vector_targets`，防止构造非法表名导致数据库错误（例如: `no such table: xxx_vectors`）。

SSE 事件补充：

- `rewrite_skipped`: 当跳过改写时返回原因
- 列表类结果逐条以 `result` 推送，可实时渲染

### 1. 分析上传图片（上传文件）

POST `/api/v1/ai/analyze-upload-image`

分析用户上传的图片，生成标题、描述和标签。

#### 请求格式

`multipart/form-data`

#### 请求参数

| 参数 | 类型 | 必填 | 描述 | 示例 |
|---|---|---|---|---|
| file | file | 是 | 要分析的图片文件 | - |
| detail | string | 否 | 细节级别: low或high，默认为low | low |

#### 响应示例

 
##### 成功响应 (200)

```json
{
  "status": "success",
  "code": 200,
  "message": "图片分析成功",
  "data": {
    "title": "日落海滩",
    "description": "一张美丽的日落海滩照片，天空呈现出橙红色，海浪轻轻拍打着沙滩",
    "tags": ["日落", "海滩", "风景", "自然", "天空", "海浪"],
    "confidence": 0.92,
    "analyzed_at": "2024-01-15T14:30:00"
  },
  "metadata": {
    "model": "AI多模态模型",
    "time_ms": 1250
  },
  "error": null
}
```

 
##### 错误响应 (500)（服务不可用）

```json
{
  "status": "error",
  "code": 500,
  "message": "图像分析服务不可用，请确认配置了正确的API密钥",
  "error": {
    "code": "SERVICE_UNAVAILABLE",
    "message": "图像分析服务不可用，请确认配置了正确的API密钥"
  }
}
```

 
##### 错误响应 (500)（处理失败）

```json
{
  "status": "error",
  "code": 500,
  "message": "AI处理出错: 网络连接超时",
  "error": {
    "code": "AI_PROCESSING_ERROR",
    "message": "AI处理出错: 网络连接超时"
  }
}
```

### 2. 分析图片ID（已存在图片）

POST `/api/v1/ai/analyze-image-id/{image_id}`

分析已上传的图片，生成标题、描述和标签。

#### 路径参数

| 参数 | 类型 | 描述 | 示例 |
|---|---|---|---|
| image_id | string | 图片的ID | 123 |

#### 请求格式（图片ID）

`multipart/form-data`

#### 请求参数（图片ID）

| 参数 | 类型 | 必填 | 描述 | 示例 |
|---|---|---|---|---|
| detail | string | 否 | 细节级别: low或high，默认为low | high |

#### 响应示例（图片ID）

 
##### 成功响应 (200)（图片ID）

```json
{
  "status": "success",
  "code": 200,
  "message": "图片分析成功",
  "data": {
    "title": "城市夜景",
    "description": "繁华的城市夜景，高楼大厦林立，灯光璀璨",
    "tags": ["城市", "夜景", "建筑", "灯光"],
    "confidence": 0.88,
    "analyzed_at": "2024-01-15T15:45:00"
  },
  "metadata": {
    "model": "AI多模态模型",
    "time_ms": 980
  },
  "error": null
}
```

 
##### 错误响应 (400)（图片ID）

```json
{
  "status": "error",
  "code": 400,
  "message": "图片格式不支持",
  "error": {
    "code": "IMAGE_ANALYSIS_ERROR",
    "message": "图片格式不支持"
  }
}
```

 
##### 错误响应 (500)（图片ID）

```json
{
  "status": "error",
  "code": 500,
  "message": "AI处理出错: 模型加载失败",
  "error": {
    "code": "AI_PROCESSING_ERROR",
    "message": "AI处理出错: 模型加载失败"
  }
}
```

## 支持的图片格式与限制

- JPEG (.jpg, .jpeg)
- PNG (.png)
- WebP (.webp)
- BMP (.bmp)
- TIFF (.tiff, .tif)

大小建议：单张图片不超过 10 MB。

## 分析结果说明

### 字段解释

| 字段 | 类型 | 描述 |
|---|---|---|
| title | string | AI生成的图片标题 |
| description | string | AI生成的图片描述 |
| tags | array | AI生成的标签列表 |
| confidence | float | AI分析的置信度，范围0-1 |
| analyzed_at | string | 分析完成时间 |

### 细节级别

- **low**: 快速分析，适合批量处理
- **high**: 详细分析，提供更丰富的描述和标签

## 错误代码

| 错误代码 | 描述 | HTTP状态码 |
|---|---|---|
| SERVICE_UNAVAILABLE | 图像分析服务不可用 | 500 |
| AI_PROCESSING_ERROR | AI处理出错 | 500 |
| IMAGE_ANALYSIS_ERROR | 图片分析失败 | 400 |

## 最佳实践

1. **模型/密钥配置**: 确保在配置文件中正确设置 AI 模型与密钥（若需要）
2. **文件大小**: 建议图片大小不超过10MB以获得最佳性能
3. **批量处理**: 对于大量图片，建议使用异步处理
4. **错误处理**: 实现重试机制以处理临时的AI服务不可用

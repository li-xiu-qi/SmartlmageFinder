# AI 分析 API

AI分析API提供图片智能分析功能，包括自动生成标题、描述和标签。

## 基础信息

- **Base URL**: `/api/v1/ai`
- **Content-Type**: `multipart/form-data` (上传图片), `application/json` (其他)

## 端点列表

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
```ts

响应：统一响应模型，data 内包含 images、query_rewrite、state 等。

### 0.2 AI 对话式推荐（流式 SSE）

POST `/api/v1/ai/recommend/chat/stream`

- Content-Type: `application/json`
- Response: `text/event-stream`（SSE）

事件流说明（当前实现只会向客户端发送以下 4 类事件；内部 agent 还有 selection 事件被封装为 complete）：

- `rewrite_start`：流开始，包含 request_id / conversation_id
- `assistant_delta`：助手增量文本（可能多次）
- `complete`：包含已排序 image_ids、images_brief、assistant_text、total_found
- `error`：出错时返回错误信息

已废弃 / 未实现的旧事件（rewrite_delta / rewrite_done / search_started / result 等）不再发送，文档中移除以避免混淆。

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
```text

### 0.3 上下文记忆与向量白名单说明

对话式推荐内部实现了 64K 字符滚动窗口上下文管理：

```text
MAX_CONTEXT_CHARS = 64_000
```

超过窗口的历史消息会从最早开始裁剪（保留 system / 最近消息），保证在多轮对话下仍可保持上下文相关性，同时控制成本。

向量相关工具函数使用固定白名单 `{title, description, image}` 过滤用户传入的 `vector_targets`，防止构造非法表名导致数据库错误（例如: `no such table: xxx_vectors`）。

SSE 事件补充：内部 agent 会产生 `selection` 事件（包含最终排序及完整候选），路由层转换为对外的 `complete` 事件一次性返回，不再逐条推送 `result`。

向量目标 whitelist 固定为 `["title","description","image"]`，传入其他值会被忽略或过滤，防止非法表访问。

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

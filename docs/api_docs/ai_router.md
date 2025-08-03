# AI 分析 API

AI分析API提供图片智能分析功能，包括自动生成标题、描述和标签。

## 基础信息

- **Base URL**: `/api/v1/ai`
- **Content-Type**: `multipart/form-data` (上传图片), `application/json` (其他)

## 端点列表

### 1. 分析上传图片

**POST** `/api/v1/ai/analyze-upload-image`

分析用户上传的图片，生成标题、描述和标签。

#### 请求格式

`multipart/form-data`

#### 请求参数

| 参数 | 类型 | 必填 | 描述 | 示例 |
|---|---|---|---|---|
| file | file | 是 | 要分析的图片文件 | - |
| detail | string | 否 | 细节级别: low或high，默认为low | low |

#### 响应示例

**成功响应 (200)**
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

**错误响应 (500)**
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

**错误响应 (500)**
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

### 2. 分析图片ID

**POST** `/api/v1/ai/analyze-image-id/{image_id}`

分析已上传的图片，生成标题、描述和标签。

#### 路径参数

| 参数 | 类型 | 描述 | 示例 |
|---|---|---|---|
| image_id | string | 图片的ID | 123 |

#### 请求格式

`multipart/form-data`

#### 请求参数

| 参数 | 类型 | 必填 | 描述 | 示例 |
|---|---|---|---|---|
| detail | string | 否 | 细节级别: low或high，默认为low | high |

#### 响应示例

**成功响应 (200)**
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

**错误响应 (400)**
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

**错误响应 (500)**
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

## 支持的图片格式

- JPEG (.jpg, .jpeg)
- PNG (.png)
- WebP (.webp)
- BMP (.bmp)
- TIFF (.tiff, .tif)

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

1. **API密钥配置**: 确保在配置文件中正确设置了AI服务的API密钥
2. **文件大小**: 建议图片大小不超过10MB以获得最佳性能
3. **批量处理**: 对于大量图片，建议使用异步处理
4. **错误处理**: 实现重试机制以处理临时的AI服务不可用
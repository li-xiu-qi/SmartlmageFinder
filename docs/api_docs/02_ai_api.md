# AI 功能 API 文档

## 概述

SmartImageFinder系统提供了一系列AI驱动的图像分析功能，包括图片内容识别、生成标题和描述、自动标签推荐等。这些功能基于大型多模态模型（如OpenAI的Vision模型），能够智能分析图像内容并提供有价值的元数据。

本文档详细介绍了AI功能模块的API端点、请求参数和响应格式。

## 基本配置

AI功能依赖于以下配置参数：

- **OPENAI_API_KEY**: OpenAI API密钥，用于访问图像分析服务
- **OPENAI_API_BASE**: API基础URL（可选，适用于代理或自定义部署）
- **TEMP_DIR**: 临时文件存储目录，用于处理上传的图片

这些配置项应在系统的`config.yaml`文件中设置。

## API端点

### 1. 分析上传图片

通过上传一张新图片进行AI分析，生成标题、描述和标签推荐。

**请求**:
- **方法**: POST
- **URL**: `/api/ai/analyze-upload-image`
- **内容类型**: `multipart/form-data`
- **参数**:
  - `file`: (必需) 要分析的图片文件
  - `detail`: (可选) 分析详细程度，可选 "low"（默认）或 "high"

**成功响应**:
```json
{
  "status": "success",
  "code": 200,
  "message": "图片分析成功",
  "data": {
    "title": "日落时的海滩风景",
    "description": "这是一张拍摄于黄昏时分的海滩照片，展示了金色的阳光照射在平静的海面上，远处有几艘小船，天空呈现出橙红色的美丽色彩。",
    "tags": ["海滩", "日落", "自然", "海洋", "风景", "橙色", "天空"]
  },
  "metadata": {
    "model": "AI多模态模型",
    "time_ms": 2500
  },
  "error": null,
  "timestamp": "2025-05-16T10:30:45.123456",
  "request_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**错误响应**:
```json
{
  "status": "error",
  "code": 500,
  "message": "AI处理出错: 无法处理图片",
  "data": null,
  "error": {
    "code": "AI_PROCESSING_ERROR",
    "message": "AI处理出错: 无法处理图片",
    "details": null
  },
  "metadata": {},
  "timestamp": "2025-05-16T10:31:22.123456",
  "request_id": "550e8400-e29b-41d4-a716-446655440001"
}
```

### 2. 分析现有图片

通过提供系统中已存在图片的ID进行AI分析，生成标题、描述和标签。这适用于已经上传到系统但尚未分析的图片。

**请求**:
- **方法**: POST
- **URL**: `/api/ai/analyze-image-id/{image_id}`
- **内容类型**: `application/x-www-form-urlencoded`
- **路径参数**:
  - `image_id`: (必需) 要分析的图片ID
- **表单参数**:
  - `detail`: (可选) 分析图片的分辨率，可选 "low"（默认）或 "high"

**成功响应**:
```json
{
  "status": "success",
  "code": 200,
  "message": "图片分析成功",
  "data": {
    "title": "雪山下的森林小屋",
    "description": "一座木制小屋坐落在茂密的松树林中，背景是雄伟的雪山。照片拍摄于晴朗的冬日，阳光使雪山顶部闪闪发光，前景有一条小溪流经。",
    "tags": ["雪山", "小屋", "森林", "自然", "冬季", "阳光", "户外", "风景"]
  },
  "metadata": {
    "model": "AI多模态模型",
    "time_ms": 2300
  },
  "error": null,
  "timestamp": "2025-05-16T10:35:15.123456",
  "request_id": "550e8400-e29b-41d4-a716-446655440002"
}
```

**错误响应**:
```json
{
  "status": "error",
  "code": 400,
  "message": "找不到ID为123的图片",
  "data": null,
  "error": {
    "code": "IMAGE_ANALYSIS_ERROR",
    "message": "找不到ID为123的图片",
    "details": null
  },
  "metadata": {},
  "timestamp": "2025-05-16T10:36:22.123456",
  "request_id": "550e8400-e29b-41d4-a716-446655440003"
}
```

## 错误代码

| 错误代码 | HTTP 状态码 | 说明 |
|---------|------------|------|
| SERVICE_UNAVAILABLE | 500 | AI服务不可用，可能由于API密钥未配置或无效 |
| AI_PROCESSING_ERROR | 500 | AI处理过程中发生错误 |
| IMAGE_ANALYSIS_ERROR | 400 | 图片分析错误，如图片不存在或文件损坏 |


## 实现细节

### 图像分析器初始化

系统在启动时初始化图像分析服务，通过以下步骤：

1. 从配置文件读取OpenAI API密钥和基础URL
2. 创建`ImageAnalysis`实例
3. 如果初始化成功，将AI功能标记为可用
4. 如果初始化失败（如缺少API密钥），相关AI功能将不可用

### 请求流程

1. 客户端发送图片分析请求（上传新图片或提供已有图片ID）
2. 服务器验证分析服务是否可用
3. 对于上传的图片，临时保存到服务器
4. 调用图像分析器分析图片内容
5. 返回分析结果（标题、描述、标签）
6. 清理临时文件（如有）


## 注意事项

1. **API密钥安全**：确保OpenAI API密钥安全保存，不要在客户端代码或公开仓库中暴露
2. **成本考虑**：根据使用场景选择适当的分析详细程度，高详细度会消耗更多的API资源
3. **错误处理**：始终检查和处理API响应中的错误信息
4. **超时设置**：图像分析可能需要几秒钟时间，确保在前端设置合理的超时时间

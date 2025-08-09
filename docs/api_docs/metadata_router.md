# 元数据管理 API

元数据管理API提供图片元数据的更新和管理功能。

## 基础信息

- **Base URL**: `/api/v1/metadata`
- **Content-Type**: `application/json`

## 端点列表

### 1. 更新图片元数据

PUT `/api/v1/metadata/{image_id}/update`

更新指定图片的元数据。元数据将以JSON对象的形式存储。

#### 路径参数

| 参数 | 类型 | 描述 | 示例 |
|---|---|---|---|
| image_id | integer | 图片ID | 123 |

#### 请求格式

`application/json`

#### 请求体

```json
{
  "metadata": {
    "camera": "Canon EOS R5",
    "iso": 400,
    "focal_length": "50mm",
    "aperture": "f/1.8",
    "location": {
      "latitude": 39.9042,
      "longitude": 116.4074,
      "address": "北京市"
    }
  }
}
```

#### 响应示例

成功响应 (200)
```json
{
  "status": "success",
  "code": 200,
  "message": "元数据更新成功",
  "data": {
    "id": 123,
    "filename": "example.jpg",
    "title": "示例图片",
    "description": "这是一个示例图片",
    "metadata": {
      "camera": "Canon EOS R5",
      "iso": 400,
      "focal_length": "50mm",
      "aperture": "f/1.8",
      "location": {
        "latitude": 39.9042,
        "longitude": 116.4074,
        "address": "北京市"
      }
    },
    "updated_at": "2024-01-15T16:30:00"
  },
  "error": null
}
```

错误响应 (404)
```json
{
  "status": "error",
  "code": 404,
  "message": "未找到ID为 123 的图片",
  "error": {
    "code": "IMAGE_NOT_FOUND",
    "message": "未找到ID为 123 的图片"
  }
}
```

错误响应 (400)
```json
{
  "status": "error",
  "code": 400,
  "message": "更新图片ID 123 的元数据失败，图片可能不存在或数据无变化",
  "error": {
    "code": "METADATA_UPDATE_FAILED",
    "message": "更新图片ID 123 的元数据失败，图片可能不存在或数据无变化"
  }
}
```

**错误响应 (400)**
```json
{
  "status": "error",
  "code": 400,
  "message": "元数据格式错误，无法编码为JSON: Expecting value",
  "error": {
    "code": "JSON_ENCODE_ERROR",
    "message": "元数据格式错误，无法编码为JSON: Expecting value"
  }
}
```

错误响应 (500)
```json
{
  "status": "error",
  "code": 500,
  "message": "更新元数据时发生数据库错误: database locked",
  "error": {
    "code": "DATABASE_ERROR",
    "message": "更新元数据时发生数据库错误: database locked"
  }
}
```

## 元数据格式

### 支持的元数据类型

| 类型 | 示例 | 说明 |
|---|---|---|
| 字符串 | `"Canon EOS R5"` | 文本信息 |
| 数字 | `400` | 数值信息 |
| 布尔值 | `true` | 开关状态 |
| 数组 | `["风景", "建筑"]` | 列表信息 |
| 对象 | `{"lat": 39.9, "lng": 116.4}` | 嵌套信息 |

### 常用元数据字段

| 字段名 | 类型 | 说明 |
|---|---|---|
| camera | string | 相机型号 |
| iso | number | ISO感光度 |
| focal_length | string | 焦距 |
| aperture | string | 光圈值 |
| shutter_speed | string | 快门速度 |
| location | object | 拍摄位置信息 |
| keywords | array | 关键词列表 |
| copyright | string | 版权信息 |
| artist | string | 摄影师 |

## 错误代码

| 错误代码 | 描述 | HTTP状态码 |
|---|---|---|
| IMAGE_NOT_FOUND | 图片不存在 | 404 |
| METADATA_UPDATE_FAILED | 元数据更新失败 | 400 |
| JSON_ENCODE_ERROR | JSON编码错误 | 400 |
| DATABASE_ERROR | 数据库错误 | 500 |
| INTERNAL_SERVER_ERROR | 内部服务器错误 | 500 |

## 最佳实践

1. **字段验证**: 在更新前验证元数据字段的格式和类型
2. **批量更新**: 对于大量元数据更新，建议使用事务处理
3. **数据清理**: 定期清理无效或过期的元数据
4. **备份**: 重要元数据变更前建议备份原始数据
5. **标准化**: 保持元数据字段命名的一致性，使用小写字母和下划线

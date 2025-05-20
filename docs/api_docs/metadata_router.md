# 元数据管理 API

## 简介

元数据管理API提供了操作图片元数据的功能，允许用户查看和更新图片的附加信息。元数据是描述图片的额外信息，如尺寸、创建工具、版权信息等，这些信息对于高级搜索和图片管理非常有用。

## 接口详情

### 更新图片元数据

**请求方式**: PUT

**路径**: `/api/v1/metadata/{image_id}/update`

**说明**: 更新指定图片的元数据

#### 路径参数

| 参数名 | 类型 | 必填 | 描述 |
|-------|------|------|-----|
| image_id | integer | 是 | 图片ID |

#### 请求体

```json
{
  "metadata": {
    "author": "张三",
    "copyright": "版权所有 © 2023",
    "location": {
      "city": "北京",
      "country": "中国"
    },
    "camera": {
      "make": "Canon",
      "model": "EOS R5",
      "settings": {
        "aperture": "f/2.8",
        "exposure": "1/200",
        "iso": 100
      }
    },
    "custom_field": "自定义值"
  }
}
```

> **注意**: 元数据是一个自由格式的JSON对象，可以包含任何键值对。更新操作会替换整个元数据对象，而不是合并，所以请确保包含所有需要保留的字段。

#### 响应

```json
{
  "status": "success",
  "code": 200,
  "message": "元数据更新成功",
  "data": {
    "id": 1,
    "filename": "example.jpg",
    "title": "城市风景",
    "description": "现代城市的天际线",
    "tags": ["城市", "建筑", "天际线"],
    "url": "/api/v1/images/1/file",
    "thumbnail_url": "/api/v1/images/1/thumbnail",
    "created_at": "2023-05-19T12:34:56.789Z",
    "updated_at": "2023-05-20T10:15:30.123Z",
    "metadata": {
      "width": 1920,
      "height": 1080,
      "size_kb": 2500,
      "author": "张三",
      "copyright": "版权所有 © 2023",
      "location": {
        "city": "北京",
        "country": "中国"
      },
      "camera": {
        "make": "Canon",
        "model": "EOS R5",
        "settings": {
          "aperture": "f/2.8",
          "exposure": "1/200",
          "iso": 100
        }
      },
      "custom_field": "自定义值"
    }
  },
  "timestamp": "2023-05-19T12:34:56.789Z",
  "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

## 错误代码

| 错误代码 | HTTP状态码 | 描述 |
|---------|-----------|-----|
| IMAGE_NOT_FOUND | 404 | 指定ID的图片不存在 |
| METADATA_UPDATE_FAILED | 400 | 元数据更新失败 |
| JSON_ENCODE_ERROR | 400 | 元数据格式错误，无法编码为JSON |
| DATABASE_ERROR | 500 | 数据库操作错误 |
| INTERNAL_SERVER_ERROR | 500 | 内部服务器错误 |

## 最佳实践

1. 元数据应该结构化并使用一致的格式，这样可以在搜索和过滤中更有效地使用。

2. 常见的元数据字段包括：
   - 作者/创建者信息
   - 版权和许可信息
   - 拍摄设备信息（相机、手机型号等）
   - 地理位置信息
   - 拍摄参数（光圈、快门速度、ISO等）
   - 创建和修改日期
   - 项目或集合识别符

3. 更新元数据时，先获取当前元数据，然后修改需要更新的字段，再提交完整的元数据对象，以避免丢失现有信息。

4. 元数据可以用于高级搜索和过滤，例如根据地理位置、拍摄设备或创建日期搜索图片。

5. 为了保持一致性，可以为特定类型的图片定义标准元数据模板，例如产品图片、风景照片或人物肖像。

6. 考虑元数据的大小，避免存储过大的元数据，这可能会影响系统性能。通常元数据应该保持在几KB以内。

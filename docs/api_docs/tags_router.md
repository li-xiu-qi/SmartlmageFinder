# 标签管理 API

标签管理API提供图片标签的获取、搜索和管理功能。

## 基础信息

- **Base URL**: `/api/v1/tags`
- **Content-Type**: `application/json`

## 端点列表

### 1. 获取所有标签

GET `/api/v1/tags/`

获取系统中所有已使用标签及其使用频率。

#### 请求参数

| 参数 | 类型 | 必填 | 描述 | 示例 |
|---|---|---|---|---|
| limit | integer | 否 | 返回标签数量，1-200，默认50 | 50 |

#### 响应示例

**成功响应 (200)**
```json
{
  "status": "success",
  "code": 200,
  "message": "成功获取标签列表",
  "data": [
    {
      "tag": "风景",
      "count": 125
    },
    {
      "tag": "建筑",
      "count": 89
    },
    {
      "tag": "人物",
      "count": 67
    }
  ],
  "metadata": {
    "total": 45
  },
  "error": null
}
```

### 2. 搜索标签

GET `/api/v1/tags/search`

搜索符合关键字的标签，用于自动完成功能。

#### 请求参数

| 参数 | 类型 | 必填 | 描述 | 示例 |
|---|---|---|---|---|
| query | string | 是 | 标签搜索关键字 | 建筑 |
| limit | integer | 否 | 返回标签数量，1-100，默认20 | 10 |

#### 响应示例

**成功响应 (200)**
```json
{
  "status": "success",
  "code": 200,
  "message": "成功搜索标签",
  "data": [
    "建筑",
    "建筑设计",
    "古建筑",
    "现代建筑"
  ],
  "metadata": {
    "total": 4
  },
  "error": null
}
```

### 3. 根据标签获取图片

GET `/api/v1/tags/by-tag/{tag}`

根据标签获取图片列表。

#### 路径参数

| 参数 | 类型 | 描述 | 示例 |
|---|---|---|---|
| tag | string | 标签名称 | 风景 |

#### 请求参数

| 参数 | 类型 | 必填 | 描述 | 示例 |
|---|---|---|---|---|
| page | integer | 否 | 页码，从1开始 | 1 |
| page_size | integer | 否 | 每页数量，1-100，默认20 | 20 |

#### 响应示例

**成功响应 (200)**
```json
{
  "status": "success",
  "code": 200,
  "message": "成功获取标签 '风景' 的图片列表",
  "data": [
    {
      "id": 1,
      "filename": "landscape1.jpg",
      "title": "美丽风景",
      "description": "夕阳下的美丽风景",
      "file_size": 204800,
      "width": 1920,
      "height": 1080,
      "tags": ["风景", "夕阳"],
      "created_at": "2024-01-15T10:30:00"
    }
  ],
  "metadata": {
    "pagination": {
      "page": 1,
      "page_size": 20,
      "total_items": 125,
      "total_pages": 7
    },
    "tag": "风景"
  },
  "error": null
}
```

### 4. 根据多个标签获取图片

GET `/api/v1/tags/by-multiple-tags`

根据多个标签获取图片列表。

#### 请求参数

| 参数 | 类型 | 必填 | 描述 | 示例 |
|---|---|---|---|---|
| tags | string | 是 | 多个标签，以逗号分隔 | 风景,建筑,自然 |
| mode | string | 否 | 匹配模式：'or'表示匹配任一标签，'and'表示匹配所有标签，默认or | and |
| page | integer | 否 | 页码，从1开始 | 1 |
| page_size | integer | 否 | 每页数量，1-100，默认20 | 20 |

#### 响应示例

**成功响应 (200)** - 匹配任一标签 (or)
```json
{
  "status": "success",
  "code": 200,
  "message": "成功获取满足任一标签的图片列表",
  "data": [
    {
      "id": 1,
      "filename": "mountain.jpg",
      "title": "山间风景",
      "tags": ["风景", "自然"],
      "created_at": "2024-01-15T10:30:00"
    }
  ],
  "metadata": {
    "pagination": {
      "page": 1,
      "page_size": 20,
      "total_items": 156,
      "total_pages": 8
    },
    "tags": ["风景", "建筑", "自然"],
    "mode": "or"
  },
  "error": null
}
```

**成功响应 (200)** - 匹配所有标签 (and)
```json
{
  "status": "success",
  "code": 200,
  "message": "成功获取满足所有标签的图片列表",
  "data": [
    {
      "id": 5,
      "filename": "architecture.jpg",
      "title": "现代建筑",
      "tags": ["建筑", "现代", "设计"],
      "created_at": "2024-01-15T11:00:00"
    }
  ],
  "metadata": {
    "pagination": {
      "page": 1,
      "page_size": 20,
      "total_items": 23,
      "total_pages": 2
    },
    "tags": ["建筑", "现代", "设计"],
    "mode": "and"
  },
  "error": null
}
```

**错误响应 (400)**
```json
{
  "status": "error",
  "code": 400,
  "message": "请提供有效的标签列表",
  "error": {
    "code": "INVALID_TAGS",
    "message": "请提供有效的标签列表"
  }
}
```

### 5. 为图片添加标签

POST `/api/v1/tags/{image_id}/update`

为图片添加或更新标签。

#### 路径参数

| 参数 | 类型 | 描述 | 示例 |
|---|---|---|---|
| image_id | integer | 图片ID | 123 |

#### 请求格式

`application/json`

#### 请求体

```json
[
  "标签",
  "建筑",
  "现代",
  "设计"
]
```

#### 响应示例

**成功响应 (200)**
```json
{
  "status": "success",
  "code": 200,
  "message": "标签添加成功",
  "data": {
    "tags": ["标签", "建筑", "现代", "设计"]
  },
  "error": null
}
```

**错误响应 (404)**
```json
{
  "status": "error",
  "code": 404,
  "message": "未找到ID为123的图片",
  "error": {
    "code": "NOT_FOUND",
    "message": "未找到ID为123的图片"
  }
}
```

**错误响应 (400)**
```json
{
  "status": "error",
  "code": 400,
  "message": "标签列表不能为空",
  "error": {
    "code": "INVALID_TAGS",
    "message": "标签列表不能为空"
  }
}
```

## 标签使用说明

### 标签规范

- 标签应该简短、有意义
- 避免使用特殊字符和空格
- 建议使用中文或英文单词
- 保持标签的一致性

### 常用标签示例

| 分类 | 示例标签 |
|---|---|
| 场景 | 风景, 城市, 建筑, 自然, 海景 |
| 对象 | 人物, 动物, 植物, 车辆, 食物 |
| 风格 | 现代, 复古, 简约, 抽象, 写实 |
| 颜色 | 红色, 蓝色, 黑白, 彩色, 暖色 |
| 时间 | 日出, 日落, 白天, 夜晚, 四季 |

## 错误代码

| 错误代码 | 描述 | HTTP状态码 |
|---|---|---|
| INVALID_TAGS | 标签列表无效 | 400 |
| NOT_FOUND | 图片不存在 | 404 |

## 最佳实践

1. **标签标准化**: 建立标签词典，保持标签的一致性
2. **层级标签**: 使用层级结构，如"建筑-现代-玻璃幕墙"
3. **标签数量**: 每张图片建议3-8个标签
4. **标签质量**: 避免过度标签化，保持标签的相关性
5. **定期整理**: 定期检查和合并相似的标签

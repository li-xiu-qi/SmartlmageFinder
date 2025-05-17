# 全局响应模式说明文档

## 简介

SmartImageFinder 系统采用统一的响应格式，确保 API 接口返回结构一致、规范，便于前端处理和展示。`global_schemas.py` 模块定义了系统中所有 API 端点共用的数据模型和响应结构，是整个后端 API 接口的基础框架。

本文档详细介绍了系统的通用响应模型及其使用方法。

## 核心模型

### StatusEnum

用于表示 API 响应的状态枚举类型：

```python
class StatusEnum(str, Enum):
    SUCCESS = "success"  # 操作成功
    ERROR = "error"     # 操作失败
```

### ErrorModel

错误信息模型，用于封装 API 调用失败时返回的错误信息：

| 字段 | 类型 | 说明 |
|------|------|------|
| code | str | 错误代码，用于标识特定错误类型 |
| message | str | 错误描述，对错误的具体说明 |
| details | Dict[str, Any] | 可选的详细错误信息，提供更多调试数据 |

### PaginationMetadata

分页查询结果的元数据模型：

| 字段 | 类型 | 默认值 | 说明 |
|------|------|-------|------|
| page | int | 1 | 当前页码 |
| page_size | int | 10 | 每页条数 |
| total_items | int | 0 | 查询结果总条目数 |
| total_pages | int | 0 | 总页数 |

### ResponseModel

通用 API 响应模型，所有 API 端点的返回值都封装在此结构中：

| 字段 | 类型 | 说明 |
|------|------|------|
| status | StatusEnum | 响应状态，"success" 或 "error" |
| code | int | HTTP 状态码 |
| message | str | 响应消息 |
| data | Any | 响应的主体数据 |
| error | ErrorModel | 错误信息，成功时为 null |
| metadata | Dict[str, Any] | 附加元数据，如分页信息 |
| timestamp | datetime | 响应时间戳 |
| request_id | str | 请求 ID，用于跟踪和调试 |

## 辅助方法

`ResponseModel` 类提供了几个辅助方法，用于快速创建标准响应：

### success()

创建成功响应：

```python
@classmethod
def success(
    cls, data: Any = None, message: str = "操作成功", 
    code: int = 200, metadata: Dict[str, Any] = None, 
    request_id: str = None
) -> "ResponseModel"
```

参数:
- `data`: 响应主体数据
- `message`: 响应消息
- `code`: HTTP 状态码
- `metadata`: 额外元数据
- `request_id`: 请求 ID

示例:
```python
return ResponseModel.success(data=user_data, message="获取用户信息成功")
```

### error()

创建错误响应：

```python
@classmethod
def error(
    cls, code: str, message: str, http_code: int = 400,
    details: Dict[str, Any] = None, request_id: str = None
) -> "ResponseModel"
```

参数:
- `code`: 错误代码
- `message`: 错误消息
- `http_code`: HTTP 状态码
- `details`: 详细错误信息
- `request_id`: 请求 ID

示例:
```python
return ResponseModel.error(
    code="USER_NOT_FOUND", 
    message="用户不存在", 
    http_code=404
)
```

### paginated_response()

创建分页成功响应：

```python
@classmethod
def paginated_response(
    cls, data: Any, page: int, page_size: int, 
    total_items: int, message: str = "获取数据成功",
    additional_metadata: Dict[str, Any] = None
) -> "ResponseModel"
```

参数:
- `data`: 分页数据
- `page`: 当前页码
- `page_size`: 每页条数
- `total_items`: 总条目数
- `message`: 响应消息
- `additional_metadata`: 额外元数据

示例:
```python
return ResponseModel.paginated_response(
    data=images,
    page=1,
    page_size=10,
    total_items=100,
    message="获取图片列表成功"
)
```

### paginated_error()

创建分页查询失败响应：

```python
@classmethod
def paginated_error(
    cls, error_code: str, message: str, http_code: int = 400,
    page: int = 1, page_size: int = 10, 
    details: Dict[str, Any] = None, request_id: str = None
) -> "ResponseModel"
```

参数:
- `error_code`: 错误代码
- `message`: 错误消息
- `http_code`: HTTP 状态码
- `page`: 当前页码
- `page_size`: 每页条数
- `details`: 详细错误信息
- `request_id`: 请求 ID

示例:
```python
return ResponseModel.paginated_error(
    error_code="DB_CONNECTION_ERROR",
    message="数据库连接失败",
    http_code=500,
    page=1,
    page_size=20
)
```

## 使用示例

### 简单成功响应

```python
from backend.global_schemas import ResponseModel

@app.get("/api/v1/users/me")
async def get_current_user():
    user = {"id": 1, "username": "demo", "email": "demo@example.com"}
    return ResponseModel.success(data=user, message="获取当前用户信息成功")
```

### 错误响应

```python
from backend.global_schemas import ResponseModel

@app.get("/api/v1/users/{user_id}")
async def get_user(user_id: int):
    user = find_user(user_id)
    if not user:
        return ResponseModel.error(
            code="USER_NOT_FOUND",
            message=f"用户ID {user_id} 不存在",
            http_code=404
        )
    return ResponseModel.success(data=user)
```

### 分页响应

```python
from backend.global_schemas import ResponseModel

@app.get("/api/v1/images")
async def list_images(page: int = 1, page_size: int = 10):
    try:
        images, total = get_images_paginated(page, page_size)
        return ResponseModel.paginated_response(
            data=images,
            page=page,
            page_size=page_size,
            total_items=total,
            message="获取图片列表成功"
        )
    except Exception as e:
        return ResponseModel.paginated_error(
            error_code="DB_ERROR",
            message=f"获取图片列表失败: {str(e)}",
            http_code=500,
            page=page,
            page_size=page_size
        )
```

## 最佳实践

1. **统一使用 ResponseModel**: 所有 API 端点应统一使用 ResponseModel 封装响应，确保前端接收到统一格式的数据。

2. **适当使用错误代码**: 错误代码应当具有描述性，且在整个系统中保持一致，便于前端进行错误处理和国际化。

3. **避免暴露敏感信息**: 在错误响应中，应避免包含数据库连接字符串、密码等敏感信息。

4. **利用 request_id**: 在日志中记录 request_id，有助于在分布式系统中追踪请求链路。

5. **合理使用元数据**: 元数据字段可以包含额外的信息，如分页信息、统计数据等，但应避免过度使用。

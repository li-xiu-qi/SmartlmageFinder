from typing import Any, Dict, Generic, List, Optional, TypeVar, Union
from pydantic import BaseModel, Field, model_validator
from enum import Enum
from datetime import datetime
import uuid  # 导入uuid模块

T = TypeVar("T")

class StatusEnum(str, Enum):
    """响应状态枚举"""
    SUCCESS = "success"
    ERROR = "error"

class ErrorModel(BaseModel):
    """错误信息模型"""

    code: str = Field(..., description="错误代码")
    message: str = Field(..., description="错误描述")
    details: Optional[Dict[str, Any]] = Field(None, description="详细错误信息")

class PaginationMetadata(BaseModel):
    """分页元数据模型"""
    page: int = Field(1, description="当前页码")
    page_size: int = Field(10, description="每页条数")
    total_items: int = Field(0, description="总条目数")
    total_pages: int = Field(0, description="总页数")

class ResponseModel(BaseModel, Generic[T]):
    """通用API响应模型"""
    status: StatusEnum = Field(..., description="响应状态，success或error")
    code: int = Field(200, description="HTTP状态码")
    message: str = Field("", description="响应消息")
    data: Optional[T] = Field(None, description="响应数据")
    error: Optional[ErrorModel] = Field(None, description="错误信息，成功时为null")
    metadata: Dict[str, Any] = Field({}, description="附加元数据")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间戳")
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="请求ID，用于跟踪")
    
    # 为 Pydantic v2 添加配置
    model_config = {
        "arbitrary_types_allowed": True,
        "validate_assignment": True
    }
    
    @classmethod
    def success(
        cls, data: Any = None, message: str = "操作成功", 
        code: int = 200, metadata: Dict[str, Any] = None, 
        request_id: str = None
    ) -> "ResponseModel":
        if metadata is None:
            metadata = {}
        # 如果没有提供 request_id，则使用默认的生成函数
        if request_id is None:
            request_id = str(uuid.uuid4())
        return cls(
            status=StatusEnum.SUCCESS,
            code=code,
            message=message,
            data=data,
            error=None,
            metadata=metadata,
            request_id=request_id
        )
    
    @classmethod
    def error(
        cls, code: str, message: str, http_code: int = 400,
        details: Dict[str, Any] = None, request_id: str = None
    ) -> "ResponseModel":
        error = ErrorModel(code=code, message=message, details=details)
        # 如果没有提供 request_id，则使用默认的生成函数
        if request_id is None:
            request_id = str(uuid.uuid4())
        return cls(
            status=StatusEnum.ERROR,
            code=http_code,
            message=message,
            data=None,
            error=error,
            metadata={},
            request_id=request_id
        )
    @classmethod
    def paginated_response(
        cls, data: Any, page: int, page_size: int, 
        total_items: int, message: str = "获取数据成功",
        additional_metadata: Dict[str, Any] = None,
        request_id: str = None
    ) -> "ResponseModel":
        total_pages = (total_items + page_size - 1) // page_size if page_size > 0 else 0
        pagination = PaginationMetadata(
            page=page,
            page_size=page_size,
            total_items=total_items,
            total_pages=total_pages
        )
        
        metadata = {"pagination": pagination.model_dump()}  # 使用 model_dump() 替代 dict()
        if additional_metadata:
            metadata.update(additional_metadata)
            
        return cls.success(data=data, message=message, metadata=metadata, request_id=request_id)
    
    @classmethod
    def paginated_error(
        cls, error_code: str, message: str, http_code: int = 400,
        page: int = 1, page_size: int = 10, 
        details: Dict[str, Any] = None, request_id: str = None
    ) -> "ResponseModel":
        """处理分页查询失败的情况"""
        pagination = PaginationMetadata(
            page=page,
            page_size=page_size,
            total_items=0,
            total_pages=0
        )
        
        error = ErrorModel(code=error_code, message=message, details=details)
        # 如果没有提供 request_id，则使用默认的生成函数
        if request_id is None:
            request_id = str(uuid.uuid4())
        return cls(
            status=StatusEnum.ERROR,
            code=http_code,
            message=message,
            data=None,
            error=error,
            metadata={"pagination": pagination.model_dump()},  # 使用 model_dump() 替代 dict()
            request_id=request_id
        )

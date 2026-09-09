from typing import Any, Dict, List, Optional
from datetime import datetime
import uuid
import json


class ResponseModel:
    """简单的API响应模型 - 不使用Pydantic"""
    
    def __init__(self, status: str = "success", code: int = 200, message: str = "", 
                 data: Any = None, error: Any = None, metadata: Dict[str, Any] = None,
                 timestamp: datetime = None, request_id: str = None):
        self.status = status
        self.code = code
        self.message = message
        self.data = data
        self.error = error
        self.metadata = metadata or {}
        self.timestamp = timestamp or datetime.now()
        self.request_id = request_id or str(uuid.uuid4())
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "status": self.status,
            "code": self.code,
            "message": self.message,
            "data": self.data,
            "error": self.error,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
            "request_id": self.request_id
        }
    
    @classmethod
    def success(cls, data: Any = None, message: str = "操作成功", 
                code: int = 200, metadata: Dict[str, Any] = None, 
                request_id: str = None) -> "ResponseModel":
        """创建成功响应"""
        return cls(
            status="success",
            code=code,
            message=message,
            data=data,
            error=None,
            metadata=metadata or {},
            request_id=request_id
        )
    
    @classmethod
    def error(cls, code: str, message: str, http_code: int = 400,
              details: Dict[str, Any] = None, request_id: str = None) -> "ResponseModel":
        """创建错误响应"""
        error_info = {
            "code": code,
            "message": message,
            "details": details
        }
        return cls(
            status="error",
            code=http_code,
            message=message,
            data=None,
            error=error_info,
            metadata={},
            request_id=request_id
        )
    
    @classmethod
    def paginated_response(cls, data: Any, page: int, page_size: int, 
                          total_items: int, message: str = "获取数据成功",
                          additional_metadata: Dict[str, Any] = None,
                          request_id: str = None) -> "ResponseModel":
        """创建分页响应"""
        total_pages = (total_items + page_size - 1) // page_size if page_size > 0 else 0
        pagination = {
            "page": page,
            "page_size": page_size,
            "total_items": total_items,
            "total_pages": total_pages
        }
        
        metadata = {"pagination": pagination}
        if additional_metadata:
            metadata.update(additional_metadata)
            
        return cls.success(data=data, message=message, metadata=metadata, request_id=request_id)
    
    @classmethod
    def paginated_error(cls, error_code: str, message: str, http_code: int = 400,
                       page: int = 1, page_size: int = 10, 
                       details: Dict[str, Any] = None, request_id: str = None) -> "ResponseModel":
        """创建分页错误响应"""
        pagination = {
            "page": page,
            "page_size": page_size,
            "total_items": 0,
            "total_pages": 0
        }
        
        error_info = {
            "code": error_code,
            "message": message,
            "details": details
        }
        
        return cls(
            status="error",
            code=http_code,
            message=message,
            data=None,
            error=error_info,
            metadata={"pagination": pagination},
            request_id=request_id
        )

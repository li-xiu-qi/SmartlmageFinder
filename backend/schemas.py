from typing import Any, Dict, Generic, List, Optional, TypeVar, Union
from pydantic import BaseModel, Field
from enum import Enum

T = TypeVar('T')

# 定义搜索相关的枚举类
class SearchType(str, Enum):
    """定义搜索类型"""
    TEXT = "text"  # 传统文本匹配
    VECTOR = "vector"  # 向量搜索
    HYBRID = "hybrid"  # 混合搜索

class TextMatchMode(str, Enum):
    """文本匹配模式"""
    TITLE = "title"  # 只匹配标题
    DESCRIPTION = "description"  # 只匹配描述
    COMBINED = "combined"  # 标题+描述综合匹配

class VectorMatchMode(str, Enum):
    """向量匹配模式"""
    TITLE = "title"  # 标题向量
    DESCRIPTION = "description"  # 描述向量
    COMBINED = "combined"  # 标题+描述向量综合
    IMAGE = "image"  # 图片向量

class ImageVectorMatchMode(str, Enum):
    """图片向量匹配模式"""
    IMAGE = "image"  # 纯图片向量
    TITLE = "title"  # 图片对标题向量
    DESCRIPTION = "description"  # 图片对描述向量
    COMBINED = "combined"  # 综合匹配

class MetadataModel(BaseModel):
    """API响应的元数据部分"""
    page: Optional[int] = None
    page_size: Optional[int] = None
    total: Optional[int] = None
    total_pages: Optional[int] = None
    
class ErrorModel(BaseModel):
    """错误信息模型"""
    code: str = Field(..., description="错误代码")
    message: str = Field(..., description="错误描述")
    details: Optional[Dict[str, Any]] = Field(None, description="详细错误信息")

class ResponseModel(BaseModel, Generic[T]):
    """通用API响应模型"""
    status: str = Field(..., description="响应状态，success或error")
    data: Optional[T] = Field(None, description="响应数据")
    error: Optional[ErrorModel] = Field(None, description="错误信息，成功时为null")
    metadata: Dict[str, Any] = Field({}, description="元数据，如分页信息")
    
    @classmethod
    def success(cls, data: Any = None, metadata: Dict[str, Any] = None) -> "ResponseModel":
        """创建成功响应"""
        if metadata is None:
            metadata = {}
        return cls(status="success", data=data, error=None, metadata=metadata)
    
    @classmethod
    def error(cls, code: str, message: str, details: Dict[str, Any] = None) -> "ResponseModel":
        """创建错误响应"""
        error = ErrorModel(code=code, message=message, details=details)
        return cls(status="error", data=None, error=error, metadata={})

# 图片相关模型
class ImageBase(BaseModel):
    """图片基础信息"""
    title: Optional[str] = None
    description: Optional[str] = None
    
class ImageCreate(ImageBase):
    """创建图片时的信息"""
    filename: str
    filepath: str
    file_size: int
    file_type: str
    width: Optional[int] = None
    height: Optional[int] = None
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ImageUpdate(BaseModel):
    """更新图片的信息"""
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

class ImageResponse(ImageBase):
    """返回给前端的图片信息"""
    uuid: str
    filename: str
    filepath: str
    file_size: int
    file_type: str
    width: Optional[int] = None
    height: Optional[int] = None
    created_at: str
    updated_at: str
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ImageListItem(BaseModel):
    """图片列表项，用于列表展示"""
    uuid: str
    title: Optional[str] = None
    filepath: str
    created_at: str
    tags: List[str] = Field(default_factory=list)

# 搜索相关模型
class SearchResult(ImageListItem):
    """搜索结果项"""
    score: float = Field(..., description="相似度得分")
    
class TextSearchQuery(BaseModel):
    """文本搜索参数"""
    q: str = Field(..., description="搜索查询文本")
    mode: str = Field("vector", description="搜索模式：vector、text或hybrid")
    field: str = Field("all", description="搜索字段：title、description或all")
    limit: int = Field(20, description="返回结果数量限制")
    start_date: Optional[str] = Field(None, description="开始日期过滤")
    end_date: Optional[str] = Field(None, description="结束日期过滤")
    tags: Optional[str] = Field(None, description="标签过滤，逗号分隔")

# 标签相关模型
class TagModel(BaseModel):
    """标签模型"""
    name: str
    count: int

class TagAddRequest(BaseModel):
    """添加标签请求"""
    tags: List[str]

# 元数据相关模型
class MetadataFieldModel(BaseModel):
    """元数据字段模型"""
    name: str
    count: int
    type: str

class MetadataUpdateRequest(BaseModel):
    """更新元数据请求"""
    metadata: Dict[str, Any]

# AI生成相关模型
class GenerateRequest(BaseModel):
    """生成内容请求"""
    generate_title: bool = True
    generate_description: bool = True
    generate_tags: bool = True
    detail: str = "low"

class BatchGenerateRequest(BaseModel):
    """批量生成内容请求"""
    uuids: List[str]
    options: GenerateRequest

class GeneratedContent(BaseModel):
    """生成的内容"""
    title: Optional[str] = None
    description: Optional[str] = None
    tags: List[str] = Field(default_factory=list)

class TaskStatusResponse(BaseModel):
    """任务状态响应"""
    task_id: str
    status: str
    progress: Dict[str, int]
    results: Optional[List[Dict[str, Any]]] = None

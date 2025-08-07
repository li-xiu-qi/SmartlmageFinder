"""
数据仓库模块

重构后的数据仓库层，提供更清晰的数据访问接口：
- BaseRepository: 基础仓库类，提供通用数据库操作
- ImageRepository: 图片数据操作
- TagRepository: 标签数据操作  
- MetadataRepository: 元数据操作
- VectorRepository: 向量数据操作
- SearchRepository: 搜索相关操作
"""

from .base import BaseRepository
from .images import ImageRepository
from .tags import TagRepository
from .metadata import MetadataRepository
from .vectors import VectorRepository
from .search import SearchRepository

__all__ = [
    'BaseRepository',
    'ImageRepository',
    'TagRepository',
    'MetadataRepository', 
    'VectorRepository',
    'SearchRepository'
]

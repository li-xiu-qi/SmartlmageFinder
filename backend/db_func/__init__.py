"""
数据库功能模块

重构后的数据库模块，提供更清晰的架构和更好的可维护性：
- core/: 核心数据库功能（连接管理、初始化、扩展）
- repositories/: 数据仓库层，按业务领域组织
- utils/: 工具函数

主要接口：
- get_db_connection: 获取数据库连接
- initialize_database: 初始化数据库
- ImageRepository, TagRepository 等：各业务领域的数据操作
"""

from .core.connection import get_db_connection_from_pool, initialize_connection_pool, get_db
from .core.database import init_db
from .repositories.images import ImageRepository
from .repositories.tags import TagRepository
from .repositories.metadata import MetadataRepository
from .repositories.vectors import VectorRepository
from .repositories.search import SearchRepository

__all__ = [
    # 核心功能
    'get_db_connection_from_pool',
    'initialize_connection_pool', 
    'init_db',
    'get_db',
    
    # 数据仓库
    'ImageRepository',
    'TagRepository', 
    'MetadataRepository',
    'VectorRepository',
    'SearchRepository',
]

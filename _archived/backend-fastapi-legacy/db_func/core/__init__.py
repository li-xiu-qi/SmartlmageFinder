"""
数据库核心功能模块
"""

from .connection import (
    get_db_connection_from_pool, 
    initialize_connection_pool,
    get_db_connection,
    get_connection_pool
)
from .database import init_db
from .connection import get_db
from .extensions import setup_connection, PlatformDetector

__all__ = [
    'get_db_connection_from_pool',
    'initialize_connection_pool', 
    'get_db_connection',
    'get_connection_pool',
    'init_db',
    'get_db',
    'setup_connection',
    'PlatformDetector'
]

"""
扩展管理模块初始化
"""

from .loader import setup_connection
from ....config.platform_detector import PlatformDetector, auto_setup_driver

__all__ = ['setup_connection', 'PlatformDetector', 'auto_setup_driver']

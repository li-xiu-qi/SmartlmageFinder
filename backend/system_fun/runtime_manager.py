"""
运行时管理模块 - 负责跟踪应用程序的启动和运行时间
"""

import time
import platform
import sys
from datetime import datetime, timedelta
from typing import Dict, Any

from ..config import settings

# 记录应用启动时间
APP_START_TIME = time.time()
APP_START_DATETIME = datetime.fromtimestamp(APP_START_TIME)


def get_app_uptime() -> float:
    """获取应用程序已运行的时间（秒）
    
    Returns:
        float: 应用程序已运行的秒数
    """
    return time.time() - APP_START_TIME


def get_app_uptime_formatted() -> str:
    """获取格式化的应用程序运行时间
    
    Returns:
        str: 格式化的时间字符串 (例如: "2天 3小时 45分钟 30秒")
    """
    seconds = get_app_uptime()
    delta = timedelta(seconds=seconds)
    
    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    parts = []
    if days > 0:
        parts.append(f"{days}天")
    if hours > 0 or days > 0:
        parts.append(f"{hours}小时")
    if minutes > 0 or hours > 0 or days > 0:
        parts.append(f"{minutes}分钟")
    parts.append(f"{seconds}秒")
    
    return " ".join(parts)


def get_runtime_info() -> Dict[str, Any]:
    """获取应用运行时间信息
    
    Returns:
        Dict[str, Any]: 包含应用运行时间信息的字典
    """
    return {
        "app_uptime_formatted": get_app_uptime_formatted(),
        "current_time": datetime.now().isoformat()
    }


def get_models_info() -> Dict[str, Any]:
    """获取模型信息
    
    Returns:
        Dict[str, Any]: 模型信息字典
    """
    config = settings.get_config()
    return {
        "embedding_model": config.MODEL_PATH,
        "embedding_dimension": config.EMBEDDING_DIMENSION
    }


def get_system_info() -> Dict[str, Any]:
    """获取系统信息
    
    Returns:
        Dict[str, Any]: 系统信息字典
    """
    return {
        "version": "1.0.0", 
        "app_uptime": int(get_app_uptime()),
        "app_uptime_formatted": get_app_uptime_formatted(),
        "status": "healthy",  # 可以基于其他监控指标动态设置
        "platform": platform.system(),
        "python_version": sys.version.split()[0],
        "models_info": get_models_info()  # 添加模型信息
    }

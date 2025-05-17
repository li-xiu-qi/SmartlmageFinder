import os
import time
import platform
import psutil
import sys
import sqlite3
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

from backend import db_func
from ..config import settings
from .cache_info import get_cache_stats

class VectorDbDriverStatus(BaseModel):
    """向量数据库驱动状态模型"""
    status: str = Field(..., description="状态(available/missing/error)")
    path: str = Field(..., description="驱动路径")
    error: Optional[str] = Field(default=None, description="错误信息(如果有)")

class DatabaseStatus(BaseModel):
    """数据库状态模型"""
    status: str = Field(..., description="数据库连接状态")
    image_count: int = Field(default=0, description="图片数量")
    total_size: int = Field(default=0, description="总文件大小(字节)")
    tag_count: int = Field(default=0, description="标签数量")
    error: Optional[str] = Field(default=None, description="错误信息(如果有)")

class MultimodalApiStatus(BaseModel):
    """多模态API状态模型"""
    status: str = Field(default="enabled", description="API状态")
    model: str = Field(..., description="当前使用的模型")
    available_models: List[str] = Field(default_factory=list, description="可用的模型列表")
    api_base: str = Field(..., description="API基础URL")

class SystemInfo(BaseModel):
    """系统信息模型"""
    version: str = Field(..., description="系统版本")
    uptime: int = Field(..., description="运行时间(秒)")
    status: str = Field(..., description="系统健康状态")
    platform: str = Field(..., description="操作系统平台")
    python_version: str = Field(..., description="Python版本")

class ComponentsStatus(BaseModel):
    """组件状态模型"""
    database: Dict[str, Any] = Field(..., description="数据库状态")
    vector_db_driver: VectorDbDriverStatus = Field(..., description="向量数据库驱动状态")
    multimodal_api: MultimodalApiStatus = Field(..., description="多模态API状态")

class StorageInfo(BaseModel):
    """存储信息模型"""
    total_images: int = Field(..., description="总图片数量")
    total_size_mb: float = Field(..., description="总大小(MB)")
    total_tags: int = Field(..., description="总标签数量")
    upload_dir: str = Field(..., description="上传目录路径")

class CacheInfo(BaseModel):
    """缓存信息模型"""
    enabled: bool = Field(..., description="是否启用缓存")
    max_size_gb: float = Field(..., description="最大缓存大小(GB)")
    text_vector_cache: Dict[str, Any] = Field(..., description="文本向量缓存信息")
    image_vector_cache: Dict[str, Any] = Field(..., description="图像向量缓存信息")

class ModelsInfo(BaseModel):
    """模型信息"""
    embedding_model: str = Field(..., description="嵌入模型路径")

class ServerInfo(BaseModel):
    """服务器信息"""
    host: str = Field(..., description="主机地址")
    port: int = Field(..., description="端口号")

class SystemStatus(BaseModel):
    """完整系统状态模型"""
    system: SystemInfo
    components: ComponentsStatus
    storage: StorageInfo
    cache: CacheInfo
    models: ModelsInfo
    server: ServerInfo

def check_vector_db_driver_status() -> VectorDbDriverStatus:
    """检查向量数据库驱动状态"""
    config = settings.get_config()
    driver_path = config.VECTOR_DB_DRIVER
    
    if not driver_path or not os.path.exists(driver_path):
        return VectorDbDriverStatus(
            status="missing",
            path=driver_path
        )
    
    try:
        # 仅检查文件是否存在和可读
        with open(driver_path, 'rb') as f:
            # 只读取一小部分以验证文件可访问
            f.read(1)
        return VectorDbDriverStatus(
            status="available",
            path=driver_path
        )
    except Exception as e:
        return VectorDbDriverStatus(
            status="error",
            path=driver_path,
            error=str(e)
        )

def get_database_status(conn: sqlite3.Connection = None) -> DatabaseStatus:
    """获取数据库状态信息"""
    try:
        
        cursor = conn.cursor()
        
        # 检查images表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='images'")
        has_images_table = cursor.fetchone() is not None
        
        if has_images_table:
            cursor.execute("SELECT COUNT(*) FROM images")
            
            image_count = cursor.fetchone()[0]    
              
            cursor.execute("SELECT SUM(file_size) FROM images")
            total_size = cursor.fetchone()[0] or 0
        else:
            image_count = 0
            total_size = 0
            
        # 获取标签总数
        from ..db_func.tags_func.get_tags import get_all_tags
        tags = get_all_tags(conn)  # 使用正确的函数并传入数据库连接
        tag_count = len(tags)
            
        db_status = "connected"
        # 不关闭传入的连接，它由调用者管理
        
        return DatabaseStatus(
            status=db_status,
            image_count=image_count,
            total_size=total_size,
            tag_count=tag_count
        )
    except Exception as e:
        print(f"数据库连接错误: {e}")
        return DatabaseStatus(
            status="error",
            image_count=0,
            total_size=0,
            tag_count=0,
            error=str(e)
        )

def get_system_status_data(conn: sqlite3.Connection = None) -> Dict[str, Any]:
    """获取完整的系统状态数据"""
    # 获取系统运行信息
    uptime = time.time() - psutil.boot_time()
    config = settings.get_config()
    
    # 获取数据库信息
    db_info = get_database_status(conn)
    
    # 获取缓存统计
    cache_info = get_cache_stats()
    
    # 检查向量数据库驱动状态
    vector_db_driver_status = check_vector_db_driver_status()
    
    # 构建响应数据
    system_status = {
        "system": {
            "version": "1.0.0",
            "uptime": int(uptime),
            "status": "healthy",
            "platform": platform.system(),
            "python_version": sys.version.split()[0]
        },
        "components": {
            "database": {
                "status": db_info.status,
                "type": "sqlite",
                "path": config.DB_PATH
            },
            "vector_db_driver": vector_db_driver_status.dict(),
            "multimodal_api": {
                "status": "enabled",
                "model": config.VISION_MODEL,
                "available_models": config.AVAILABLE_VISION_MODELS,
                "api_base": config.OPENAI_API_BASE
            }
        },
        "storage": {
            "total_images": db_info.image_count,
            "total_size_mb": round(db_info.total_size / (1024 * 1024), 2),
            "total_tags": db_info.tag_count,
            "upload_dir": config.UPLOAD_DIR,
        },
        "cache": {
            "enabled": config.USE_CACHE,
            "max_size_gb": config.MAX_CACHE_SIZE_GB,
            "text_vector_cache": {
                "path": config.TEXT_VECTOR_CACHE_DIR,
                "entries": cache_info.text_vector_cache.entries,
                "size_mb": cache_info.text_vector_cache.size_mb
            },
            "image_vector_cache": {
                "path": config.IMAGE_VECTOR_CACHE_DIR,
                "entries": cache_info.image_vector_cache.entries,
                "size_mb": cache_info.image_vector_cache.size_mb
            }
        },
        "models": {
            "embedding_model": config.MODEL_PATH
        },
        "server": {
            "host": config.HOST,
            "port": config.PORT
        }
    }
    
    return system_status

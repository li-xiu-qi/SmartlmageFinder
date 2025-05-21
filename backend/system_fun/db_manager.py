"""
数据库状态管理模块 - 负责获取和管理数据库状态信息
"""

import os
import sqlite3
import traceback
from typing import Dict, Tuple, Any, Optional

from ..config import settings
from ..db_func.utils import row_to_dict, rows_to_dicts


def check_table_exists(conn: sqlite3.Connection, table_name: str) -> bool:
    """检查指定表是否存在"""
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
    return cursor.fetchone() is not None


def get_image_statistics(conn: sqlite3.Connection) -> Tuple[int, int]:
    """获取图片统计信息：数量和总大小"""
    cursor = conn.cursor()
    
    image_count = 0
    total_size = 0
    
    if check_table_exists(conn, 'images'):
        print("表 images 存在，获取图片统计信息")
        cursor.execute("SELECT COUNT(*) AS count FROM images")
        image_count_row = cursor.fetchone()
        if image_count_row:
            image_count = row_to_dict(image_count_row)['count']
        
        cursor.execute("SELECT SUM(file_size) AS total_size FROM images")
        total_size_row = cursor.fetchone()
        if total_size_row:
            size_val = row_to_dict(total_size_row)['total_size']
            total_size = size_val if size_val is not None else 0
    else:
        print("表 images 不存在，无法获取图片统计信息")
        
    return image_count, total_size


def get_tag_count(conn: sqlite3.Connection) -> int:
    """获取标签总数"""
    try:
        from ..db_func.tags_func.get_tags import get_all_tags
        tags = get_all_tags(conn)
        return len(tags)
    except Exception as e:
        print(f"获取标签数量失败: {e}")
        return 0


def check_vector_db_status(conn: sqlite3.Connection) -> bool:
    """检查向量数据库状态"""
    try:
        cursor = conn.cursor()
        # 尝试执行向量数据库特有的函数来检查是否正常
        cursor.execute("SELECT vec_version()")
        return True
    except Exception:
        return False


def get_db_version(conn: sqlite3.Connection) -> str:
    """获取SQLite数据库版本"""
    cursor = conn.cursor()
    cursor.execute("SELECT sqlite_version() AS version")
    result = cursor.fetchone()
    result_dict = row_to_dict(result) 
    return result_dict["version"]





def get_database_info(conn: Optional[sqlite3.Connection] = None) -> Dict[str, Any]:
    """获取数据库状态信息，整合各个子函数的结果
    
    Args:
        conn: 数据库连接，如不提供则创建新连接
        
    Returns:
        Dict[str, Any]: 数据库状态信息
    """
    
    # 设置统一的row_factory确保数据访问一致性
    conn.row_factory = sqlite3.Row

    try:
        config = settings.get_config()
        
        # 获取各项统计信息
        image_count, total_size = get_image_statistics(conn)
        tag_count = get_tag_count(conn)
        vector_status = check_vector_db_status(conn)
        db_version = get_db_version(conn)
        
        db_status = "connected"
        
        return {
            "status": db_status,
            "type": "sqlite",
            "path": config.DB_PATH,
            "image_count": image_count,
            "total_size": total_size,
            "tag_count": tag_count,
            "vector_status": vector_status,
            "db_version": db_version,
            "error": None  # 成功时明确设置错误为 None
        }
    except Exception as e:
        error_msg = f"数据库连接错误: {e}\n{traceback.format_exc()}"
        print(error_msg)
        return {
            "status": "error",
            "type": "sqlite",
            "path": settings.get_config().DB_PATH,
            "image_count": 0,
            "total_size": 0,
            "tag_count": 0,
            "vector_status": False,
            "db_version": "未知",
            "tables_info": {},
            "error": str(e)
        }

            
def get_storage_info(conn: Optional[sqlite3.Connection] = None) -> Dict[str, Any]:
    """获取存储统计信息
    
    Args:
        conn: 数据库连接，如不提供则创建新连接
        
    Returns:
        Dict[str, Any]: 存储统计信息
    """
    # 获取基础数据库信息
    db_info = get_database_info(conn)
    config = settings.get_config()
    
    return {
        "total_images": db_info["image_count"],
        "total_size_mb": round(db_info["total_size"] / (1024 * 1024), 2),
        "total_tags": db_info["tag_count"],
        "upload_dir": config.UPLOAD_DIR
    }

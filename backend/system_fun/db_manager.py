"""
数据库状态管理模块 - 负责获取和管理数据库状态信息
"""

import os
import sqlite3
import traceback
from typing import Dict, Tuple, Any, Optional

from ..config import settings
from ..db_func.core import get_db_connection, dict_factory


def check_table_exists(conn: sqlite3.Connection, table_name: str) -> bool:
    """检查指定表是否存在"""
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
    return cursor.fetchone() is not None


def get_image_statistics(conn: sqlite3.Connection) -> Tuple[int, int]:
    """获取图片统计信息：数量和总大小"""
    cursor = conn.cursor()
    
    if check_table_exists(conn, 'images'):
        cursor.execute("SELECT COUNT(*) FROM images")
        image_count = cursor.fetchone()[0]    
        
        cursor.execute("SELECT SUM(file_size) FROM images")
        total_size = cursor.fetchone()[0] or 0
    else:
        image_count = 0
        total_size = 0
        
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
    cursor.execute("SELECT sqlite_version()")
    return cursor.fetchone()[0]


def get_tables_info(conn: sqlite3.Connection) -> Dict[str, int]:
    """获取数据库中所有表的信息及记录数"""
    cursor = conn.cursor()
    tables_info = {}
    
    # 获取所有表名
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    
    # 获取每个表的记录数
    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            tables_info[table] = count
        except sqlite3.Error as e:
            print(f"Error counting rows in table {table}: {e}")
            tables_info[table] = -1  # 标记错误或不可用的计数
    
    return tables_info


def get_database_info(conn: Optional[sqlite3.Connection] = None) -> Dict[str, Any]:
    """获取数据库状态信息，整合各个子函数的结果
    
    Args:
        conn: 数据库连接，如不提供则创建新连接
        
    Returns:
        Dict[str, Any]: 数据库状态信息
    """
    # 如果没有传入连接，则创建新连接
    connection_created = False
    if conn is None:
        conn = get_db_connection()
        connection_created = True
        conn.row_factory = dict_factory  # 确保使用字典工厂

    try:
        config = settings.get_config()
        
        # 获取各项统计信息
        image_count, total_size = get_image_statistics(conn)
        tag_count = get_tag_count(conn)
        vector_status = check_vector_db_status(conn)
        db_version = get_db_version(conn)
        tables_info = get_tables_info(conn)
        
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
            "tables_info": tables_info,
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
    finally:
        # 只关闭我们自己创建的连接
        if connection_created and conn:
            conn.close()
            
            
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

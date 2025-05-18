"""
创建图片记录相关函数
"""
import os
import sqlite3
import json
from typing import Dict, Any
from datetime import datetime

from backend.db_func.utils import python_to_json_for_db
from ..vector_func.add_image_vectors import add_image_vector
from ..vector_func.add_text_vectors import add_title_vector, add_description_vector

def add_image_to_database(conn: sqlite3.Connection, image_data: Dict[str, Any]) -> int:
    """插入图片记录到数据库
    
    Args:
        conn: SQLite数据库连接对象
        image_data: 图片数据字典
        
    Returns:
        新插入记录的ID
    """
    cursor = conn.cursor()
    
    # 确保时间字段使用标准 ISO 8601 格式 (包含微秒)
    current_time_iso = datetime.now().isoformat(timespec='microseconds')
    
    # 插入图片元数据
    sql = """
    INSERT INTO images (
        filename, filepath, title, description, 
        file_size, file_type, width, height,
        created_at, updated_at, metadata, tags
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    
    params = (
        image_data.get("filename", ""),
        image_data.get("filepath", ""),
        image_data.get("title", ""),
        image_data.get("description", ""),
        image_data.get("file_size", 0),
        image_data.get("file_type", ""),
        image_data.get("width", 0),
        image_data.get("height", 0),
        image_data.get("created_at", current_time_iso), # Use ISO format
        current_time_iso, # Use ISO format for updated_at
        python_to_json_for_db(image_data.get("metadata", {}), {}),
        python_to_json_for_db(image_data.get("tags", []), [])
    )
    
    cursor.execute(sql, params)
    image_id = cursor.lastrowid
    conn.commit()
    
    # 生成各类向量
    filepath = image_data.get("filepath", "")
    title = image_data.get("title", "")
    description = image_data.get("description", "")
    
    # 生成图像向量
    add_image_vector(conn, image_id, filepath)
    
    # 生成标题向量
    add_title_vector(conn, image_id, title)
    
    # 生成描述向量
    add_description_vector(conn, image_id, description)
    
    return image_id



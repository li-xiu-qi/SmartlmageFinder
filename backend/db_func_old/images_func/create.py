"""
创建图片记录相关函数
"""
import os
import sqlite3
import json
from typing import Dict, Any, List
from datetime import datetime

from backend.db_func.utils import python_to_json_for_db
from ..vector_func.add_image_vectors import add_image_vector
from ..vector_func.add_text_vectors import add_title_vector, add_description_vector
from ..vector_func.batch_vectors import batch_add_vectors_for_images

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


def batch_add_images_to_database(conn: sqlite3.Connection, 
                                 images_data: List[Dict[str, Any]]) -> List[int]:
    """批量插入图片记录到数据库并生成向量
    
    Args:
        conn: SQLite数据库连接对象
        images_data: 图片数据字典列表
        
    Returns:
        新插入记录的ID列表
    """
    if not images_data:
        return []
    
    print(f"开始批量插入图片记录，共 {len(images_data)} 条记录")
    
    # 使用事务确保数据一致性
    conn.execute("BEGIN IMMEDIATE")
    
    try:
        cursor = conn.cursor()
        
        # 确保时间字段使用标准 ISO 8601 格式 (包含微秒)
        current_time_iso = datetime.now().isoformat(timespec='microseconds')
        
        # 插入图片元数据 - 批量插入
        sql = """
        INSERT INTO images (
            filename, filepath, title, description, 
            file_size, file_type, width, height,
            created_at, updated_at, metadata, tags
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        # 准备批量插入的数据
        batch_params = []
        for image_data in images_data:
            params = (
                image_data.get("filename", ""),
                image_data.get("filepath", ""),
                image_data.get("title", ""),
                image_data.get("description", ""),
                image_data.get("file_size", 0),
                image_data.get("file_type", ""),
                image_data.get("width", 0),
                image_data.get("height", 0),
                image_data.get("created_at", current_time_iso),
                current_time_iso,
                python_to_json_for_db(image_data.get("metadata", {}), {}),
                python_to_json_for_db(image_data.get("tags", []), [])
            )
            batch_params.append(params)
        
        # 由于SQLite在批量插入时lastrowid的行为不一致，我们采用逐个插入的方式
        # 这样能确保正确获取每个记录的ID，并避免数据库锁定问题
        image_ids = []
        for params in batch_params:
            cursor.execute(sql, params)
            image_id = cursor.lastrowid
            if image_id:
                image_ids.append(image_id)
            else:
                raise Exception("插入记录失败，无法获取插入ID")
        
        # 提交图片记录插入
        conn.commit()
        print(f"批量插入图片记录成功，共 {len(image_ids)} 条记录")
        
        # 准备批量向量生成的数据
        vector_data_list = []
        for i, image_data in enumerate(images_data):
            vector_data = {
                'image_id': image_ids[i],
                'filepath': image_data.get("filepath", ""),
                'title': image_data.get("title", ""),
                'description': image_data.get("description", "")
            }
            vector_data_list.append(vector_data)
        
        # 批量生成向量
        try:
            success_ids = batch_add_vectors_for_images(conn, vector_data_list)
            print(f"批量生成向量完成，成功处理 {len(success_ids)} 张图片")
        except Exception as e:
            print(f"批量生成向量失败: {e}")
            # 即使向量生成失败，图片记录已经插入，所以仍然返回图片ID
        
        return image_ids
        
    except Exception as e:
        print(f"批量插入过程中发生错误: {e}")
        conn.rollback()
        raise e



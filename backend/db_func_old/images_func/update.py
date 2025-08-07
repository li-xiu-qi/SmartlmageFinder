"""
更新图片记录相关函数
"""
import sqlite3
from typing import Dict, Any, List
from datetime import datetime

from backend.db_func.utils import python_to_json_for_db
from backend.db_func.vector_func.add_text_vectors import add_description_vector, add_title_vector

from ..vector_func.delete_vectors import delete_vector_by_type

def update_image(conn: sqlite3.Connection, image_id: int, update_data: Dict[str, Any]) -> bool:
    """
    更新图片信息
    
    Args:
        conn: 数据库连接
        image_id: 图片ID
        update_data: 要更新的字段数据
        
    Returns:
        bool: 更新是否成功
    """
    cursor = conn.cursor()
    
    # 检查图片是否存在
    cursor.execute("SELECT id FROM images WHERE id = ?", (image_id,))
    if not cursor.fetchone():
        return False
    
    # 准备要更新的字段
    update_fields = []
    params = []
    
    title_updated = False
    description_updated = False
    title_value = None
    description_value = None
    
    # 处理标题和描述字段，同时记录更新的值
    for field in ['title', 'description']:
        if field in update_data:
            field_value = update_data[field]
            update_fields.append(f"{field} = ?")
            params.append(field_value)
            
            if field == 'title':
                title_updated = True
                title_value = field_value
            elif field == 'description':
                description_updated = True
                description_value = field_value
    
    # 处理标签和元数据，使用工具函数
    if 'tags' in update_data:
        update_fields.append("tags = ?")
        params.append(python_to_json_for_db(update_data['tags'], []))
    
    if 'metadata' in update_data:
        update_fields.append("metadata = ?")
        params.append(python_to_json_for_db(update_data['metadata'], {}))
    
    # 更新时间戳
    update_fields.append("updated_at = ?")
    params.append(datetime.now().isoformat(timespec='microseconds')) # Ensure microseconds
    
    # 添加ID参数
    params.append(image_id)
    
    # 执行更新
    if update_fields:
        query = f"UPDATE images SET {', '.join(update_fields)} WHERE id = ?"
        cursor.execute(query, params)
        conn.commit()
    
    # 更新向量索引
    try:
        # 只有在标题或描述有更新时才处理向量
        if title_updated:
            if title_value:  # 如果标题有值，更新向量
                add_title_vector(conn, image_id, title_value)
            else:  # 如果标题为空，删除向量
                delete_vector_by_type(conn, image_id, 'title_vectors')
        
        if description_updated:
            if description_value:  # 如果描述有值，更新向量
                add_description_vector(conn, image_id, description_value)
            else:  # 如果描述为空，删除向量
                delete_vector_by_type(conn, image_id, 'description_vectors')
    except Exception as e:
        print(f"更新文本向量失败: {e}")
    
    # 返回更新成功
    return True

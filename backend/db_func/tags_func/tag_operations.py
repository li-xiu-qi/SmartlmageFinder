"""
标签管理相关函数
"""
import sqlite3
import json
from typing import List, Dict, Any

from backend.db_func.images_func.utils import python_to_json_for_db


def get_image_tags(conn: sqlite3.Connection, image_id: int) -> List[str]:
    """
    获取图片的所有标签
    
    Args:
        conn: 数据库连接
        image_id: 图片ID
        
    Returns:
        List[str]: 标签列表
    """
    cursor = conn.cursor()
    cursor.execute("SELECT tags FROM images WHERE id = ?", (image_id,))
    result = cursor.fetchone()
    
    if not result:
        return []
    
    tags_json = result[0]
    if not tags_json:
        return []
    
    try:
        return json.loads(tags_json)
    except json.JSONDecodeError:
        return []

def update_tags(conn: sqlite3.Connection, image_id: int, tags: List[str]) -> List[str]:
    """
    更新图片的标签（覆盖方式）
    
    Args:
        conn: 数据库连接
        image_id: 图片ID
        tags: 新的标签列表（将完全替换旧的标签）
        
    Returns:
        List[str]: 更新后的标签列表
    """
    # 去重
    unique_tags = list(set(tags))
    
    # 更新数据库
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE images SET tags = ?, updated_at = datetime('now') WHERE id = ?",
        (python_to_json_for_db(unique_tags, []), image_id)
    )
    conn.commit()
    
    return unique_tags


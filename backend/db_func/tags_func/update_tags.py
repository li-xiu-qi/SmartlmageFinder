"""
标签更新相关功能
"""
import json
import sqlite3
from typing import Dict, List, Any


def update_image_tags(conn: sqlite3.Connection, image_id: int, tags: List[str]) -> bool:
    """更新图片的标签列表"""
    cursor = conn.cursor()
    
    # 检查图片是否存在
    cursor.execute("SELECT id FROM images WHERE id = ?", (image_id,))
    if not cursor.fetchone():
        return False
    
    # 更新标签
    tags_json = json.dumps(tags, ensure_ascii=False)
    cursor.execute("UPDATE images SET tags = ? WHERE id = ?", (tags_json, image_id))
    conn.commit()
    
    return True


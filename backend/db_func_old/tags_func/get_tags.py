"""
标签获取相关功能
"""
import json
import sqlite3
from typing import Dict, List, Set

from ..utils import rows_to_dicts

def get_all_tags(conn: sqlite3.Connection) -> List[str]:
    """获取系统中所有标签"""
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 获取所有图片的标签字段
    cursor.execute("SELECT tags FROM images WHERE tags IS NOT NULL AND tags != '[]'")
    results = cursor.fetchall()
    
    # 提取并合并所有标签
    all_tags: Set[str] = set()
    for row in results:
        tags = json.loads(row['tags'])
        all_tags.update(tags)
    return sorted(list(all_tags))

def get_tags_count(conn: sqlite3.Connection) -> Dict[str, int]:
    """获取标签使用次数统计"""
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 获取所有图片的标签字段
    cursor.execute("SELECT tags FROM images WHERE tags IS NOT NULL AND tags != '[]'")
    results = cursor.fetchall()
    
    # 将查询结果转换为字典列表
    results_dicts = rows_to_dicts(results)
      # 统计每个标签的出现次数
    tag_counts: Dict[str, int] = {}
    for row in results_dicts:
        tags = json.loads(row['tags'])
        for tag in tags:
            if tag in tag_counts:
                tag_counts[tag] += 1
            else:
                tag_counts[tag] = 1
    
    return tag_counts


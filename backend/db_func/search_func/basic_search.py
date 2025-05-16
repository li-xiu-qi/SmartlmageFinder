"""
基本搜索功能模块，提供基于文本条件的图像过滤。
"""
import sqlite3
from typing import List, Dict, Any
from datetime import datetime

def format_datetime(dt):
    """将datetime对象格式化为标准格式字符串"""
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def get_filtered_image_ids(conn: sqlite3.Connection, filters: Dict[str, Any]) -> List[int]:
    """
    根据过滤条件查询符合的图像ID。

    Args:
        conn: SQLite数据库连接对象。
        filters: 过滤条件字典，可以包含以下键：
            - filename: 按文件名模糊匹配
            - title: 按标题模糊匹配
            - description: 按描述模糊匹配
            - tags: 按标签过滤 (列表，对JSON数组成员进行OR逻辑匹配)
            - start_date: 按创建时间过滤（起始时间 YYYY-MM-DD HH:MM:SS）
            - end_date: 按创建时间过滤（结束时间 YYYY-MM-DD HH:MM:SS）

    Returns:
        一个符合条件的图像ID列表。
    """
    cursor = conn.cursor()
    filter_query = "SELECT images.id FROM images WHERE 1=1"
    filter_params = []

    if filters.get('filename'):
        filter_query += " AND images.filename LIKE ?"
        filter_params.append(f"%{filters['filename']}%")

    if filters.get('title'):
        filter_query += " AND images.title LIKE ?"
        filter_params.append(f"%{filters['title']}%")

    if filters.get('description'):
        filter_query += " AND images.description LIKE ?"
        filter_params.append(f"%{filters['description']}%")

    # 时间过滤与test_db_vec_search.py保持一致
    if filters.get('start_date'):
        filter_query += " AND images.created_at >= ?"
        filter_params.append(filters['start_date'])

    if filters.get('end_date'):
        filter_query += " AND images.created_at <= ?"
        filter_params.append(filters['end_date'])

    if filters.get('tags'):
        tags_filter_values = filters['tags']
        if isinstance(tags_filter_values, list) and tags_filter_values:
            tag_conditions = []
            for tag_value in tags_filter_values:
                tag_conditions.append("images.tags LIKE ?")
                filter_params.append(f"%{tag_value}%")
            if tag_conditions:
                filter_query += f" AND ({ ' OR '.join(tag_conditions) })"

    cursor.execute(filter_query, tuple(filter_params))
    filtered_ids = [row[0] for row in cursor.fetchall()]
    return filtered_ids
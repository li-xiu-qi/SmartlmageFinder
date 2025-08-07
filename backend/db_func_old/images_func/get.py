"""
图片获取相关函数
"""

import sqlite3
from typing import Dict, List, Any, Optional, Tuple

from ..utils import json_from_db_to_python, rows_to_dicts, row_to_dict


def get_image_by_id(
    conn: sqlite3.Connection,
    image_id: int,
) -> Optional[Dict[str, Any]]:
    """通过ID获取图片信息"""
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()    
    cursor.execute("SELECT * FROM images WHERE id = ?", (image_id,))
    raw_image = cursor.fetchone()
    image = row_to_dict(raw_image) if raw_image else None
    # 处理JSON字段
    return json_from_db_to_python(image)


def get_images(
    conn: sqlite3.Connection,
    page: int = 1,
    page_size: int = 20,
    sort_by: str = "created_at",
    order: str = "desc",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    tags: Optional[List[str]] = None,
) -> Tuple[List[Dict[str, Any]], int]:
    """获取图片列表，支持分页和过滤"""

    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = "SELECT * FROM images"
    count_query = "SELECT COUNT(*) as count FROM images"

    conditions = []
    params = []

    # 添加过滤条件
    if start_date:
        conditions.append("created_at >= ?")
        params.append(start_date)

    if end_date:
        conditions.append("created_at <= ?")
        params.append(end_date)

    # 改进标签过滤逻辑
    if tags and len(tags) > 0:
        tag_conditions = []
        for tag in tags:
            # 使用JSON包含检查，查找包含特定标签的图片
            tag_conditions.append("tags LIKE ?")
            # 对特定标签进行精确匹配
            params.append(f'%"{tag}"%')
        conditions.append("(" + " OR ".join(tag_conditions) + ")")

    # 组合查询条件
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
        count_query += " WHERE " + " AND ".join(conditions)

    # 添加排序和分页
    query += f" ORDER BY {sort_by} {order}"
    query += f" LIMIT {page_size} OFFSET {(page - 1) * page_size}"    # 执行查询
    cursor.execute(query, params)
    raw_images = cursor.fetchall()
    images = rows_to_dicts(raw_images)

    # 执行计数查询
    cursor.execute(count_query, params)
    count_result = cursor.fetchone()
    total_count = row_to_dict(count_result)["count"]

    # 处理JSON字段
    processed_images = [json_from_db_to_python(image) for image in images]
    return processed_images, total_count


def get_images_by_ids(
    image_ids: List[int], conn: sqlite3.Connection
) -> List[Dict[str, Any]]:
    """批量获取图片信息"""
    if not image_ids:
        return []

    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    placeholders = ", ".join(["?"] * len(image_ids))
    query = f"SELECT * FROM images WHERE id IN ({placeholders})"    
    cursor.execute(query, image_ids)
    raw_images = cursor.fetchall()
    images = rows_to_dicts(raw_images)

    # 处理JSON字段并返回
    return [json_from_db_to_python(image) for image in images]


def get_images_by_tag(conn: sqlite3.Connection, tag: str) -> List[int]:
    """获取包含指定标签的所有图片ID"""
    cursor = conn.cursor()

    # 查找包含特定标签的图片
    cursor.execute("SELECT id FROM images WHERE tags LIKE ?", (f'%"{tag}"%',))
    results = cursor.fetchall()

    # 返回图片ID列表
    return [row[0] for row in results]

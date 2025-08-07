"""
多维向量搜索功能模块，提供结合多种向量类型（标题、描述、图像）的混合向量检索。
"""
import sqlite3
import json
from typing import List, Dict, Any, Optional, Union

from .basic_search import get_filtered_image_ids
from ...ai_func.generate_vector import encode_text, encode_image
from ..utils import json_from_db_to_python, rows_to_dicts


def text_search(
    conn: sqlite3.Connection,
    text_query: str,
    search_targets: List[str] = ["title", "description", "image"],
    filters: Optional[Dict[str, Any]] = None,
    limit: int = 20,
    offset: int = 0
) -> List[Dict[str, Any]]:
    """
    使用文本查询执行多维向量搜索。
    
    Args:
        conn: 数据库连接对象
        text_query: 文本查询内容
        search_targets: 要搜索的目标类型列表，可包含："title", "description", "image"
        filters: 过滤条件字典
        limit: 返回结果的最大数量
        offset: 结果的起始偏移量，用于分页
        
    Returns:
        图像信息字典的列表，按综合得分排序
    """
    # 设置 row_factory 以便能够正确处理查询结果
    conn.row_factory = sqlite3.Row
    
    # 将文本转换为向量
    query_embedding = encode_text(text_query).tolist()
    
    # 执行向量搜索
    return _vector_search(
        conn=conn,
        query_embedding=query_embedding,
        search_targets=search_targets,
        filters=filters,
        limit=limit,
        offset=offset,
        exclude_image_id=None
    )


def image_search(
    conn: sqlite3.Connection,
    image_path: str,
    search_targets: List[str] = ["title", "description", "image"],
    filters: Optional[Dict[str, Any]] = None,
    limit: int = 20,
    offset: int = 0
) -> List[Dict[str, Any]]:
    """
    使用图像路径执行多维向量搜索。
    
    Args:
        conn: 数据库连接对象
        image_path: 图像文件路径
        search_targets: 要搜索的目标类型列表，可包含："title", "description", "image"
        filters: 过滤条件字典
        limit: 返回结果的最大数量
        offset: 结果的起始偏移量，用于分页
        
    Returns:
        图像信息字典的列表，按综合得分排序
    """
    # 设置 row_factory 以便能够正确处理查询结果
    conn.row_factory = sqlite3.Row
    
    # 将图像转换为向量
    query_embedding = encode_image(image_path).tolist()
    
    # 执行向量搜索
    return _vector_search(
        conn=conn,
        query_embedding=query_embedding,
        search_targets=search_targets,
        filters=filters,
        limit=limit,
        offset=offset,
        exclude_image_id=None
    )


def image_id_search(
    conn: sqlite3.Connection,
    image_id: int,
    search_targets: List[str] = ["title", "description", "image"],
    filters: Optional[Dict[str, Any]] = None,
    limit: int = 20,
    offset: int = 0,
    exclude_self: bool = True
) -> List[Dict[str, Any]]:
    """
    使用图像ID执行多维向量搜索。
    
    Args:
        conn: 数据库连接对象
        image_id: 数据库中的图像ID
        search_targets: 要搜索的目标类型列表，可包含："title", "description", "image"
        filters: 过滤条件字典
        limit: 返回结果的最大数量
        offset: 结果的起始偏移量，用于分页
        exclude_self: 是否从结果中排除查询图像本身
        
    Returns:
        图像信息字典的列表，按综合得分排序
    """
    # 设置 row_factory 以便能够正确处理查询结果
    conn.row_factory = sqlite3.Row
    
    # 检查图像是否存在
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM images WHERE id = ?", (image_id,))
    if not cursor.fetchone():
        raise ValueError(f"未找到ID为 {image_id} 的图像")
    
    # 获取图像向量
    if not search_targets:
        raise ValueError("search_targets 不能为空")
    
    # 使用第一个搜索目标类型的向量作为查询向量
    target_type = search_targets[0]
    vector_table = f"{target_type}_vectors"
    
    cursor.execute(f"SELECT embedding FROM {vector_table} WHERE image_id = ?", (image_id,))
    vector_row = cursor.fetchone()
    
    if not vector_row:
        raise ValueError(f"未找到ID为 {image_id} 的图像的 {target_type} 向量")
    
    query_embedding = json.loads(vector_row[0])
    
    # 执行向量搜索
    exclude_id = image_id if exclude_self else None
    return _vector_search(
        conn=conn,
        query_embedding=query_embedding,
        search_targets=search_targets,
        filters=filters,
        limit=limit,
        offset=offset,
        exclude_image_id=exclude_id
    )


def _vector_search(
    conn: sqlite3.Connection,
    query_embedding: List[float],
    search_targets: List[str],
    filters: Optional[Dict[str, Any]] = None,
    limit: int = 20,
    offset: int = 0,
    exclude_image_id: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    使用向量表示执行多维向量搜索的内部函数。
    
    Args:
        conn: 数据库连接对象
        query_embedding: 查询内容的向量表示
        search_targets: 要搜索的目标类型列表
        filters: 过滤条件字典
        limit: 返回结果的最大数量
        offset: 结果的起始偏移量，用于分页
        exclude_image_id: 要从结果中排除的图像ID
        
    Returns:
        图像信息字典的列表，按综合得分排序
    """
    # 设置 row_factory 以便能够正确处理查询结果
    conn.row_factory = sqlite3.Row
    
    filters = filters or {}
      # 检查参数有效性
    if not search_targets or not all(t in ["title", "description", "image"] for t in search_targets):
        raise ValueError("search_targets 必须包含有效的目标类型：'title', 'description', 'image'")
      # 首先根据过滤条件获取符合条件的图像ID
    filtered_ids = get_filtered_image_ids(conn, filters)
    # A如果需要排除自身，从过滤结果中移除查询图像ID
    if exclude_image_id is not None and exclude_image_id in filtered_ids:
        filtered_ids.remove(exclude_image_id)
        
    if not filtered_ids:
        return []
      # 2. 构建联合SQL查询，直接在SQL中计算多维向量搜索得分
    # 为每个搜索目标(title, description, image)创建子查询
    subqueries = []
    
    for target_type in search_targets:
        vector_table = f"{target_type}_vectors"
        filtered_ids_str = ','.join(str(id) for id in filtered_ids)
        
        subquery = f"""
        SELECT 
            vec.image_id, 
            (1 - vec.distance) AS {target_type}_score
        FROM 
            {vector_table} AS vec
        WHERE 
            vec.image_id IN ({filtered_ids_str})
            AND vec.embedding MATCH '{json.dumps(query_embedding)}'
            AND k = {min(limit*2, len(filtered_ids))}
        """
        subqueries.append(subquery)
    
    # 第一个子查询作为基础
    base_query = subqueries[0]
    base_type = search_targets[0]
    
    # 构建完整的连接查询
    sql = f"""
    WITH base AS ({base_query})
    """
    
    # 添加其他子查询作为CTE (Common Table Expressions)
    for i, (target_type, subquery) in enumerate(zip(search_targets[1:], subqueries[1:]), 1):
        sql += f"""
        , q{i} AS ({subquery})
        """
    
    # 开始SELECT语句，结合所有查询结果
    sql += f"""
    SELECT 
        base.image_id,
    """
    
    # 添加各个得分列
    score_columns = [f"base.{base_type}_score"]
    for i, target_type in enumerate(search_targets[1:], 1):
        score_columns.append(f"q{i}.{target_type}_score")
    
    sql += ",\n        ".join(score_columns) + ","
    
    # 计算总得分和平均得分
    coalesce_parts = []
    for i, target_type in enumerate(search_targets):
        if i == 0:
            coalesce_parts.append(f"COALESCE(base.{target_type}_score, 0)")
        else:
            coalesce_parts.append(f"COALESCE(q{i}.{target_type}_score, 0)")
    
    # 总得分计算
    sql += f"""
        ({" + ".join(coalesce_parts)}) AS total_score,
        ({" + ".join(coalesce_parts)}) / {len(search_targets)} AS avg_score
    FROM 
        base
    """
    
    # 添加LEFT JOIN连接其他子查询
    for i, target_type in enumerate(search_targets[1:], 1):
        sql += f"""
    LEFT JOIN q{i} ON base.image_id = q{i}.image_id
    """
    
    # 添加排序和分页
    sql += f"""
    ORDER BY avg_score DESC
    LIMIT {limit} OFFSET {offset}    """
    
    # 执行SQL查询
    cursor = conn.cursor()
    cursor.execute(sql)
    
    # 保存结果
    scored_results = []
    for row in cursor.fetchall():
        image_id = row["image_id"]
        avg_score = row["avg_score"]
        scored_results.append((image_id, avg_score))
    
    # 按得分降序排序
    scored_results.sort(key=lambda x: x[1], reverse=True)
    
    # 应用分页
    paged_image_ids = [item[0] for item in scored_results[offset:offset+limit]]
    
    if not paged_image_ids:
        return []
    
    # 4. 获取完整的图像信息
    cursor = conn.cursor()
    
    placeholders = ','.join(['?'] * len(paged_image_ids))
    cursor.execute(f"""
    SELECT * FROM images WHERE id IN ({placeholders})
    """, paged_image_ids)
      # 获取所有结果
    raw_results = cursor.fetchall()
    
    # 将查询结果转换为字典列表
    results = rows_to_dicts(raw_results)
    
    # 使用查询结果中的得分对结果进行排序
    # 创建 ID 到得分的映射
    id_to_score = {id: score for id, score in scored_results}
    
    # 处理特殊字段并添加得分
    for result in results:
        # 添加得分
        result['score'] = id_to_score.get(result['id'], 0)
        
        # 处理 JSON 字段（tags 和 metadata）
        result = json_from_db_to_python(result)
    
    # 根据得分排序
    results.sort(key=lambda x: x['score'], reverse=True)
    
    return results

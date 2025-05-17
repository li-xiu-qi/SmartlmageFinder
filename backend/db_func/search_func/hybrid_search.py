"""
混合搜索功能模块，提供结合向量检索和文本匹配的混合检索。
"""
import sqlite3
import json
from typing import List, Dict, Any, Optional, Union, Tuple

from ..core import dict_factory
from .basic_search import get_filtered_image_ids
from ...utils.generate_vector import encode_text, encode_image


def hybrid_search(
    conn: sqlite3.Connection,
    query: Union[str, int, Tuple[str, str]],
    query_type: str = "text",
    search_targets: List[str] = ["title", "description", "image"],
    filters: Optional[Dict[str, Any]] = None,
    limit: int = 20,
    offset: int = 0,
    exclude_self: bool = False
) -> List[Dict[str, Any]]:
    """
    执行混合搜索，结合向量相似度和文本匹配。
    
    Args:
        conn: 数据库连接对象
        query: 查询内容，可以是文本字符串、图像路径或图像ID。若为元组，则第一个元素是查询内容，第二个元素是查询类型。
        query_type: 查询类型，可选值："text"（默认）、"image"或"image_id"。
        search_targets: 要搜索的目标类型列表，可以包含："title", "description", "image"。默认搜索所有类型。
        filters: 过滤条件字典。
        limit: 返回结果的最大数量。
        offset: 结果的起始偏移量，用于分页。
        exclude_self: 是否从结果中排除查询图像本身，仅在query_type为"image_id"时有效。
        
    Returns:
        图像信息字典的列表，按综合得分排序。
    """
    filters = filters or {}

    # 检查查询内容是否为元组
    if isinstance(query, tuple):
        query_content, query_type = query
    else:
        query_content = query

    # 检查参数有效性
    if query_type not in ["text", "image", "image_id"]:
        raise ValueError("查询类型必须是 'text', 'image' 或 'image_id'")
    
    if not search_targets or not all(t in ["title", "description", "image"] for t in search_targets):
        raise ValueError("search_targets 必须包含有效的目标类型：'title', 'description', 'image'")
    
    # 记录查询图像ID，用于排除自身
    query_image_id = None
    if query_type == "image_id" and exclude_self:
        query_image_id = int(query_content)

    # 生成查询内容的向量表示
    if query_type == "text":
        query_embedding = encode_text(query_content).tolist()
    elif query_type == "image":
        query_embedding = encode_image(query_content).tolist()
    elif query_type == "image_id":
        # 从数据库中获取指定ID的图像向量
        cursor = conn.cursor()
        
        # 首先确认图像是否存在
        cursor.execute("SELECT id FROM images WHERE id = ?", (query_content,))
        if not cursor.fetchone():
            raise ValueError(f"未找到ID为 {query_content} 的图像")
        
        # 使用第一个搜索目标类型的向量作为查询向量
        if search_targets:
            target_type = search_targets[0]
            vector_table = f"{target_type}_vectors"
            
            cursor.execute(f"SELECT embedding FROM {vector_table} WHERE image_id = ?", (query_content,))
            vector_row = cursor.fetchone()
            
            if vector_row:
                query_embedding = json.loads(vector_row[0])
            else:
                raise ValueError(f"未找到ID为 {query_content} 的图像的 {target_type} 向量")
    
    # 1. 首先根据过滤条件获取符合条件的图像ID
    filtered_ids = get_filtered_image_ids(conn, filters)
    # 如果需要排除自身，从过滤结果中移除查询图像ID
    if query_image_id is not None and query_image_id in filtered_ids:
        filtered_ids.remove(query_image_id)
        
    if not filtered_ids:
        return []
    
    # 2. 对每个目标类型进行向量搜索
    results_by_type = {}
    for target_type in search_targets:
        # 构建查询
        vector_table = f"{target_type}_vectors"
        filtered_ids_str = ','.join(str(id) for id in filtered_ids)
        sql = f"""
        SELECT 
            vec.image_id, 
            vec.distance,
            (1 - vec.distance) AS score
        FROM 
            {vector_table} AS vec
        WHERE 
            vec.image_id IN ({filtered_ids_str})
            AND vec.embedding MATCH ?
            AND k = ?
        """
        
        # 执行向量搜索
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(sql, (json.dumps(query_embedding), min(limit*2, len(filtered_ids))))
          # 保存结果
        for row in cursor.fetchall():
            image_id = row["image_id"]
            distance = row["distance"]
            score = row["score"]
            
            if image_id not in results_by_type:
                results_by_type[image_id] = {}
            
            results_by_type[image_id][target_type] = {"distance": distance, "score": score}
      # 3. 计算综合得分
    scored_results = []
    for image_id, target_data in results_by_type.items():
        total_score = 0
        for target_type in search_targets:
            if target_type in target_data:
                # 直接使用SQL计算的score
                score = target_data[target_type]["score"]
                total_score += score
        
        # 平均得分
        avg_score = total_score / len(search_targets)
        scored_results.append((image_id, avg_score))
    
    # 按得分降序排序
    scored_results.sort(key=lambda x: x[1], reverse=True)
    
    # 应用分页
    paged_image_ids = [item[0] for item in scored_results[offset:offset+limit]]
    
    if not paged_image_ids:
        return []
    
    # 4. 获取完整的图像信息
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    placeholders = ','.join(['?'] * len(paged_image_ids))
    cursor.execute(f"""
    SELECT * FROM images WHERE id IN ({placeholders})
    """, paged_image_ids)
    
    # 获取所有结果
    results = cursor.fetchall()
    
    # 使用查询结果中的得分对结果进行排序
    # 创建 ID 到得分的映射
    id_to_score = {id: score for id, score in scored_results}
    
    # 处理特殊字段并添加得分
    for result in results:
        # 添加得分
        result['score'] = id_to_score.get(result['id'], 0)
        
        # 处理 JSON 字段
        if result.get('tags') and isinstance(result['tags'], str):
            try:
                result['tags'] = json.loads(result['tags'])
            except:
                result['tags'] = []
        
        if result.get('metadata') and isinstance(result['metadata'], str):
            try:
                result['metadata'] = json.loads(result['metadata'])
            except:
                result['metadata'] = {}
    
    # 根据得分排序
    results.sort(key=lambda x: x['score'], reverse=True)
    
    return results


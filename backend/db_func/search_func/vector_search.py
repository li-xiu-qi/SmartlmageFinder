import sqlite3
import json
from typing import List, Dict, Any, Literal

from ..utils import row_to_dict
from .basic_search import get_filtered_image_ids

def find_similar_images(
    conn: sqlite3.Connection,
    query_embedding: List[float], 
    vector_type: Literal["title", "description", "image"], 
    k: int = 5, 
    filters: Dict[str, Any] = None
) -> List[Dict[str, Any]]:
    """
    根据查询嵌入向量执行 K-最近邻 (KNN) 搜索以查找相似图像，支持过滤条件。

    Args:
        conn: 数据库连接对象
        query_embedding: 查询的嵌入向量。
        vector_type: 要搜索的向量类型。
                     有效选项："title", "description", "image"。
        k: 要检索的最近邻居的数量。
        filters: 过滤条件字典，可以包含以下键：
            - filename: 按文件名模糊匹配
            - title: 按标题模糊匹配
            - description: 按描述模糊匹配
            - tags: 按标签过滤
            - start_date: 按创建时间过滤（起始时间）
            - end_date: 按创建时间过滤（结束时间）

    Returns:
        一个字典列表，其中每个字典包含有关相似图像及其与查询嵌入的距离的信息。
        示例: [{'id': 1, 'filename': '...', 'filepath': '...', 'distance': 0.123}, ...]
        如果发生错误或未找到结果，则返回空列表。
    """  
    if not isinstance(query_embedding, list) or not all(isinstance(x, (float, int)) for x in query_embedding):
        raise ValueError("query_embedding 必须是浮点数或整数列表。")
    if vector_type not in ["title", "description", "image"]:
        raise ValueError("无效的 vector_type。必须是 'title', 'description', 或 'image'。")
    if not isinstance(k, int) or k <= 0:
        raise ValueError("k 必须是正整数。")
    

    vector_table_map = {
        "title": "title_vectors",
        "description": "description_vectors",
        "image": "image_vectors"
    }
    target_vector_table = vector_table_map[vector_type]
    filters = filters or {}   
    results = []    
    try:
        # 设置row_factory以便能够通过row_to_dict处理结果
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        query_embedding_json = json.dumps(query_embedding)

        # 1. 首先根据过滤条件查询符合的图像ID
        filtered_ids = get_filtered_image_ids(conn, filters)

        # 如果没有符合条件的结果，直接返回空列表
        if not filtered_ids:
            return []

        # 2. 使用过滤后的ID进行向量相似度搜索
        filtered_ids_str = ','.join(str(id) for id in filtered_ids)
        
        # 3. 构建向量相似度搜索查询
        sql_query = f"""
        SELECT
            img.id,
            img.filename,
            img.filepath,
            img.title,
            img.description,
            img.file_size,
            img.file_type,
            img.width,
            img.created_at,
            img.updated_at,
            img.metadata,
            img.tags,
            vec.distance,
            (1 - vec.distance) AS score
        FROM
            {target_vector_table} AS vec
        JOIN
            images AS img ON vec.image_id = img.id
        WHERE
            vec.image_id IN ({filtered_ids_str})
            AND vec.embedding MATCH ? AND k = ?;
        """
        
        # 调整k的值，确保不大于过滤后的结果数量
        actual_k = min(k, len(filtered_ids))
        
        cursor.execute(sql_query, (query_embedding_json, actual_k))
        
        # 使用我们的辅助函数将 sqlite3.Row 结果转换为字典
        raw_results = cursor.fetchall()
        results = [row_to_dict(r) for r in raw_results]

    except sqlite3.Error as e:
        print(f"数据库相似度搜索错误: {e}")
    except ValueError as e:
        raise e
    except Exception as e:
        print(f"相似度搜索期间发生意外错误: {e}")
    
    print("相似度搜索完成")
    return results

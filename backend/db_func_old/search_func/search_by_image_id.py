"""
优化的向量搜索函数，使用单个SQL查询完成向量获取和搜索
"""
import sqlite3
from typing import List, Dict, Any, Optional
import json
import traceback

from backend.db_func.search_func.basic_search import get_filtered_image_ids

from ..utils import json_from_db_to_python, row_to_dict

# 导入图像工具函数来处理JSON字段

def search_by_image_id(
    conn: sqlite3.Connection,
    image_id: int,
    vector_type: str = "image",
    k: int = 5,
    filters: Optional[Dict[str, Any]] = None,
    exclude_self: bool = True
) -> List[Dict[str, Any]]:
    """
    使用单个SQL查询完成向量获取和搜索，查找与指定图像ID相似的图像
    
    Args:
        conn: 数据库连接对象
        image_id: 要搜索的图像ID
        vector_type: 要使用的向量类型，可选值: "title", "description", "image"
        k: 返回的相似结果数量
        filters: 过滤条件字典，可以包含以下键：
            - filename: 按文件名模糊匹配
            - title: 按标题模糊匹配
            - description: 按描述模糊匹配
            - tags: 按标签过滤 (列表，对JSON数组成员进行OR逻辑匹配)
            - start_date: 按创建时间过滤（起始时间 YYYY-MM-DD HH:MM:SS）
            - end_date: 按创建时间过滤（结束时间 YYYY-MM-DD HH:MM:SS）
        exclude_self: 是否从结果中排除查询图像本身
        
    Returns:
        相似图像列表，按相似度排序
    """
    print(f"开始使用图像ID {image_id} 进行向量搜索")
    print("向量类型：",vector_type)
    cursor = conn.cursor()
    results = []
    try:
        # 保存原始的row_factory
        original_row_factory = conn.row_factory
        
        # 设置row_factory为sqlite3.Row以便能够使用row_to_dict函数
        conn.row_factory = sqlite3.Row
        
        # 首先验证查询的图像ID是否存在
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM images WHERE id = ?", (image_id,))
        image_exists = cursor.fetchone()
        if not image_exists:
            print(f"图像ID {image_id} 不存在于数据库中")
            return []
            
        # 处理过滤条件
        # 在调用get_filtered_image_ids前确保使用原始的row_factory
        conn.row_factory = original_row_factory
          # 使用 basic_search 中的函数获取过滤后的图像ID
        filtered_ids = get_filtered_image_ids(conn, filters or {})
        
        # 重新设置row_factory为sqlite3.Row
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 如果需要排除自己，从过滤ID中移除
        if exclude_self and image_id in filtered_ids:
            filtered_ids.remove(image_id)
            
        # 如果没有符合条件的结果，直接返回空列表
        if not filtered_ids:
            print("过滤后没有符合条件的图像ID")
            # 完成后恢复原始的row_factory
            conn.row_factory = original_row_factory
            return []
            
        # 构建过滤ID字符串
        filtered_ids_str = ','.join(str(id) for id in filtered_ids)
        
        # 确定向量表名
        vector_table = f"{vector_type}_vectors"
        
        # 验证向量表中是否存在该图像ID的向量
        cursor.execute(f"SELECT COUNT(*) FROM {vector_table} WHERE image_id = ?", (image_id,))
        vector_count = cursor.fetchone()["COUNT(*)"]
        if vector_count == 0:
            print(f"图像ID {image_id} 在 {vector_table} 表中不存在向量")
            # 完成后恢复原始的row_factory
            conn.row_factory = original_row_factory
            return []
        
        # 构建单一SQL查询，先获取指定ID的向量，然后使用该向量进行搜索
        # 使用WITH子句创建临时表保存查询向量
        try:            
            sql_query = f"""
            WITH query_vector AS (
                SELECT embedding 
                FROM {vector_table}
                WHERE image_id = ?
            )
            SELECT 
                img.id,
                img.filename, 
                img.filepath,
                img.title,
                img.description,
                img.file_size,
                img.file_type,
                img.width,
                img.height,
                img.created_at,
                img.updated_at,
                img.metadata,
                img.tags,
                res.distance,
                (1 - res.distance) AS score
            FROM (
                SELECT 
                    image_id,
                    distance
                FROM 
                    {vector_table}
                WHERE 
                    image_id IN ({filtered_ids_str})
                    AND embedding MATCH (SELECT embedding FROM query_vector)
                    AND k = ?
            ) AS res
            JOIN 
                images AS img ON res.image_id = img.id
            ORDER BY 
                res.distance ASC
            """
            
            # 执行查询
            cursor.execute(sql_query, (image_id, k))
              # 获取结果
            raw_results = cursor.fetchall()
            
            # 处理结果
            for row in raw_results:
                # 使用row_to_dict转换Row对象为字典
                result = row_to_dict(row)
                
                # 使用统一的JSON处理函数来处理tags和metadata字段
                result = json_from_db_to_python(result)
                
                results.append(result)
                
            print(f"使用图像ID进行向量搜索成功: {len(results)} 条结果")
        except sqlite3.Error as e:
            print(f"执行向量搜索SQL查询错误: {e}")
            traceback.print_exc()
        finally:
            # 无论成功还是失败，都恢复原始的row_factory
            conn.row_factory = original_row_factory
            
    except Exception as e:
        print(f"使用图像ID进行向量搜索失败: {e}")
        traceback.print_exc()
        # 出现异常时也确保恢复原始的row_factory
        if 'original_row_factory' in locals():
            conn.row_factory = original_row_factory
        
    return results

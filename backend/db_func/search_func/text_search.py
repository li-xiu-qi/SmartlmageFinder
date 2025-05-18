"""
文本搜索功能模块，提供基于文本的图像检索。
"""
import sqlite3
import json
from typing import List, Dict, Any, Optional, Literal

from ..utils import row_to_dict, rows_to_dicts
from .basic_search import get_filtered_image_ids

def search_by_text(
    conn: sqlite3.Connection,
    text: str,
    search_type: Literal["title", "description", "both"] = "both",
    filters: Optional[Dict[str, Any]] = None,
    limit: int = 100,
    offset: int = 0
) -> List[Dict[str, Any]]:
    """
    基于文本在标题和/或描述中搜索图像。
    
    Args:
        conn: 数据库连接对象
        text: 要搜索的文本。
        search_type: 搜索范围，可选值：
            - "title": 只搜索标题
            - "description": 只搜索描述
            - "both": 同时搜索标题和描述（默认）
        filters: 过滤条件字典，可以包含以下键：
            - filename: 按文件名模糊匹配
            - tags: 按标签过滤 (列表，对JSON数组成员进行OR逻辑匹配)
            - start_date: 按创建时间过滤（起始时间 YYYY-MM-DD HH:MM:SS）
            - end_date: 按创建时间过滤（结束时间 YYYY-MM-DD HH:MM:SS）
        limit: 返回结果的最大数量。
        offset: 结果的起始偏移量，用于分页。
        
    Returns:
        图像信息字典的列表，每个字典包含图像的所有字段。
        如果未找到结果或发生错误，则返回空列表。
    """          
    filters = filters or {}
    results = []    
    if not text.strip():
        return results  # 如果搜索文本为空，直接返回空结果
    
    # 设置row_factory以便正确处理查询结果
    conn.row_factory = sqlite3.Row
    
    try:
        cursor = conn.cursor()
        
        # 构建查询条件
        search_conditions = []
        search_params = []
        
        if search_type in ["title", "both"]:
            search_conditions.append("title LIKE ?")
            search_params.append(f"%{text}%")
            
        if search_type in ["description", "both"]:
            search_conditions.append("description LIKE ?")
            search_params.append(f"%{text}%")
            
        if not search_conditions:
            return []  # 如果搜索类型无效，返回空结果
        
        # 获取符合过滤条件的ID
        query = ""
        params = []
        
        if filters:
            filtered_ids = get_filtered_image_ids(conn, filters)
            if not filtered_ids:
                return []  # 如果没有符合过滤条件的ID，直接返回空结果
            
            # 构建查询SQL
            query = f"""
            SELECT * FROM images 
            WHERE ({" OR ".join(search_conditions)})
            AND id IN ({','.join(['?'] * len(filtered_ids))})
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
            """
            
            # 构建查询参数
            params = search_params + filtered_ids + [limit, offset]
            
        else:
            # 没有过滤条件，直接进行文本搜索
            query = f"""
            SELECT * FROM images 
            WHERE {" OR ".join(search_conditions)}
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
            """
            params = search_params + [limit, offset]
          # 执行查询
        cursor.execute(query, params)
        raw_results = cursor.fetchall()
          # 使用rows_to_dicts函数将结果转换为字典列表
        results = rows_to_dicts(raw_results)
        
        # 处理JSON字段
        from ..utils import json_from_db_to_python
        results = [json_from_db_to_python(result) for result in results]
    
    except sqlite3.Error as e:
        print(f"数据库文本搜索错误: {e}")
    except Exception as e:
        print(f"文本搜索期间发生意外错误: {e}")
        
    return results
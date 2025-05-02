import sqlite3
import json
from typing import Dict, List, Any, Optional, Tuple
import uuid as uuid_lib
from datetime import datetime
import os

# 导入向量数据库模块
from .vector_db import (
    add_text_vector, add_image_vector, delete_vectors, save_indices,
    search_by_text as vector_search_by_text,
    search_by_image as vector_search_by_image,
    search_by_uuid as vector_search_by_uuid
)

from .config import settings

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(settings.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """初始化数据库表结构"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 创建图片表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS images (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        uuid TEXT UNIQUE NOT NULL,
        filename TEXT NOT NULL,
        filepath TEXT NOT NULL,
        title TEXT,
        description TEXT,
        file_size INTEGER NOT NULL,
        file_type TEXT NOT NULL,
        width INTEGER,
        height INTEGER,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        hash_value TEXT,
        metadata TEXT,
        tags TEXT
    )
    ''')
    
    # 创建索引
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_images_uuid ON images(uuid)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_images_created_at ON images(created_at)')
    
    conn.commit()
    conn.close()
    
    print("数据库初始化完成")

def dict_factory(cursor, row):
    """将sqlite3.Row转换为dict"""
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def get_image_by_uuid(uuid: str) -> Optional[Dict[str, Any]]:
    """通过UUID获取图片信息"""
    conn = get_db_connection()
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM images WHERE uuid = ?", (uuid,))
    image = cursor.fetchone()
    
    # 处理JSON字段
    if image:
        if image['tags']:
            try:
                image['tags'] = json.loads(image['tags'])
            except:
                image['tags'] = []
        else:
            image['tags'] = []
            
        if image['metadata']:
            try:
                image['metadata'] = json.loads(image['metadata'])
            except:
                image['metadata'] = {}
        else:
            image['metadata'] = {}
    
    conn.close()
    return image

def get_images(page: int = 1, 
               page_size: int = 20, 
               sort_by: str = "created_at",
               order: str = "desc",
               start_date: Optional[str] = None,
               end_date: Optional[str] = None,
               tags: Optional[List[str]] = None) -> Tuple[List[Dict[str, Any]], int]:
    """获取图片列表，支持分页和过滤"""
    conn = get_db_connection()
    conn.row_factory = dict_factory
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
    
    if tags and len(tags) > 0:
        tag_conditions = []
        for tag in tags:
            tag_conditions.append("tags LIKE ?")
            params.append(f'%"{tag}"%')
        conditions.append("(" + " OR ".join(tag_conditions) + ")")
    
    # 组合查询条件
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
        count_query += " WHERE " + " AND ".join(conditions)
    
    # 添加排序和分页
    query += f" ORDER BY {sort_by} {order}"
    query += f" LIMIT {page_size} OFFSET {(page - 1) * page_size}"
    
    # 执行查询
    cursor.execute(query, params)
    images = cursor.fetchall()
    
    # 执行计数查询
    cursor.execute(count_query, params)
    total_count = cursor.fetchone()['count']
    
    # 处理JSON字段
    for image in images:
        if image['tags']:
            try:
                image['tags'] = json.loads(image['tags'])
            except:
                image['tags'] = []
        else:
            image['tags'] = []
    
    conn.close()
    return images, total_count

def create_image(image_data: Dict[str, Any]) -> Dict[str, Any]:
    """创建新图片记录"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 生成UUID
    image_uuid = str(uuid_lib.uuid4())
    now = datetime.now().isoformat()
    
    # 准备JSON字段
    if 'tags' in image_data and image_data['tags']:
        tags_json = json.dumps(image_data['tags'], ensure_ascii=False)
    else:
        tags_json = json.dumps([], ensure_ascii=False)
    
    if 'metadata' in image_data and image_data['metadata']:
        metadata_json = json.dumps(image_data['metadata'], ensure_ascii=False)
    else:
        metadata_json = json.dumps({}, ensure_ascii=False)
    
    cursor.execute("""
    INSERT INTO images (uuid, filename, filepath, title, description, file_size, file_type,
                       width, height, created_at, updated_at, hash_value, metadata, tags)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        image_uuid, 
        image_data['filename'],
        image_data['filepath'],
        image_data.get('title'),
        image_data.get('description'),
        image_data['file_size'],
        image_data['file_type'],
        image_data.get('width'),
        image_data.get('height'),
        now,
        now,
        image_data.get('hash_value'),
        metadata_json,
        tags_json
    ))
    
    conn.commit()
    conn.close()
    
    # 创建成功后，添加向量到索引
    try:
        # 添加文本向量 (如果有标题或描述)
        text_content = ""
        if image_data.get('title'):
            text_content += image_data['title'] + " "
        if image_data.get('description'):
            text_content += image_data['description']
            
        if text_content.strip():
            add_text_vector(image_uuid, text_content)
            
        # 添加图像向量
        if os.path.exists(image_data['filepath']):
            add_image_vector(image_uuid, image_data['filepath'])
            
        # 定期保存索引 (这里简化处理，实际应用中可能需要更复杂的策略)
        save_indices()
    except Exception as e:
        print(f"向量索引更新失败: {e}")
    
    # 返回创建的图片信息
    return get_image_by_uuid(image_uuid)

def update_image(uuid: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """更新图片信息"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 检查图片是否存在
    existing_image = get_image_by_uuid(uuid)
    if not existing_image:
        conn.close()
        return None
    
    # 准备要更新的字段
    update_fields = []
    params = []
    
    for field in ['title', 'description']:
        if field in update_data and update_data[field] is not None:
            update_fields.append(f"{field} = ?")
            params.append(update_data[field])
    
    # 处理标签
    if 'tags' in update_data and update_data['tags'] is not None:
        update_fields.append("tags = ?")
        params.append(json.dumps(update_data['tags'], ensure_ascii=False))
    
    # 处理元数据
    if 'metadata' in update_data and update_data['metadata'] is not None:
        update_fields.append("metadata = ?")
        params.append(json.dumps(update_data['metadata'], ensure_ascii=False))
    
    # 更新时间戳
    update_fields.append("updated_at = ?")
    params.append(datetime.now().isoformat())
    
    # 添加UUID参数
    params.append(uuid)
    
    # 执行更新
    if update_fields:
        query = f"UPDATE images SET {', '.join(update_fields)} WHERE uuid = ?"
        cursor.execute(query, params)
        conn.commit()
    
    conn.close()
    
    # 如果标题或描述有更新，需要更新文本向量
    try:
        if 'title' in update_data or 'description' in update_data:
            updated_image = get_image_by_uuid(uuid)
            text_content = ""
            if updated_image.get('title'):
                text_content += updated_image['title'] + " "
            if updated_image.get('description'):
                text_content += updated_image['description']
                
            if text_content.strip():
                # 先删除旧向量（实际是标记为已删除）
                delete_vectors(uuid)
                # 添加新的文本向量
                add_text_vector(uuid, text_content)
                # 保存索引
                save_indices()
    except Exception as e:
        print(f"更新文本向量失败: {e}")
    
    # 返回更新后的图片
    return get_image_by_uuid(uuid)

def delete_image(uuid: str) -> bool:
    """删除图片"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 检查图片是否存在
    cursor.execute("SELECT id FROM images WHERE uuid = ?", (uuid,))
    if not cursor.fetchone():
        conn.close()
        return False
    
    # 执行删除
    cursor.execute("DELETE FROM images WHERE uuid = ?", (uuid,))
    conn.commit()
    conn.close()
    
    # 从向量索引中删除
    try:
        delete_vectors(uuid)
        save_indices()
    except Exception as e:
        print(f"删除向量索引失败: {e}")
    
    return True

def get_popular_tags(limit: int = 50) -> List[Dict[str, Any]]:
    """获取热门标签列表"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 使用SQL聚合查询获取标签
    cursor.execute("""
    WITH RECURSIVE split_tags(tag, rest) AS (
        SELECT '', tags || ',' FROM images WHERE tags IS NOT NULL
        UNION ALL
        SELECT 
            substr(rest, 0, instr(rest, ',')),
            substr(rest, instr(rest, ',')+1)
        FROM split_tags WHERE rest != ''
    )
    SELECT tag, COUNT(*) as count
    FROM split_tags
    WHERE tag != ''
    GROUP BY tag
    ORDER BY count DESC
    LIMIT ?
    """, (limit,))
    
    tags = []
    for row in cursor.fetchall():
        # 清理标签名（去除JSON格式中的引号）
        tag_name = row[0].strip('"')
        if tag_name:
            tags.append({
                "name": tag_name,
                "count": row[1]
            })
    
    conn.close()
    return tags

def add_tags_to_image(uuid: str, new_tags: List[str]) -> Optional[Dict[str, Any]]:
    """向图片添加标签"""
    # 获取图片
    image = get_image_by_uuid(uuid)
    if not image:
        return None
    
    # 添加新标签
    current_tags = image['tags']
    for tag in new_tags:
        if tag not in current_tags:
            current_tags.append(tag)
    
    # 更新图片
    return update_image(uuid, {'tags': current_tags})

def remove_tag_from_image(uuid: str, tag: str) -> Optional[Dict[str, Any]]:
    """从图片中移除标签"""
    # 获取图片
    image = get_image_by_uuid(uuid)
    if not image:
        return None
    
    # 移除标签
    current_tags = image['tags']
    if tag in current_tags:
        current_tags.remove(tag)
        # 更新图片
        return update_image(uuid, {'tags': current_tags})
    
    return image

def get_metadata_fields(limit: int = 50) -> List[Dict[str, Any]]:
    """获取所有元数据字段及其使用频率"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 使用SQL分析元数据字段
    cursor.execute("""
    SELECT json_extract(metadata, '$') as all_meta FROM images WHERE metadata IS NOT NULL
    """)
    
    # 分析元数据字段和类型
    field_stats = {}
    for row in cursor.fetchall():
        if row[0]:
            try:
                metadata = json.loads(row[0])
                for key, value in metadata.items():
                    if key not in field_stats:
                        field_stats[key] = {
                            'count': 0,
                            'types': {}
                        }
                    field_stats[key]['count'] += 1
                    
                    # 统计类型
                    value_type = type(value).__name__
                    if value_type not in field_stats[key]['types']:
                        field_stats[key]['types'][value_type] = 0
                    field_stats[key]['types'][value_type] += 1
            except:
                pass
    
    # 格式化输出
    fields = []
    for name, stats in field_stats.items():
        # 确定主要类型
        primary_type = max(stats['types'].items(), key=lambda x: x[1])[0]
        fields.append({
            "name": name,
            "count": stats['count'],
            "type": primary_type
        })
    
    # 按使用频率排序
    fields.sort(key=lambda x: x['count'], reverse=True)
    
    conn.close()
    return fields[:limit]

def update_image_metadata(uuid: str, metadata: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """更新图片元数据"""
    # 获取图片
    image = get_image_by_uuid(uuid)
    if not image:
        return None
    
    # 更新元数据
    current_metadata = image['metadata']
    for key, value in metadata.items():
        current_metadata[key] = value
    
    # 更新图片
    return update_image(uuid, {'metadata': current_metadata})

def search_by_text(query: str, 
                  mode: str = "text",
                  limit: int = 20,
                  start_date: Optional[str] = None,
                  end_date: Optional[str] = None,
                  tags: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """文本搜索，支持普通文本、向量和混合模式"""
    # 根据模式选择搜索方式
    if mode == "vector":
        return vector_text_search(query, limit, start_date, end_date, tags)
    elif mode == "hybrid":
        return hybrid_text_search(query, limit, start_date, end_date, tags)
    else:
        return simple_text_search(query, limit, start_date, end_date, tags)

def simple_text_search(query: str, 
                      limit: int = 20,
                      start_date: Optional[str] = None,
                      end_date: Optional[str] = None,
                      tags: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """基本文本搜索（不使用向量）"""
    conn = get_db_connection()
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    search_term = f"%{query}%"
    conditions = [
        "title LIKE ? OR description LIKE ? OR tags LIKE ?"
    ]
    params = [search_term, search_term, search_term]
    
    # 添加时间过滤
    if start_date:
        conditions.append("created_at >= ?")
        params.append(start_date)
    
    if end_date:
        conditions.append("created_at <= ?")
        params.append(end_date)
    
    # 添加标签过滤
    if tags and len(tags) > 0:
        tag_conditions = []
        for tag in tags:
            tag_conditions.append("tags LIKE ?")
            params.append(f'%"{tag}"%')
        conditions.append("(" + " OR ".join(tag_conditions) + ")")
    
    query_sql = f"""
    SELECT *,
           (CASE 
             WHEN title LIKE ? THEN 3
             WHEN description LIKE ? THEN 2
             WHEN tags LIKE ? THEN 1
             ELSE 0
           END) as relevance
    FROM images
    WHERE {" AND ".join(conditions)}
    ORDER BY relevance DESC
    LIMIT ?
    """
    
    # 添加相关性计算参数
    params.extend([search_term, search_term, search_term, limit])
    
    cursor.execute(query_sql, params)
    results = cursor.fetchall()
    
    # 处理JSON字段并计算分数
    for result in results:
        if result['tags']:
            try:
                result['tags'] = json.loads(result['tags'])
            except:
                result['tags'] = []
        else:
            result['tags'] = []
        
        # 计算标准化分数
        result['score'] = min(result['relevance'] / 3.0, 1.0)
    
    conn.close()
    return results

def vector_text_search(query: str, 
                      limit: int = 20,
                      start_date: Optional[str] = None,
                      end_date: Optional[str] = None,
                      tags: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """基于向量的文本搜索"""
    # 使用FAISS进行向量搜索
    vector_results = vector_search_by_text(query, limit * 2)  # 获取2倍数量的结果以便应用过滤
    
    if not vector_results:
        return []  # 如果没有向量搜索结果，直接返回空列表
    
    # 提取结果中的UUID
    uuids = [result['uuid'] for result in vector_results]
    uuid_to_score = {result['uuid']: result['score'] for result in vector_results}
    
    # 从数据库查询详细信息并应用过滤
    conn = get_db_connection()
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    placeholders = ", ".join(["?"] * len(uuids))
    conditions = [f"uuid IN ({placeholders})"]
    params = uuids.copy()
    
    # 添加时间过滤
    if start_date:
        conditions.append("created_at >= ?")
        params.append(start_date)
    
    if end_date:
        conditions.append("created_at <= ?")
        params.append(end_date)
    
    # 添加标签过滤
    if tags and len(tags) > 0:
        tag_conditions = []
        for tag in tags:
            tag_conditions.append("tags LIKE ?")
            params.append(f'%"{tag}"%')
        conditions.append("(" + " OR ".join(tag_conditions) + ")")
    
    query_sql = f"SELECT * FROM images WHERE {' AND '.join(conditions)}"
    
    cursor.execute(query_sql, params)
    images = cursor.fetchall()
    
    # 处理JSON字段，添加分数，并保持向量搜索排序
    results = []
    for image in images:
        if image['tags']:
            try:
                image['tags'] = json.loads(image['tags'])
            except:
                image['tags'] = []
        else:
            image['tags'] = []
        
        # 添加向量相似度分数
        image['score'] = uuid_to_score.get(image['uuid'], 0.0)
        results.append(image)
    
    # 按相似度分数排序
    results.sort(key=lambda x: x['score'], reverse=True)
    
    # 限制结果数量
    results = results[:limit]
    
    conn.close()
    return results

def hybrid_text_search(query: str, 
                       limit: int = 20,
                       start_date: Optional[str] = None,
                       end_date: Optional[str] = None,
                       tags: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """混合文本和向量的搜索"""
    # 获取文本搜索结果
    text_results = simple_text_search(query, limit * 2, start_date, end_date, tags)
    text_uuids = set(result['uuid'] for result in text_results)
    
    # 获取向量搜索结果
    vector_results = vector_text_search(query, limit * 2, start_date, end_date, tags)
    vector_uuids = set(result['uuid'] for result in vector_results)
    
    # 创建UUID到分数的映射
    uuid_to_score = {}
    for result in text_results:
        uuid_to_score[result['uuid']] = {'text': result['score'], 'vector': 0.0}
    
    for result in vector_results:
        if result['uuid'] in uuid_to_score:
            uuid_to_score[result['uuid']]['vector'] = result['score']
        else:
            uuid_to_score[result['uuid']] = {'text': 0.0, 'vector': result['score']}
    
    # 合并两组结果
    all_uuids = list(text_uuids.union(vector_uuids))
    
    if not all_uuids:
        return []  # 如果没有结果，直接返回空列表
    
    # 从数据库查询详细信息
    conn = get_db_connection()
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    placeholders = ", ".join(["?"] * len(all_uuids))
    query_sql = f"SELECT * FROM images WHERE uuid IN ({placeholders})"
    
    cursor.execute(query_sql, all_uuids)
    images = cursor.fetchall()
    
    # 处理JSON字段，计算混合分数
    results = []
    for image in images:
        if image['uuid'] not in uuid_to_score:
            continue
            
        if image['tags']:
            try:
                image['tags'] = json.loads(image['tags'])
            except:
                image['tags'] = []
        else:
            image['tags'] = []
        
        # 计算混合分数：文本相关性 * 0.4 + 向量相似度 * 0.6
        image['score'] = (
            uuid_to_score[image['uuid']]['text'] * 0.4 +
            uuid_to_score[image['uuid']]['vector'] * 0.6
        )
        results.append(image)
    
    # 按混合分数排序
    results.sort(key=lambda x: x['score'], reverse=True)
    
    # 限制结果数量
    results = results[:limit]
    
    conn.close()
    return results

def search_by_image_path(image_path: str,
                         limit: int = 20,
                         start_date: Optional[str] = None,
                         end_date: Optional[str] = None,
                         tags: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """通过图片路径搜索相似图片"""
    # 使用FAISS进行向量搜索
    vector_results = vector_search_by_image(image_path, limit * 2)  # 获取2倍数量的结果以便应用过滤
    
    if not vector_results:
        return []  # 如果没有向量搜索结果，直接返回空列表
    
    # 提取结果中的UUID
    uuids = [result['uuid'] for result in vector_results]
    uuid_to_score = {result['uuid']: result['score'] for result in vector_results}
    
    # 从数据库查询详细信息并应用过滤
    conn = get_db_connection()
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    placeholders = ", ".join(["?"] * len(uuids))
    conditions = [f"uuid IN ({placeholders})"]
    params = uuids.copy()
    
    # 添加时间过滤
    if start_date:
        conditions.append("created_at >= ?")
        params.append(start_date)
    
    if end_date:
        conditions.append("created_at <= ?")
        params.append(end_date)
    
    # 添加标签过滤
    if tags and len(tags) > 0:
        tag_conditions = []
        for tag in tags:
            tag_conditions.append("tags LIKE ?")
            params.append(f'%"{tag}"%')
        conditions.append("(" + " OR ".join(tag_conditions) + ")")
    
    query_sql = f"SELECT * FROM images WHERE {' AND '.join(conditions)}"
    
    cursor.execute(query_sql, params)
    images = cursor.fetchall()
    
    # 处理JSON字段，添加分数，并保持向量搜索排序
    results = []
    for image in images:
        if image['tags']:
            try:
                image['tags'] = json.loads(image['tags'])
            except:
                image['tags'] = []
        else:
            image['tags'] = []
        
        # 添加向量相似度分数
        image['score'] = uuid_to_score.get(image['uuid'], 0.0)
        results.append(image)
    
    # 按相似度分数排序
    results.sort(key=lambda x: x['score'], reverse=True)
    
    # 限制结果数量
    results = results[:limit]
    
    conn.close()
    return results

def search_similar_to_uuid(uuid: str,
                          limit: int = 20,
                          start_date: Optional[str] = None,
                          end_date: Optional[str] = None,
                          tags: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """通过UUID搜索相似图片"""
    # 使用FAISS进行向量搜索
    vector_results = vector_search_by_uuid(uuid, limit * 2)  # 获取2倍数量的结果以便应用过滤
    
    if not vector_results:
        return []  # 如果没有向量搜索结果，直接返回空列表
    
    # 提取结果中的UUID
    uuids = [result['uuid'] for result in vector_results]
    uuid_to_score = {result['uuid']: result['score'] for result in vector_results}
    
    # 从数据库查询详细信息并应用过滤
    conn = get_db_connection()
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    placeholders = ", ".join(["?"] * len(uuids))
    conditions = [f"uuid IN ({placeholders})"]
    params = uuids.copy()
    
    # 添加时间过滤
    if start_date:
        conditions.append("created_at >= ?")
        params.append(start_date)
    
    if end_date:
        conditions.append("created_at <= ?")
        params.append(end_date)
    
    # 添加标签过滤
    if tags and len(tags) > 0:
        tag_conditions = []
        for tag in tags:
            tag_conditions.append("tags LIKE ?")
            params.append(f'%"{tag}"%')
        conditions.append("(" + " OR ".join(tag_conditions) + ")")
    
    query_sql = f"SELECT * FROM images WHERE {' AND '.join(conditions)}"
    
    cursor.execute(query_sql, params)
    images = cursor.fetchall()
    
    # 处理JSON字段，添加分数，并保持向量搜索排序
    results = []
    for image in images:
        if image['tags']:
            try:
                image['tags'] = json.loads(image['tags'])
            except:
                image['tags'] = []
        else:
            image['tags'] = []
        
        # 添加向量相似度分数
        image['score'] = uuid_to_score.get(image['uuid'], 0.0)
        results.append(image)
    
    # 按相似度分数排序
    results.sort(key=lambda x: x['score'], reverse=True)
    
    # 限制结果数量
    results = results[:limit]
    
    conn.close()
    return results
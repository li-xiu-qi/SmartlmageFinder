"""
文本向量相关操作，包括标题和描述的向量处理
"""
import json
import traceback
import sqlite3

from ...utils.generate_vector import encode_text

def add_text_vector(conn: sqlite3.Connection, image_id: int, text: str, table_name: str, text_type: str):
    """通用的文本向量添加/更新函数
    
    Args:
        conn: 数据库连接
        image_id: 图片ID
        text: 文本内容
        table_name: 向量表名称 
        text_type: 文本类型描述(用于日志)
    """
    if not text or not text.strip():
        return None
    
    try:        
        # 生成向量
        vector = encode_text(text)
        vector_json = json.dumps(vector.tolist())
        
        # 连接池已自动加载向量扩展，不再需要单独加载
        
        cursor = conn.cursor()
        
        # 检查是否已存在，如果存在则更新
        cursor.execute(f"SELECT id FROM {table_name} WHERE image_id = ?", (image_id,))
        result = cursor.fetchone()
        
        if result:
            cursor.execute(
                f"UPDATE {table_name} SET embedding = vec_f32(?) WHERE image_id = ?",
                (vector_json, image_id)
            )
            print(f"更新{text_type}向量成功: {image_id}")
        else:
            cursor.execute(
                f"INSERT INTO {table_name}(image_id, embedding) VALUES (?, vec_f32(?))",
                (image_id, vector_json)
            )
            print(f"添加{text_type}向量成功: {image_id}")
        
        conn.commit()
        return True
        
    except Exception as e:
        print(f"添加{text_type}向量失败: {e}")
        traceback.print_exc()
        return False

def add_title_vector(conn: sqlite3.Connection, image_id: int, title: str):
    """将标题文本添加到向量表"""
    return add_text_vector(conn, image_id, title, "title_vectors", "标题")

def add_description_vector(conn: sqlite3.Connection, image_id: int, description: str):
    """将描述文本添加到向量表"""
    return add_text_vector(conn, image_id, description, "description_vectors", "描述")

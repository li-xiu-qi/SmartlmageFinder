"""
向量操作的通用工具函数
"""
import traceback
import sqlite3

from ...config import settings

def delete_vectors(conn: sqlite3.Connection, image_id: int):
    """从向量表中删除指定图片ID的所有向量"""
    try:
        conn.enable_load_extension(True)
        conn.execute(f"SELECT load_extension('{settings.get_config().VECTOR_DB_DRIVER}')")
        
        cursor = conn.cursor()
        
        # 删除各个表中的向量
        cursor.execute("DELETE FROM title_vectors WHERE image_id = ?", (image_id,))
        cursor.execute("DELETE FROM description_vectors WHERE image_id = ?", (image_id,))
        cursor.execute("DELETE FROM image_vectors WHERE image_id = ?", (image_id,))
        
        conn.commit()
        print(f"删除向量成功: {image_id}")
        return True
        
    except Exception as e:
        print(f"删除向量失败: {e}")
        traceback.print_exc()
        return False

def delete_vector_by_type(conn: sqlite3.Connection, image_id: int, vector_table: str):
    """删除指定类型的向量
    
    Args:
        conn: 数据库连接
        image_id: 图片ID
        vector_table: 向量表名称 (title_vectors, description_vectors, image_vectors)
    """
    try:
        conn.enable_load_extension(True)
        conn.execute(f"SELECT load_extension('{settings.get_config().VECTOR_DB_DRIVER}')")
        conn.execute(f"DELETE FROM {vector_table} WHERE image_id = ?", (image_id,))
        conn.commit()
        print(f"删除{vector_table}向量成功: {image_id}")
        return True
    except Exception as e:
        print(f"删除{vector_table}向量失败: {e}")
        traceback.print_exc()
        return False


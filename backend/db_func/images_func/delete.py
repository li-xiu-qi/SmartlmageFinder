"""
删除图片记录相关函数
"""
import sqlite3

from ..vector_func.delete_vectors import delete_vectors


def delete_image( conn: sqlite3.Connection, image_id: int,) -> bool:
    """删除图片记录及相关向量"""
    cursor = conn.cursor()
    
    # 检查图片是否存在
    cursor.execute("SELECT id FROM images WHERE id = ?", (image_id,))
    if not cursor.fetchone():
        return False
    
    # 执行删除
    cursor.execute("DELETE FROM images WHERE id = ?", (image_id,))
    conn.commit()
    
    # 从向量索引中删除
    try:
        delete_vectors(conn, image_id)
    except Exception as e:
        print(f"删除向量索引失败: {e}")
    
    return True

"""
删除图片记录相关函数
"""
import sqlite3
from typing import List, Dict, Any

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


def batch_delete_images(conn: sqlite3.Connection, image_ids: List[int]) -> Dict[str, Any]:
    """
    批量删除图片记录及相关向量
    
    Args:
        conn: 数据库连接
        image_ids: 要删除的图片ID列表
        
    Returns:
        Dict包含删除结果统计信息:
        - success_count: 成功删除的数量
        - failed_count: 删除失败的数量 
        - total_count: 总数量
        - failed_ids: 删除失败的ID列表
        - errors: 具体错误信息字典
    """
    cursor = conn.cursor()
    
    success_count = 0
    failed_count = 0
    failed_ids = []
    errors = {}
    total_count = len(image_ids)
    
    for image_id in image_ids:
        try:
            # 检查图片是否存在
            cursor.execute("SELECT id FROM images WHERE id = ?", (image_id,))
            if not cursor.fetchone():
                failed_count += 1
                failed_ids.append(image_id)
                errors[str(image_id)] = "图片不存在"
                continue
            
            # 执行删除
            cursor.execute("DELETE FROM images WHERE id = ?", (image_id,))
            
            # 从向量索引中删除
            try:
                delete_vectors(conn, image_id)
            except Exception as e:
                print(f"删除图片 {image_id} 的向量索引失败: {e}")
                # 向量删除失败不影响数据库删除，但记录警告
            
            success_count += 1
            
        except Exception as e:
            failed_count += 1
            failed_ids.append(image_id)
            errors[str(image_id)] = str(e)
            print(f"删除图片 {image_id} 失败: {e}")
    
    # 提交所有成功的删除操作
    try:
        conn.commit()
    except Exception as e:
        print(f"提交删除操作失败: {e}")
        # 如果提交失败，回滚并调整统计信息
        conn.rollback()
        for image_id in image_ids:
            if image_id not in failed_ids:
                failed_ids.append(image_id)
                errors[str(image_id)] = "数据库提交失败"
        failed_count = total_count
        success_count = 0
    
    return {
        "success_count": success_count,
        "failed_count": failed_count,
        "total_count": total_count,
        "failed_ids": failed_ids,
        "errors": errors
    }

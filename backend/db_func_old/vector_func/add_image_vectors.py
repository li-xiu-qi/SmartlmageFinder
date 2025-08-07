"""
图像向量相关操作
"""
import json
import os
import traceback
import sqlite3

from ...ai_func.generate_vector import encode_image

def add_image_vector(conn: sqlite3.Connection, image_id: int, image_path: str):
    """将图像添加到向量表"""
    if not image_path or not os.path.exists(image_path):
        print(f"图像文件不存在: {image_path}")
        return None
    
    try:        # 生成向量
        vector = encode_image(image_path)
        vector_json = json.dumps(vector.tolist())
        
        # 连接池已自动加载向量扩展，不再需要单独加载
        
        cursor = conn.cursor()
        
        # 检查是否已存在，如果存在则更新
        cursor.execute("SELECT id FROM image_vectors WHERE image_id = ?", (image_id,))
        result = cursor.fetchone()
        
        if result:
            cursor.execute(
                "UPDATE image_vectors SET embedding = vec_f32(?) WHERE image_id = ?",
                (vector_json, image_id)
            )
            print(f"更新图像向量成功: {image_id}")
        else:
            cursor.execute(
                "INSERT INTO image_vectors(image_id, embedding) VALUES (?, vec_f32(?))",
                (image_id, vector_json)
            )
            print(f"添加图像向量成功: {image_id}")
        
        conn.commit()
        return True
        
    except Exception as e:
        print(f"添加图像向量失败: {e}")
        traceback.print_exc()
        return False

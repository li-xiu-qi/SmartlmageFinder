"""
批量向量生成模块
专门用于优化向量生成效率，利用sentence transformer的批处理能力
"""
import json
import sqlite3
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

from ...ai_func.generate_vector import encode_text, encode_image


class BatchVectorManager:
    """批量向量管理器，用于高效生成和保存向量"""
    
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        
    def add_batch_vectors(self, image_data_list: List[Dict[str, Any]]) -> List[int]:
        """
        批量生成并添加向量到数据库
        
        Args:
            image_data_list: 图片数据列表，包含image_id, filepath, title, description等信息
            
        Returns:
            成功处理的image_id列表
        """
        if not image_data_list:
            return []
            
        # 提取所有需要处理的数据
        image_ids = []
        image_paths = []
        titles = []
        descriptions = []
        
        for data in image_data_list:
            image_ids.append(data['image_id'])
            image_paths.append(data['filepath'])
            titles.append(data.get('title', ''))
            descriptions.append(data.get('description', ''))
        
        print(f"开始批量生成向量，共 {len(image_data_list)} 张图片")
        
        try:
            # 批量生成图像向量
            self._batch_add_image_vectors(image_ids, image_paths)
            
            # 批量生成标题向量
            self._batch_add_text_vectors(image_ids, titles, "title_vectors", "标题")
            
            # 批量生成描述向量
            self._batch_add_text_vectors(image_ids, descriptions, "description_vectors", "描述")
            
            print(f"批量向量生成完成，共处理 {len(image_data_list)} 张图片")
            return image_ids
            
        except Exception as e:
            print(f"批量向量生成失败: {e}")
            # 如果批量失败，尝试逐个处理
            return self._fallback_single_processing(image_data_list)
    
    def _batch_add_image_vectors(self, image_ids: List[int], image_paths: List[str]):
        """批量生成图像向量"""
        # 过滤存在的图片文件
        valid_data = []
        for image_id, image_path in zip(image_ids, image_paths):
            if image_path and Path(image_path).exists():
                valid_data.append((image_id, image_path))
        
        if not valid_data:
            print("没有有效的图片文件需要处理")
            return
            
        valid_ids, valid_paths = zip(*valid_data)
        
        print(f"批量生成图像向量，共 {len(valid_paths)} 张图片")
        
        # 批量生成向量
        vectors = encode_image(list(valid_paths))
        
        # 批量保存向量
        cursor = self.conn.cursor()
        
        for image_id, vector in zip(valid_ids, vectors):
            vector_json = json.dumps(vector.tolist())
            
            # 检查是否已存在
            cursor.execute("SELECT id FROM image_vectors WHERE image_id = ?", (image_id,))
            result = cursor.fetchone()
            
            if result:
                cursor.execute(
                    "UPDATE image_vectors SET embedding = vec_f32(?) WHERE image_id = ?",
                    (vector_json, image_id)
                )
            else:
                cursor.execute(
                    "INSERT INTO image_vectors(image_id, embedding) VALUES (?, vec_f32(?))",
                    (image_id, vector_json)
                )
        
        self.conn.commit()
        print(f"批量保存图像向量完成，共保存 {len(valid_ids)} 个向量")
    
    def _batch_add_text_vectors(self, image_ids: List[int], texts: List[str], 
                               table_name: str, text_type: str):
        """批量生成文本向量"""
        # 过滤非空文本
        valid_data = []
        for image_id, text in zip(image_ids, texts):
            if text and text.strip():
                valid_data.append((image_id, text.strip()))
        
        if not valid_data:
            print(f"没有有效的{text_type}文本需要处理")
            return
            
        valid_ids, valid_texts = zip(*valid_data)
        
        print(f"批量生成{text_type}向量，共 {len(valid_texts)} 个文本")
        
        # 批量生成向量
        vectors = encode_text(list(valid_texts))
        
        # 批量保存向量
        cursor = self.conn.cursor()
        
        for image_id, vector in zip(valid_ids, vectors):
            vector_json = json.dumps(vector.tolist())
            
            # 检查是否已存在
            cursor.execute(f"SELECT id FROM {table_name} WHERE image_id = ?", (image_id,))
            result = cursor.fetchone()
            
            if result:
                cursor.execute(
                    f"UPDATE {table_name} SET embedding = vec_f32(?) WHERE image_id = ?",
                    (vector_json, image_id)
                )
            else:
                cursor.execute(
                    f"INSERT INTO {table_name}(image_id, embedding) VALUES (?, vec_f32(?))",
                    (image_id, vector_json)
                )
        
        self.conn.commit()
        print(f"批量保存{text_type}向量完成，共保存 {len(valid_ids)} 个向量")
    
    def _fallback_single_processing(self, image_data_list: List[Dict[str, Any]]) -> List[int]:
        """
        降级处理：如果批量处理失败，则逐个处理
        """
        print("批量处理失败，使用逐个处理模式")
        from .add_image_vectors import add_image_vector
        from .add_text_vectors import add_title_vector, add_description_vector
        
        success_ids = []
        for data in image_data_list:
            try:
                image_id = data['image_id']
                
                # 逐个生成向量
                add_image_vector(self.conn, image_id, data['filepath'])
                add_title_vector(self.conn, image_id, data.get('title', ''))
                add_description_vector(self.conn, image_id, data.get('description', ''))
                
                success_ids.append(image_id)
                
            except Exception as e:
                print(f"处理图片 ID {data.get('image_id')} 失败: {e}")
                continue
        
        return success_ids


def batch_add_vectors_for_images(conn: sqlite3.Connection, 
                                 image_data_list: List[Dict[str, Any]]) -> List[int]:
    """
    便捷函数：批量为图片生成向量
    
    Args:
        conn: 数据库连接
        image_data_list: 图片数据列表，每个元素应包含:
            - image_id: 图片ID
            - filepath: 图片文件路径
            - title: 图片标题 (可选)
            - description: 图片描述 (可选)
    
    Returns:
        成功处理的image_id列表
    """
    manager = BatchVectorManager(conn)
    return manager.add_batch_vectors(image_data_list)

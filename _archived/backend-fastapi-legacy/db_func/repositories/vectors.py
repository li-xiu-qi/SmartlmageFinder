"""
向量数据仓库
处理向量相关的所有数据库操作
"""
import json
import sqlite3
import traceback
from typing import Dict, List, Any, Optional
from pathlib import Path

from .base import BaseRepository


class VectorRepository(BaseRepository):
    """向量数据仓库类"""
    
    def add_image_vector(self, image_id: int, image_path: str) -> bool:
        """
        为图片添加图像向量
        
        Args:
            image_id: 图片ID
            image_path: 图片文件路径
            
        Returns:
            bool: 是否添加成功
        """
        if not image_path or not Path(image_path).exists():
            print(f"图像文件不存在: {image_path}")
            return False
        
        try:
            # 使用AI功能生成向量
            from ...ai_func.generate_vector import encode_image
            vector = encode_image(image_path)
            vector_json = json.dumps(vector.tolist())
            
            with self.get_connection() as conn:
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
    
    def add_text_vector(self, image_id: int, text: str, vector_type: str) -> bool:
        """
        为图片添加文本向量
        
        Args:
            image_id: 图片ID
            text: 文本内容
            vector_type: 向量类型 ('title' 或 'description')
            
        Returns:
            bool: 是否添加成功
        """
        if not text or not text.strip():
            return False
        
        if vector_type not in ['title', 'description']:
            raise ValueError("vector_type 必须是 'title' 或 'description'")
        
        table_name = f"{vector_type}_vectors"
        
        try:
            # 使用AI功能生成向量
            from ...ai_func.generate_vector import encode_text
            vector = encode_text(text)
            vector_json = json.dumps(vector.tolist())
            
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # 检查是否已存在，如果存在则更新
                cursor.execute(f"SELECT id FROM {table_name} WHERE image_id = ?", (image_id,))
                result = cursor.fetchone()
                
                if result:
                    cursor.execute(
                        f"UPDATE {table_name} SET embedding = vec_f32(?) WHERE image_id = ?",
                        (vector_json, image_id)
                    )
                    print(f"更新{vector_type}向量成功: {image_id}")
                else:
                    cursor.execute(
                        f"INSERT INTO {table_name}(image_id, embedding) VALUES (?, vec_f32(?))",
                        (image_id, vector_json)
                    )
                    print(f"添加{vector_type}向量成功: {image_id}")
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"添加{vector_type}向量失败: {e}")
            traceback.print_exc()
            return False
    
    def add_title_vector(self, image_id: int, title: str) -> bool:
        """为图片添加标题向量"""
        return self.add_text_vector(image_id, title, 'title')
    
    def add_description_vector(self, image_id: int, description: str) -> bool:
        """为图片添加描述向量"""
        return self.add_text_vector(image_id, description, 'description')
    
    def delete_vectors(self, image_id: int) -> bool:
        """
        删除图片的所有向量
        
        Args:
            image_id: 图片ID
            
        Returns:
            bool: 是否删除成功
        """
        try:
            with self.get_connection() as conn:
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
    
    def delete_vector_by_type(self, image_id: int, vector_type: str) -> bool:
        """
        删除指定类型的向量
        
        Args:
            image_id: 图片ID
            vector_type: 向量类型 ('title', 'description', 'image')
            
        Returns:
            bool: 是否删除成功
        """
        if vector_type not in ['title', 'description', 'image']:
            raise ValueError("vector_type 必须是 'title', 'description' 或 'image'")
        
        table_name = f"{vector_type}_vectors"
        
        try:
            query = f"DELETE FROM {table_name} WHERE image_id = ?"
            affected_rows = self.execute_delete(query, (image_id,))
            
            if affected_rows > 0:
                print(f"删除{vector_type}向量成功: {image_id}")
                return True
            else:
                print(f"未找到图片 {image_id} 的{vector_type}向量")
                return False
                
        except Exception as e:
            print(f"删除{vector_type}向量失败: {e}")
            traceback.print_exc()
            return False
    
    def batch_add_vectors(self, image_data_list: List[Dict[str, Any]]) -> List[int]:
        """
        批量添加向量
        
        Args:
            image_data_list: 图片数据列表，每个元素应包含:
                - image_id: 图片ID
                - filepath: 图片文件路径
                - title: 图片标题 (可选)
                - description: 图片描述 (可选)
        
        Returns:
            List[int]: 成功处理的图片ID列表
        """
        if not image_data_list:
            return []
        
        try:
            # 使用批量向量管理器
            from .batch_vector_manager import BatchVectorManager
            
            with self.get_connection() as conn:
                manager = BatchVectorManager(conn)
                return manager.add_batch_vectors(image_data_list)
                
        except Exception as e:
            print(f"批量添加向量失败: {e}")
            # 如果批量失败，尝试逐个处理
            return self._fallback_single_processing(image_data_list)
    
    def _fallback_single_processing(self, image_data_list: List[Dict[str, Any]]) -> List[int]:
        """降级处理：如果批量处理失败，则逐个处理"""
        print("批量处理失败，使用逐个处理模式")
        
        success_ids = []
        for data in image_data_list:
            try:
                image_id = data['image_id']
                
                # 逐个生成向量
                self.add_image_vector(image_id, data['filepath'])
                self.add_title_vector(image_id, data.get('title', ''))
                self.add_description_vector(image_id, data.get('description', ''))
                
                success_ids.append(image_id)
                
            except Exception as e:
                print(f"处理图片 ID {data.get('image_id')} 失败: {e}")
                continue
        
        return success_ids
    
    def vector_search(self, query_embedding: List[float], vector_type: str, 
                     limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """
        执行向量搜索
        
        Args:
            query_embedding: 查询向量
            vector_type: 向量类型 ('title', 'description', 'image')
            limit: 返回结果数量限制
            offset: 结果偏移量
            
        Returns:
            List[Dict]: 搜索结果列表，包含image_id和相似度分数
        """
        if vector_type not in ['title', 'description', 'image']:
            raise ValueError("vector_type 必须是 'title', 'description' 或 'image'")
        
        table_name = f"{vector_type}_vectors"
        
        try:
            query_json = json.dumps(query_embedding)
            
            sql = f"""
            SELECT 
                vec.image_id, 
                (1 - vec.distance) AS score
            FROM 
                {table_name} AS vec
            WHERE 
                vec.embedding MATCH '{query_json}'
                AND k = {limit + offset}
            ORDER BY score DESC
            LIMIT {limit} OFFSET {offset}
            """
            
            results = self.execute_query(sql)
            return results
            
        except Exception as e:
            print(f"向量搜索失败: {e}")
            traceback.print_exc()
            return []
    
    def multi_vector_search(self, query_embedding: List[float], 
                           search_targets: List[str], 
                           filters: Optional[Dict[str, Any]] = None,
                           limit: int = 20, offset: int = 0,
                           exclude_image_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        执行多向量搜索
        
        Args:
            query_embedding: 查询向量
            search_targets: 搜索目标列表 ['title', 'description', 'image']
            filters: 过滤条件
            limit: 返回结果数量限制
            offset: 结果偏移量
            exclude_image_id: 要排除的图片ID
            
        Returns:
            List[Dict]: 搜索结果列表
        """
        try:
            # 导入具体的搜索函数
            from ...db_func.search_func.multi_vector_search import _vector_search
            
            with self.get_connection() as conn:
                return _vector_search(
                    conn=conn,
                    query_embedding=query_embedding,
                    search_targets=search_targets,
                    filters=filters,
                    limit=limit,
                    offset=offset,
                    exclude_image_id=exclude_image_id
                )
                
        except Exception as e:
            print(f"多向量搜索失败: {e}")
            traceback.print_exc()
            return []
    
    def get_vector_stats(self) -> Dict[str, int]:
        """
        获取向量统计信息
        
        Returns:
            Dict: 各类型向量的数量统计
        """
        stats = {}
        
        for vector_type in ['title', 'description', 'image']:
            table_name = f"{vector_type}_vectors"
            query = f"SELECT COUNT(*) as count FROM {table_name}"
            result = self.execute_query_one(query)
            stats[vector_type] = result['count'] if result else 0
        
        return stats
    
    def check_vector_exists(self, image_id: int, vector_type: str) -> bool:
        """
        检查指定类型的向量是否存在
        
        Args:
            image_id: 图片ID
            vector_type: 向量类型
            
        Returns:
            bool: 向量是否存在
        """
        if vector_type not in ['title', 'description', 'image']:
            raise ValueError("vector_type 必须是 'title', 'description' 或 'image'")
        
        table_name = f"{vector_type}_vectors"
        query = f"SELECT id FROM {table_name} WHERE image_id = ?"
        result = self.execute_query_one(query, (image_id,))
        return result is not None

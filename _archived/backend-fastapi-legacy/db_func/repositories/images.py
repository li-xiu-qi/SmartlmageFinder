"""
图片数据仓库
处理图片相关的所有数据库操作
"""
import sqlite3
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

from .base import BaseRepository
from ..utils.common import json_from_db_to_python, python_to_json_for_db
from ..core.connection import get_db_connection_from_pool


class ImageRepository(BaseRepository):
    """图片数据仓库类"""
    
    def get_by_id(self, image_id: int) -> Optional[Dict[str, Any]]:
        """通过ID获取图片信息"""
        query = "SELECT * FROM images WHERE id = ?"
        image = self.execute_query_one(query, (image_id,))
        return json_from_db_to_python(image) if image else None
    
    def get_list(
        self,
        page: int = 1,
        page_size: int = 20,
        sort_by: str = "created_at",
        order: str = "desc",
        filters: Optional[Dict[str, Any]] = None,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """获取图片列表，支持分页和过滤"""
        filters = filters or {}
        
        query = "SELECT * FROM images"
        count_query = "SELECT COUNT(*) as count FROM images"
        
        conditions = []
        params = []
        
        # 添加日期过滤条件
        if filters.get('start_date'):
            conditions.append("created_at >= ?")
            params.append(filters['start_date'])
        
        if filters.get('end_date'):
            conditions.append("created_at <= ?")
            params.append(filters['end_date'])
        
        # 文本过滤条件
        if filters.get('filename'):
            conditions.append("filename LIKE ?")
            params.append(f"%{filters['filename']}%")
        
        if filters.get('title'):
            conditions.append("title LIKE ?")
            params.append(f"%{filters['title']}%")
        
        if filters.get('description'):
            conditions.append("description LIKE ?")
            params.append(f"%{filters['description']}%")
        
        # 标签过滤逻辑
        if filters.get('tags') and len(filters['tags']) > 0:
            tag_conditions = []
            for tag in filters['tags']:
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
        images = self.execute_query(query, params)
        
        # 执行计数查询
        count_result = self.execute_query_one(count_query, params)
        total_count = count_result["count"] if count_result else 0
        
        # 处理JSON字段
        processed_images = [json_from_db_to_python(image) for image in images]
        return processed_images, total_count
    
    def get_by_ids(self, image_ids: List[int]) -> List[Dict[str, Any]]:
        """批量获取图片信息"""
        if not image_ids:
            return []
        
        placeholders = ", ".join(["?"] * len(image_ids))
        query = f"SELECT * FROM images WHERE id IN ({placeholders})"
        images = self.execute_query(query, image_ids)
        
        # 处理JSON字段
        return [json_from_db_to_python(image) for image in images]
    
    def create(self, image_data: Dict[str, Any]) -> int:
        """创建图片记录"""
        current_time_iso = datetime.now().isoformat(timespec='microseconds')
        
        sql = """
        INSERT INTO images (
            filename, filepath, title, description, 
            file_size, file_type, width, height,
            created_at, updated_at, metadata, tags
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        params = (
            image_data.get("filename", ""),
            image_data.get("filepath", ""),
            image_data.get("title", ""),
            image_data.get("description", ""),
            image_data.get("file_size", 0),
            image_data.get("file_type", ""),
            image_data.get("width", 0),
            image_data.get("height", 0),
            image_data.get("created_at", current_time_iso),
            current_time_iso,
            python_to_json_for_db(image_data.get("metadata", {}), {}),
            python_to_json_for_db(image_data.get("tags", []), [])
        )
        
        return self.execute_insert(sql, params)
    
    def batch_create(self, images_data: List[Dict[str, Any]]) -> List[int]:
        """批量创建图片记录"""
        if not images_data:
            return []
            
        current_time_iso = datetime.now().isoformat(timespec='microseconds')
        
        sql = """
        INSERT INTO images (
            filename, filepath, title, description, 
            file_size, file_type, width, height,
            created_at, updated_at, metadata, tags
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        image_ids = []
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            for image_data in images_data:
                params = (
                    image_data.get("filename", ""),
                    image_data.get("filepath", ""),
                    image_data.get("title", ""),
                    image_data.get("description", ""),
                    image_data.get("file_size", 0),
                    image_data.get("file_type", ""),
                    image_data.get("width", 0),
                    image_data.get("height", 0),
                    image_data.get("created_at", current_time_iso),
                    current_time_iso,
                    python_to_json_for_db(image_data.get("metadata", {}), {}),
                    python_to_json_for_db(image_data.get("tags", []), [])
                )
                
                cursor.execute(sql, params)
                if cursor.lastrowid:
                    image_ids.append(cursor.lastrowid)
            
            conn.commit()
        
        return image_ids
    
    def update(self, image_id: int, update_data: Dict[str, Any]) -> bool:
        """更新图片信息"""
        if not update_data:
            return False
            
        # 准备要更新的字段
        update_fields = []
        params = []
        
        # 处理基础字段
        for field in ['title', 'description', 'filename', 'filepath', 'file_size', 'file_type', 'width', 'height']:
            if field in update_data:
                update_fields.append(f"{field} = ?")
                params.append(update_data[field])
        
        # 处理JSON字段
        if 'tags' in update_data:
            update_fields.append("tags = ?")
            params.append(python_to_json_for_db(update_data['tags'], []))
        
        if 'metadata' in update_data:
            update_fields.append("metadata = ?")
            params.append(python_to_json_for_db(update_data['metadata'], {}))
        
        # 添加更新时间
        update_fields.append("updated_at = ?")
        params.append(datetime.now().isoformat(timespec='microseconds'))
        params.append(image_id)
        
        if update_fields:
            query = f"UPDATE images SET {', '.join(update_fields)} WHERE id = ?"
            affected_rows = self.execute_update(query, params)
            return affected_rows > 0
        
        return False
    
    def delete(self, image_id: int) -> bool:
        """删除图片记录"""
        query = "DELETE FROM images WHERE id = ?"
        affected_rows = self.execute_delete(query, (image_id,))
        return affected_rows > 0
    
    def batch_delete(self, image_ids: List[int]) -> Dict[str, Any]:
        """批量删除图片记录"""
        if not image_ids:
            return {"deleted_count": 0, "total_count": 0}
        
        deleted_count = 0
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            for image_id in image_ids:
                try:
                    cursor.execute("DELETE FROM images WHERE id = ?", (image_id,))
                    if cursor.rowcount > 0:
                        deleted_count += 1
                except Exception:
                    continue
            
            conn.commit()
        
        return {
            "deleted_count": deleted_count,
            "total_count": len(image_ids)
        }
    
    def exists(self, image_id: int) -> bool:
        """检查图片是否存在"""
        query = "SELECT id FROM images WHERE id = ?"
        result = self.execute_query_one(query, (image_id,))
        return result is not None
    
    def get_count(self) -> int:
        """获取图片总数"""
        query = "SELECT COUNT(*) as count FROM images"
        result = self.execute_query_one(query)
        return result["count"] if result else 0

"""
元数据数据仓库
处理图片元数据相关的所有数据库操作
"""
import json
import sqlite3
from typing import Dict, Any, List
from datetime import datetime

from .base import BaseRepository


class MetadataRepository(BaseRepository):
    """元数据数据仓库类"""
    
    def get_image_metadata(self, image_id: int) -> Dict[str, Any]:
        """
        获取图片的元数据
        
        Args:
            image_id: 图片ID
            
        Returns:
            Dict[str, Any]: 元数据字典
        """
        query = "SELECT metadata FROM images WHERE id = ?"
        result = self.execute_query_one(query, (image_id,))
        
        if not result or not result.get('metadata'):
            return {}
        
        try:
            return json.loads(result['metadata'])
        except json.JSONDecodeError:
            return {}
    
    def update_metadata(self, image_id: int, metadata_data: Dict[str, Any]) -> bool:
        """
        更新图片的元数据
        
        Args:
            image_id: 图片ID
            metadata_data: 新的元数据字典
            
        Returns:
            bool: 是否更新成功
        """
        try:
            # 确保所有键都是字符串，因为JSON对象的键必须是字符串
            validated_metadata_data = {str(k): v for k, v in metadata_data.items()}
            metadata_json = json.dumps(validated_metadata_data, ensure_ascii=False)
            updated_at_iso = datetime.now().isoformat(timespec='microseconds')
            
            query = """
            UPDATE images
            SET metadata = ?, updated_at = ?
            WHERE id = ?
            """
            params = (metadata_json, updated_at_iso, image_id)
            
            affected_rows = self.execute_update(query, params)
            
            if affected_rows > 0:
                return True
            else:
                print(f"警告：未找到ID为{image_id}的图片，无法更新元数据。")
                return False
                
        except json.JSONEncoder as e:
            print(f"将图片ID {image_id}的元数据编码为JSON时发生错误：{e}")
            return False
        except Exception as e:
            print(f"更新图片ID {image_id}的元数据时发生意外错误：{e}")
            return False
    
    def add_metadata_field(self, image_id: int, key: str, value: Any) -> bool:
        """
        为图片添加单个元数据字段
        
        Args:
            image_id: 图片ID
            key: 元数据键
            value: 元数据值
            
        Returns:
            bool: 是否添加成功
        """
        # 获取当前元数据
        current_metadata = self.get_image_metadata(image_id)
        
        # 添加新字段
        current_metadata[key] = value
        
        # 更新元数据
        return self.update_metadata(image_id, current_metadata)
    
    def remove_metadata_field(self, image_id: int, key: str) -> bool:
        """
        从图片元数据中移除指定字段
        
        Args:
            image_id: 图片ID
            key: 要移除的元数据键
            
        Returns:
            bool: 是否移除成功
        """
        # 获取当前元数据
        current_metadata = self.get_image_metadata(image_id)
        
        # 移除指定字段
        if key in current_metadata:
            del current_metadata[key]
            # 更新元数据
            return self.update_metadata(image_id, current_metadata)
        
        return True  # 字段不存在也算成功
    
    def get_metadata_field(self, image_id: int, key: str, default_value: Any = None) -> Any:
        """
        获取图片元数据中的特定字段
        
        Args:
            image_id: 图片ID
            key: 元数据键
            default_value: 默认值
            
        Returns:
            Any: 字段值或默认值
        """
        metadata = self.get_image_metadata(image_id)
        return metadata.get(key, default_value)
    
    def search_by_metadata(self, search_criteria: Dict[str, Any]) -> List[int]:
        """
        根据元数据搜索图片
        
        Args:
            search_criteria: 搜索条件字典
            
        Returns:
            List[int]: 符合条件的图片ID列表
        """
        if not search_criteria:
            return []
        
        query = "SELECT id, metadata FROM images WHERE metadata IS NOT NULL AND metadata != '{}'"
        results = self.execute_query(query)
        
        matching_ids = []
        for row in results:
            try:
                metadata = json.loads(row['metadata'])
                
                # 检查是否匹配所有搜索条件
                match = True
                for key, value in search_criteria.items():
                    if key not in metadata or metadata[key] != value:
                        match = False
                        break
                
                if match:
                    matching_ids.append(row['id'])
                    
            except (json.JSONDecodeError, TypeError):
                continue
        
        return matching_ids
    
    def get_all_metadata_keys(self) -> List[str]:
        """
        获取系统中所有使用过的元数据键
        
        Returns:
            List[str]: 元数据键列表
        """
        query = "SELECT metadata FROM images WHERE metadata IS NOT NULL AND metadata != '{}'"
        results = self.execute_query(query)
        
        all_keys = set()
        for row in results:
            try:
                metadata = json.loads(row['metadata'])
                all_keys.update(metadata.keys())
            except (json.JSONDecodeError, TypeError):
                continue
        
        return sorted(list(all_keys))
    
    def get_metadata_values(self, key: str) -> List[Any]:
        """
        获取指定元数据键的所有值
        
        Args:
            key: 元数据键
            
        Returns:
            List[Any]: 该键的所有唯一值列表
        """
        query = "SELECT metadata FROM images WHERE metadata IS NOT NULL AND metadata != '{}'"
        results = self.execute_query(query)
        
        values = set()
        for row in results:
            try:
                metadata = json.loads(row['metadata'])
                if key in metadata:
                    values.add(metadata[key])
            except (json.JSONDecodeError, TypeError):
                continue
        
        return sorted(list(values))
    
    def clear_metadata(self, image_id: int) -> bool:
        """
        清空图片的所有元数据
        
        Args:
            image_id: 图片ID
            
        Returns:
            bool: 是否清空成功
        """
        return self.update_metadata(image_id, {})

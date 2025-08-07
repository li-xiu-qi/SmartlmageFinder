"""
标签数据仓库
处理标签相关的所有数据库操作
"""
import json
import sqlite3
from typing import Dict, List, Set
from datetime import datetime

from .base import BaseRepository
from ..utils.common import python_to_json_for_db


class TagRepository(BaseRepository):
    """标签数据仓库类"""
    
    def get_image_tags(self, image_id: int) -> List[str]:
        """
        获取图片的所有标签
        
        Args:
            image_id: 图片ID
            
        Returns:
            List[str]: 标签列表
        """
        query = "SELECT tags FROM images WHERE id = ?"
        result = self.execute_query_one(query, (image_id,))
        
        if not result or not result.get('tags'):
            return []
        
        try:
            return json.loads(result['tags'])
        except json.JSONDecodeError:
            return []
    
    def update_tags(self, image_id: int, tags: List[str]) -> List[str]:
        """
        更新图片的标签（覆盖方式）
        
        Args:
            image_id: 图片ID
            tags: 新的标签列表（将完全替换旧的标签）
            
        Returns:
            List[str]: 更新后的标签列表
        """
        # 去重
        unique_tags = list(set(tags))
        
        # 生成时间戳
        current_time_iso = datetime.now().isoformat(timespec='microseconds')
        
        # 更新数据库
        query = "UPDATE images SET tags = ?, updated_at = ? WHERE id = ?"
        params = (python_to_json_for_db(unique_tags, []), current_time_iso, image_id)
        
        affected_rows = self.execute_update(query, params)
        return unique_tags if affected_rows > 0 else []
    
    def add_tags(self, image_id: int, new_tags: List[str]) -> List[str]:
        """
        为图片添加新标签（追加方式）
        
        Args:
            image_id: 图片ID
            new_tags: 要添加的新标签列表
            
        Returns:
            List[str]: 更新后的完整标签列表
        """
        # 获取当前标签
        current_tags = self.get_image_tags(image_id)
        
        # 合并并去重
        all_tags = list(set(current_tags + new_tags))
        
        # 更新标签
        return self.update_tags(image_id, all_tags)
    
    def remove_tags(self, image_id: int, tags_to_remove: List[str]) -> List[str]:
        """
        从图片中移除指定标签
        
        Args:
            image_id: 图片ID
            tags_to_remove: 要移除的标签列表
            
        Returns:
            List[str]: 更新后的标签列表
        """
        # 获取当前标签
        current_tags = self.get_image_tags(image_id)
        
        # 移除指定标签
        updated_tags = [tag for tag in current_tags if tag not in tags_to_remove]
        
        # 更新标签
        return self.update_tags(image_id, updated_tags)
    
    def get_all_tags(self) -> List[str]:
        """获取系统中所有标签"""
        query = "SELECT tags FROM images WHERE tags IS NOT NULL AND tags != '[]'"
        results = self.execute_query(query)
        
        # 提取并合并所有标签
        all_tags: Set[str] = set()
        for row in results:
            try:
                tags = json.loads(row['tags'])
                all_tags.update(tags)
            except (json.JSONDecodeError, TypeError):
                continue
        
        return sorted(list(all_tags))
    
    def get_tags_count(self) -> Dict[str, int]:
        """获取标签使用次数统计"""
        query = "SELECT tags FROM images WHERE tags IS NOT NULL AND tags != '[]'"
        results = self.execute_query(query)
        
        # 统计每个标签的出现次数
        tag_counts: Dict[str, int] = {}
        for row in results:
            try:
                tags = json.loads(row['tags'])
                for tag in tags:
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1
            except (json.JSONDecodeError, TypeError):
                continue
        
        return tag_counts
    
    def get_popular_tags(self, limit: int = 10) -> List[Dict[str, any]]:
        """
        获取最受欢迎的标签
        
        Args:
            limit: 返回的标签数量限制
            
        Returns:
            List[Dict]: 包含标签名和使用次数的列表，按使用次数降序排列
        """
        tag_counts = self.get_tags_count()
        
        # 按使用次数排序
        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
        
        # 转换为字典列表并限制数量
        return [
            {"tag": tag, "count": count}
            for tag, count in sorted_tags[:limit]
        ]
    
    def search_tags(self, keyword: str) -> List[str]:
        """
        搜索包含关键词的标签
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            List[str]: 匹配的标签列表
        """
        all_tags = self.get_all_tags()
        keyword_lower = keyword.lower()
        
        # 模糊匹配标签
        matching_tags = [
            tag for tag in all_tags
            if keyword_lower in tag.lower()
        ]
        
        return matching_tags
    
    def get_images_by_tag(self, tag: str) -> List[int]:
        """
        根据标签获取图片ID列表
        
        Args:
            tag: 标签名
            
        Returns:
            List[int]: 包含该标签的图片ID列表
        """
        query = "SELECT id FROM images WHERE tags LIKE ?"
        # 使用JSON包含检查
        params = (f'%"{tag}"%',)
        
        results = self.execute_query(query, params)
        return [row['id'] for row in results]
    
    def get_images_by_tags(self, tags: List[str], match_all: bool = True) -> List[int]:
        """
        根据多个标签获取图片ID列表
        
        Args:
            tags: 标签列表
            match_all: 是否需要匹配所有标签（True）或匹配任意标签（False）
            
        Returns:
            List[int]: 符合条件的图片ID列表
        """
        if not tags:
            return []
        
        if match_all:
            # 需要匹配所有标签
            conditions = []
            params = []
            for tag in tags:
                conditions.append("tags LIKE ?")
                params.append(f'%"{tag}"%')
            
            where_clause = " AND ".join(conditions)
            query = f"SELECT id FROM images WHERE {where_clause}"
        else:
            # 匹配任意标签
            conditions = []
            params = []
            for tag in tags:
                conditions.append("tags LIKE ?")
                params.append(f'%"{tag}"%')
            
            where_clause = " OR ".join(conditions)
            query = f"SELECT id FROM images WHERE {where_clause}"
        
        results = self.execute_query(query, params)
        return [row['id'] for row in results]

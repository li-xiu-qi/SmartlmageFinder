"""
搜索数据仓库
处理搜索相关的所有数据库操作
"""
import sqlite3
import logging
from typing import Dict, List, Any, Optional, Tuple

from .base import BaseRepository

logger = logging.getLogger(__name__)


class SearchRepository(BaseRepository):
    """搜索数据仓库类"""
    _ALLOWED_VECTOR_TARGETS = {"title", "description", "image"}

    @classmethod
    def _sanitize_targets(cls, targets: List[str]) -> List[str]:
        valid = [t for t in targets if isinstance(t, str) and t in cls._ALLOWED_VECTOR_TARGETS]
        return valid or ["title", "description", "image"]
    
    def basic_search(self, text: str = None, search_type: str = "both", 
                    filters: Dict[str, Any] = None, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """
        基础文本搜索
        
        Args:
            text: 搜索文本
            search_type: 搜索类型，可选值：title, description, both
            filters: 过滤条件字典
            limit: 返回结果数量限制
            offset: 结果偏移量
            
        Returns:
            List[Dict]: 搜索结果列表
        """
        if not text or not text.strip():
            return []
            
        # 构建基础查询
        query = "SELECT * FROM images"
        conditions = []
        params = []
        
        # 处理文本搜索条件
        search_conditions = []
        if search_type in ["title", "both"]:
            search_conditions.append("title LIKE ?")
            params.append(f"%{text.strip()}%")
            
        if search_type in ["description", "both"]:
            search_conditions.append("description LIKE ?")
            params.append(f"%{text.strip()}%")
            
        if search_conditions:
            conditions.append("(" + " OR ".join(search_conditions) + ")")
        
        # 处理过滤条件
        if filters:
            if filters.get('filename'):
                conditions.append("filename LIKE ?")
                params.append(f"%{filters['filename']}%")
                
            if filters.get('tags'):
                tag_conditions = []
                for tag in filters['tags']:
                    tag_conditions.append("tags LIKE ?")
                    params.append(f'%"{tag}"%')
                if tag_conditions:
                    conditions.append("(" + " OR ".join(tag_conditions) + ")")
            
            if filters.get('start_date'):
                conditions.append("created_at >= ?")
                params.append(filters['start_date'])
            
            if filters.get('end_date'):
                conditions.append("created_at <= ?")
                params.append(filters['end_date'])
        
        # 组合查询条件
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        # 添加排序和分页
        query += " ORDER BY created_at DESC"
        query += f" LIMIT {limit} OFFSET {offset}"
        
        return self.execute_query(query, params)
    
    def search_with_filters(self, filters: Dict[str, Any], 
                           limit: int = 20, offset: int = 0) -> Tuple[List[Dict[str, Any]], int]:
        """
        带过滤条件的搜索
        
        Args:
            filters: 过滤条件字典
            limit: 返回结果数量限制
            offset: 结果偏移量
            
        Returns:
            Tuple[List[Dict], int]: (搜索结果列表, 总数)
        """
        # 构建基础查询
        query = "SELECT * FROM images"
        count_query = "SELECT COUNT(*) as count FROM images"
        
        conditions = []
        params = []
        
        # 处理各种过滤条件
        if filters.get('start_date'):
            conditions.append("created_at >= ?")
            params.append(filters['start_date'])
        
        if filters.get('end_date'):
            conditions.append("created_at <= ?")
            params.append(filters['end_date'])
        
        if filters.get('tags'):
            tag_conditions = []
            for tag in filters['tags']:
                tag_conditions.append("tags LIKE ?")
                params.append(f'%"{tag}"%')
            conditions.append("(" + " OR ".join(tag_conditions) + ")")
        
        if filters.get('keyword'):
            keyword_conditions = []
            for field in ['title', 'description', 'filename']:
                keyword_conditions.append(f"{field} LIKE ?")
                params.append(f"%{filters['keyword']}%")
            conditions.append("(" + " OR ".join(keyword_conditions) + ")")
        
        # 组合查询条件
        if conditions:
            where_clause = " WHERE " + " AND ".join(conditions)
            query += where_clause
            count_query += where_clause
        
        # 添加排序和分页
        sort_by = filters.get('sort_by', 'created_at')
        order = filters.get('order', 'desc')
        query += f" ORDER BY {sort_by} {order}"
        query += f" LIMIT {limit} OFFSET {offset}"
        
        # 执行查询
        results = self.execute_query(query, params)
        count_result = self.execute_query_one(count_query, params)
        total_count = count_result['count'] if count_result else 0
        
        return results, total_count
    
    def get_filtered_image_ids(self, filters: Dict[str, Any]) -> List[int]:
        """
        根据过滤条件获取图片ID列表
        
        Args:
            filters: 过滤条件字典
            
        Returns:
            List[int]: 符合条件的图片ID列表
        """
        query = "SELECT id FROM images"
        conditions = []
        params = []
        
        # 处理过滤条件（与search_with_filters类似的逻辑）
        if filters.get('start_date'):
            conditions.append("created_at >= ?")
            params.append(filters['start_date'])
        
        if filters.get('end_date'):
            conditions.append("created_at <= ?")
            params.append(filters['end_date'])
        
        if filters.get('tags'):
            tag_conditions = []
            for tag in filters['tags']:
                tag_conditions.append("tags LIKE ?")
                params.append(f'%"{tag}"%')
            conditions.append("(" + " OR ".join(tag_conditions) + ")")
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        results = self.execute_query(query, params)
        return [row['id'] for row in results]

    def vector_search(self, vector_type: str, query_vector: list, top_k: int = 50) -> List[Tuple[int, float]]:
        """基础向量搜索方法"""
        try:
            table_name = f"{vector_type}_vectors"
            
            # 使用sqlite-vec的MATCH语法，确保向量格式正确
            query = f"""
            SELECT image_id, distance
            FROM {table_name}
            WHERE embedding MATCH ? AND k = ?
            ORDER BY distance ASC
            """
            
            # 将向量转换为JSON字符串，确保格式正确
            import json
            query_embedding_json = json.dumps(query_vector)
            
            results = self.execute_query(query, (query_embedding_json, top_k))
            return [(row['image_id'], row['distance']) for row in results]
                
        except Exception as e:
            logger.error(f"向量搜索失败: {str(e)}")
            return []

    def _vector_search_with_filter(self, vector_type: str, query_vector: list, 
                                  filtered_ids: List[int], top_k: int = 50) -> List[Tuple[int, float]]:
        """在指定ID范围内进行向量搜索"""
        try:
            if not filtered_ids:
                return []
                
            table_name = f"{vector_type}_vectors"
            filtered_ids_str = ','.join(str(id) for id in filtered_ids)
            
            # 使用sqlite-vec的MATCH语法，同时限制在过滤的ID范围内
            query = f"""
            SELECT image_id, distance
            FROM {table_name}
            WHERE image_id IN ({filtered_ids_str})
              AND embedding MATCH ? AND k = ?
            ORDER BY distance ASC
            """
            
            # 将向量转换为JSON字符串，确保格式正确
            import json
            query_embedding_json = json.dumps(query_vector)
            
            results = self.execute_query(query, (query_embedding_json, min(top_k, len(filtered_ids))))
            return [(row['image_id'], row['distance']) for row in results]
                
        except Exception as e:
            logger.error(f"过滤向量搜索失败: {str(e)}")
            return []

    def search_by_image_vector(self, query_vector: list, top_k: int = 50) -> List[Tuple[int, float]]:
        """使用图像向量搜索"""
        return self.vector_search('image', query_vector, top_k)

    def search_by_title_vector(self, query_vector: list, top_k: int = 50) -> List[Tuple[int, float]]:
        """使用标题向量搜索"""
        return self.vector_search('title', query_vector, top_k)

    def search_by_description_vector(self, query_vector: list, top_k: int = 50) -> List[Tuple[int, float]]:
        """使用描述向量搜索"""
        return self.vector_search('description', query_vector, top_k)
    
    def image_search(self, image_path: str, search_targets: List[str] = ["image"], 
                    filters: Dict[str, Any] = None, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """
        使用图像路径执行向量搜索
        
        Args:
            image_path: 图像文件路径
            search_targets: 要搜索的目标类型列表，可包含："title", "description", "image"
            filters: 过滤条件字典
            limit: 返回结果的最大数量
            offset: 结果的起始偏移量，用于分页
            
        Returns:
            List[Dict]: 图像信息字典的列表，按综合得分排序
        """
        from ...ai_func.generate_vector import encode_image
        
        # 将图像转换为向量
        query_embedding = encode_image(image_path).tolist()
        
        # 使用统一的多向量搜索方法
        return self._multi_vector_search(
            query_embedding=query_embedding,
            search_targets=search_targets,
            filters=filters,
            limit=limit,
            offset=offset
        )
    
    def _get_images_by_ids(self, image_ids: List[int]) -> List[Dict[str, Any]]:
        """根据图片ID列表获取完整图片信息"""
        if not image_ids:
            return []
            
        placeholders = ','.join(['?'] * len(image_ids))
        query = f"SELECT * FROM images WHERE id IN ({placeholders})"
        return self.execute_query(query, image_ids)
    
    def text_search(self, text_query: str, search_targets: List[str] = ["title", "description", "image"],
                   filters: Dict[str, Any] = None, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """
        使用文本查询执行多维向量搜索
        
        Args:
            text_query: 文本查询内容
            search_targets: 要搜索的目标类型列表，可包含："title", "description", "image"
            filters: 过滤条件字典
            limit: 返回结果的最大数量
            offset: 结果的起始偏移量，用于分页
            
        Returns:
            List[Dict]: 图像信息字典的列表，按综合得分排序
        """
        from ...ai_func.generate_vector import encode_text
        
        # 将文本转换为向量
        query_embedding = encode_text(text_query).tolist()
        
        # 使用统一的多向量搜索方法
        return self._multi_vector_search(
            query_embedding=query_embedding,
            search_targets=self._sanitize_targets(search_targets),
            filters=filters,
            limit=limit,
            offset=offset
        )

    def unified_search(self, query_type: str, query_content: str, 
                      search_targets: List[str] = ["title", "description", "image"],
                      filters: Dict[str, Any] = None, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """
        统一的搜索方法，支持文本查询和图像查询
        
        Args:
            query_type: 查询类型，可选值："text", "image"
                        if 'public_url' not in image:
                            image['public_url'] = build_public_url(image.get('filepath') or '')
            offset: 结果的起始偏移量，用于分页
            
        Returns:
            List[Dict]: 图像信息字典的列表，按综合得分排序
        """
        if query_type == "text":
            return self.text_search(query_content, self._sanitize_targets(search_targets), filters, limit, offset)
        elif query_type == "image":
            return self.image_search(query_content, search_targets, filters, limit, offset)
        else:
            raise ValueError(f"不支持的查询类型: {query_type}，支持的类型：'text', 'image'")

    def vector_search_direct(self, query_embedding: list, search_targets: List[str] = ["title", "description", "image"],
                           filters: Dict[str, Any] = None, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """
        直接使用向量进行搜索
        
        Args:
            query_embedding: 查询向量
            search_targets: 要搜索的目标类型列表，可包含："title", "description", "image"
            filters: 过滤条件字典
            limit: 返回结果的最大数量
            offset: 结果的起始偏移量，用于分页
            
        Returns:
            List[Dict]: 图像信息字典的列表，按综合得分排序
        """
        return self._multi_vector_search(
            query_embedding=query_embedding,
            search_targets=search_targets,
            filters=filters,
            limit=limit,
            offset=offset
        )
    
    def _multi_vector_search(self, query_embedding: list, search_targets: List[str], 
                           filters: Dict[str, Any] = None, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """执行多向量检索并融合得分。

        1. 过滤得到候选 ID
        2. 针对每个向量目标执行向量检索
        3. 融合 (平均得分) 并排序 + 分页
        4. 附加 score 与 public_url
        """
        search_targets = self._sanitize_targets(search_targets)
        filtered_ids = self.get_filtered_image_ids(filters or {})
        if not filtered_ids:
            return []

        if len(search_targets) == 1:
            vector_results = self._vector_search_with_filter(search_targets[0], query_embedding, filtered_ids, limit + offset)
            if not vector_results:
                return []
            paginated = vector_results[offset:offset + limit]
            ids = [r[0] for r in paginated]
            images = self._get_images_by_ids(ids)
            id2score = {r[0]: 1 - r[1] for r in paginated}
            for img in images:
                img['score'] = id2score.get(img['id'], 0)
                if 'filepath' in img and img.get('filepath'):
                    import os
                    img['public_url'] = f"/static/images/{os.path.basename(img['filepath'])}"
            return images

        all_results: Dict[int, List[float]] = {}
        for target in search_targets:
            vres = self._vector_search_with_filter(target, query_embedding, filtered_ids, limit * 2)
            for iid, dist in vres:
                score = 1 - dist
                all_results.setdefault(iid, []).append(score)

        scored = [(iid, sum(scores)/len(scores)) for iid, scores in all_results.items()]
        scored.sort(key=lambda x: x[1], reverse=True)
        page = scored[offset:offset + limit]
        ids = [i for i, _ in page]
        images = self._get_images_by_ids(ids)
        id2score = {i: s for i, s in page}
        for img in images:
            img['score'] = id2score.get(img['id'], 0)
            if 'filepath' in img and img.get('filepath'):
                import os
                img['public_url'] = f"/static/images/{os.path.basename(img['filepath'])}"
        images.sort(key=lambda x: x['score'], reverse=True)
        return images
    
    def search_by_image_id(self, image_id: int, vector_type: str = "image", 
                          k: int = 5, filters: Optional[Dict[str, Any]] = None,
                          exclude_self: bool = True) -> List[Dict[str, Any]]:
        """
        使用指定图像ID的向量进行相似图像搜索
        
        Args:
            image_id: 要搜索的图像ID
            vector_type: 要使用的向量类型，可选值: "title", "description", "image"
            k: 返回的相似结果数量
            filters: 过滤条件字典
            exclude_self: 是否从结果中排除查询图像本身
            
        Returns:
            List[Dict]: 相似图像列表，按相似度排序
        """
        # 首先验证查询的图像ID是否存在
        check_query = "SELECT id FROM images WHERE id = ?"
        if not self.execute_query_one(check_query, (image_id,)):
            logger.warning(f"图像ID {image_id} 不存在于数据库中")
            return []
            
        # 获取过滤后的图像ID列表
        filtered_ids = self.get_filtered_image_ids(filters or {})
        
        # 如果需要排除自己，从过滤ID中移除
        if exclude_self and image_id in filtered_ids:
            filtered_ids.remove(image_id)
            
        # 如果没有符合条件的结果，直接返回空列表
        if not filtered_ids:
            logger.info("过滤后没有符合条件的图像ID")
            return []
            
        # 构建过滤ID字符串
        filtered_ids_str = ','.join(str(id) for id in filtered_ids)
        
        # 确定向量表名
        vector_table = f"{vector_type}_vectors"
        
        # 验证向量表中是否存在该图像ID的向量
        vector_check_query = f"SELECT COUNT(*) as count FROM {vector_table} WHERE image_id = ?"
        vector_count_result = self.execute_query_one(vector_check_query, (image_id,))
        if not vector_count_result or vector_count_result.get('count', 0) == 0:
            logger.warning(f"图像ID {image_id} 在 {vector_table} 表中不存在向量")
            return []
        
        # 使用原来的实现方式：WITH子句 + 子查询
        try:            
            sql_query = f"""
            WITH query_vector AS (
                SELECT embedding 
                FROM {vector_table}
                WHERE image_id = ?
            )
            SELECT 
                img.id,
                img.filename, 
                img.filepath,
                img.title,
                img.description,
                img.file_size,
                img.file_type,
                img.width,
                img.height,
                img.created_at,
                img.updated_at,
                img.metadata,
                img.tags,
                res.distance,
                (1 - res.distance) AS score
            FROM (
                SELECT 
                    image_id,
                    distance
                FROM 
                    {vector_table}
                WHERE 
                    image_id IN ({filtered_ids_str})
                    AND embedding MATCH (SELECT embedding FROM query_vector)
                    AND k = ?
            ) AS res
            JOIN 
                images AS img ON res.image_id = img.id
            ORDER BY 
                res.distance ASC
            """
            
            results = self.execute_query(sql_query, (image_id, k))
            
            logger.info(f"使用图像ID {image_id} 的 {vector_type} 向量找到 {len(results)} 个相似结果")
            return results
            
        except Exception as e:
            logger.error(f"向量搜索失败: {str(e)}")
            return []

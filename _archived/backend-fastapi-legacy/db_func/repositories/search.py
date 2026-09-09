"""
搜索数据仓库
处理搜索相关的所有数据库操作
"""
import sqlite3
import logging
from typing import Dict, List, Any, Optional, Tuple

from .base import BaseRepository
from ...utils.image_utils import build_public_url

logger = logging.getLogger(__name__)


class SearchRepository(BaseRepository):
    """搜索数据仓库类

    """
    _ALLOWED_VECTOR_TARGETS = {"title", "description", "image"}

    @classmethod
    def _sanitize_targets(cls, targets: List[str]) -> List[str]:
        valid = [t for t in targets if isinstance(t, str) and t in cls._ALLOWED_VECTOR_TARGETS]
        return valid or ["title", "description", "image"]
    
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

    # =============== Fuzzy (模糊) 文本搜索 ===============
    def fuzzy_search(self, text: str, fields: Optional[List[str]] = None,
                     filters: Optional[Dict[str, Any]] = None,
                     limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """基于 LIKE 的轻量模糊搜索（不走向量）。

        Args:
            text: 搜索关键字（至少1个非空字符）
            fields: 参与匹配的字段集合，支持: title, description, filename
            filters: 额外过滤（tags / start_date / end_date）
            limit: 数量限制
            offset: 分页偏移
        """
        if not text or not text.strip():
            return []
        fields = fields or ["title", "description"]
        allowed = {"title", "description", "filename"}
        use_fields = [f for f in fields if f in allowed] or ["title", "description"]

        query = "SELECT * FROM images"
        conditions: List[str] = []
        params: List[Any] = []

        like_exprs = []
        kw = f"%{text.strip()}%"
        for f in use_fields:
            like_exprs.append(f"{f} LIKE ?")
            params.append(kw)
        if like_exprs:
            conditions.append("(" + " OR ".join(like_exprs) + ")")

        filters = filters or {}
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

        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY created_at DESC"
        query += f" LIMIT {limit} OFFSET {offset}"
        results = self.execute_query(query, params)
        return self._attach_public_url(results)
    
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
                    filters: Dict[str, Any] = None, limit: int = 20, offset: int = 0,
                    weights: Optional[Dict[str, float]] = None, min_score: Optional[float] = None) -> List[Dict[str, Any]]:
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
            offset=offset,
            weights=weights,
            min_score=min_score
        )
    
    def _get_images_by_ids(self, image_ids: List[int]) -> List[Dict[str, Any]]:
        """根据图片ID列表获取完整图片信息"""
        if not image_ids:
            return []
            
        placeholders = ','.join(['?'] * len(image_ids))
        query = f"SELECT * FROM images WHERE id IN ({placeholders})"
        return self.execute_query(query, image_ids)
    
    def text_search(self, text_query: str, search_targets: List[str] = ["title", "description", "image"],
                   filters: Dict[str, Any] = None, limit: int = 20, offset: int = 0,
                   weights: Optional[Dict[str, float]] = None, min_score: Optional[float] = None) -> List[Dict[str, Any]]:
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
            offset=offset,
            weights=weights,
            min_score=min_score
        )

    def unified_search(self, query_type: str, query_content: str,
                      search_targets: List[str] = ["title", "description", "image"],
                      filters: Dict[str, Any] = None, limit: int = 20, offset: int = 0,
                      weights: Optional[Dict[str, float]] = None, min_score: Optional[float] = None) -> List[Dict[str, Any]]:
        """统一搜索入口。

        当前 text/image 入口沿用原有 encode + _multi_vector_search 逻辑；如需权重应用到文本/图像入口可改造为直接在此分支调用 _multi_vector_search。
        """
        if query_type == "text":
            return self.text_search(query_content, self._sanitize_targets(search_targets), filters, limit, offset, weights=weights, min_score=min_score)
        if query_type == "image":
            return self.image_search(query_content, search_targets, filters, limit, offset, weights=weights, min_score=min_score)
        raise ValueError(f"不支持的查询类型: {query_type}，支持的类型：'text', 'image'")

    def vector_search_direct(self, query_embedding: list, search_targets: List[str] = ["title", "description", "image"],
                           filters: Dict[str, Any] = None, limit: int = 20, offset: int = 0,
                           weights: Optional[Dict[str, float]] = None, min_score: Optional[float] = None) -> List[Dict[str, Any]]:
        return self._multi_vector_search(
            query_embedding=query_embedding,
            search_targets=search_targets,
            filters=filters,
            limit=limit,
            offset=offset,
            weights=weights,
            min_score=min_score
        )

    def _multi_vector_search(self, query_embedding: list, search_targets: List[str],
                           filters: Dict[str, Any] = None, limit: int = 20, offset: int = 0,
                           weights: Optional[Dict[str, float]] = None, min_score: Optional[float] = None) -> List[Dict[str, Any]]:
        search_targets = self._sanitize_targets(search_targets)
        filtered_ids = self.get_filtered_image_ids(filters or {})
        if not filtered_ids:
            return []

        # 单目标：直接距离排序（SQL 保序）
        if len(search_targets) == 1:
            vector_results = self._vector_search_with_filter(search_targets[0], query_embedding, filtered_ids, limit + offset)
            if not vector_results:
                return []
            paginated = vector_results[offset:offset + limit]
            ids = [r[0] for r in paginated]
            if not ids:
                return []
            placeholders = ','.join(['?'] * len(ids))
            order_case = 'CASE id ' + ' '.join(f"WHEN ? THEN {idx}" for idx, _ in enumerate(paginated)) + ' END'
            sql = f"SELECT * FROM images WHERE id IN ({placeholders}) ORDER BY {order_case}"
            params = ids + ids
            images = self.execute_query(sql, params)
            id2score = {iid: 1 - dist for iid, dist in paginated}
            id2dist = {iid: dist for iid, dist in paginated}
            out = []
            for img in images:
                score = id2score.get(img['id'], 0.0)
                if min_score is not None and score < min_score:
                    continue
                img['score'] = score
                img['distance'] = id2dist.get(img['id'])
                out.append(img)
            return self._attach_public_url(out)

        # 多目标：收集每个目标的分数再加权融合
        weights = weights or {}
        norm_weights: Dict[str, float] = {}
        total_w = 0.0
        for t in search_targets:
            w = float(weights.get(t, 1.0))
            if w > 0:
                norm_weights[t] = w
                total_w += w
        if not norm_weights:
            norm_weights = {t: 1.0 for t in search_targets}
            total_w = float(len(search_targets))

        per_target_scores: Dict[str, Dict[int, float]] = {}
        candidate_ids: set[int] = set()
        fetch_k = limit * 2
        for target in search_targets:
            vres = self._vector_search_with_filter(target, query_embedding, filtered_ids, fetch_k)
            target_map: Dict[int, float] = {}
            for iid, dist in vres:
                score = 1 - dist
                target_map[iid] = max(target_map.get(iid, 0.0), score)
                candidate_ids.add(iid)
            per_target_scores[target] = target_map

        scored: List[Tuple[int, float]] = []
        for iid in candidate_ids:
            weighted_sum = 0.0
            weight_sum = 0.0
            for t, w in norm_weights.items():
                s = per_target_scores.get(t, {}).get(iid)
                if s is not None:
                    weighted_sum += s * w
                    weight_sum += w
            if weight_sum == 0:
                continue
            final_score = weighted_sum / weight_sum
            if min_score is not None and final_score < min_score:
                continue
            scored.append((iid, final_score))

        if not scored:
            return []

        scored.sort(key=lambda x: x[1], reverse=True)
        page = scored[offset:offset + limit]
        if not page:
            return []
        ids = [i for i, _ in page]
        images = self._get_images_by_ids(ids)
        id2score = {i: s for i, s in page}
        # 取最小 distance 作为参考
        min_dist_ref: Dict[int, float] = {}
        for tmap in per_target_scores.values():
            for iid, s in tmap.items():
                dist = 1 - s
                if iid not in min_dist_ref or dist < min_dist_ref[iid]:
                    min_dist_ref[iid] = dist
        for img in images:
            img['score'] = id2score.get(img['id'], 0.0)
            img['distance'] = min_dist_ref.get(img['id'])
        images.sort(key=lambda x: x['score'], reverse=True)
        return self._attach_public_url(images)
    
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
            results = self._attach_public_url(results)
            logger.info(f"使用图像ID {image_id} 的 {vector_type} 向量找到 {len(results)} 个相似结果")
            return results
            
        except Exception as e:
            logger.error(f"向量搜索失败: {str(e)}")
            return []

    # =============== 辅助：统一附加 public_url ===============
    def _attach_public_url(self, images: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        for img in images:
            if not img.get('public_url'):
                fp = img.get('filepath') or ''
                if fp:
                    img['public_url'] = build_public_url(fp)
        return images

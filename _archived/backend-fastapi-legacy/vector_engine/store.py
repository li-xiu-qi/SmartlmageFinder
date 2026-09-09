"""
SQLite-vec 向量存储实现

将原 vectors.py 的 vec0 虚表操作 + 检索语法封装为 VectorStore。
扩展加载失败时 is_available() 返回 False，不抛 SystemExit。
"""
import json
import traceback
from typing import Any, Dict, List, Optional

import numpy as np

from .base import VectorStore


class SqliteVecStore(VectorStore):
    """基于 sqlite-vec 的向量存储"""

    VECTOR_TYPES = ("title", "description", "image")

    def __init__(self):
        self._driver_path: Optional[str] = None
        self._driver_error: str = ""
        self._driver_resolved = False

    def _resolve_driver(self) -> Optional[str]:
        if self._driver_resolved:
            return self._driver_path
        self._driver_resolved = True
        try:
            from ..config import settings
            from ..config.platform_detector import PlatformDetector
            import os

            config = settings.get_config()
            driver_dir = getattr(config, "VECTOR_DB_DRIVER_DIR", None)
            if not driver_dir:
                self._driver_error = "VECTOR_DB_DRIVER_DIR 未配置"
                return None
            project_root = __import__("os").path.dirname(
                __import__("os").path.dirname(
                    __import__("os").path.dirname(
                        __import__("os").path.dirname(__import__("os").path.abspath(__file__))
                    )
                )
            )
            rel = driver_dir.lstrip("./").lstrip(".\\")
            abs_dir = __import__("os").path.normpath(__import__("os").path.join(project_root, rel))
            self._driver_path = PlatformDetector.get_driver_path(abs_dir)
            if not self._driver_path:
                self._driver_error = "未找到适用于当前平台的驱动"
            return self._driver_path
        except Exception as e:
            self._driver_error = f"驱动解析失败: {e}"
            return None

    def _ensure_extension(self, connection) -> bool:
        """确保连接已加载 sqlite-vec 扩展"""
        driver = self._resolve_driver()
        if not driver:
            return False
        try:
            # 已加载则跳过
            try:
                cur = connection.cursor()
                cur.execute("SELECT vec_version()")
                row = cur.fetchone()
                if row:
                    return True
            except Exception:
                pass
            import os
            if not os.path.exists(driver):
                return False
            connection.enable_load_extension(True)
            connection.execute(f"SELECT load_extension('{driver}')")
            return True
        except Exception as e:
            self._driver_error = f"扩展加载失败: {e}"
            return False

    def is_available(self) -> bool:
        driver = self._resolve_driver()
        return driver is not None and __import__("os").path.exists(driver)

    def unavailable_reason(self) -> str:
        return self._driver_error

    def create_tables(self, connection, dimension: int) -> bool:
        """创建 vec0 虚拟表"""
        if not self._ensure_extension(connection):
            print(f"警告: sqlite-vec 扩展不可用，跳过向量表创建。原因: {self._driver_error}")
            return False
        try:
            for vtype in self.VECTOR_TYPES:
                table = f"{vtype}_vectors"
                connection.execute(f"""
                    CREATE VIRTUAL TABLE IF NOT EXISTS {table} USING vec0(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        image_id INTEGER UNIQUE NOT NULL,
                        embedding FLOAT[{dimension}] DISTANCE_METRIC=cosine
                    );
                """)
            print(f"向量表创建成功，维度: {dimension}")
            return True
        except Exception as e:
            print(f"向量表创建失败: {e}")
            return False

    def add(self, connection, image_id: int, vector_type: str, vector: np.ndarray) -> bool:
        if vector_type not in self.VECTOR_TYPES:
            raise ValueError(f"vector_type 必须是 {self.VECTOR_TYPES}")
        if not self._ensure_extension(connection):
            return False
        try:
            vector_json = json.dumps(vector.tolist())
            table = f"{vector_type}_vectors"
            cursor = connection.cursor()
            cursor.execute(f"SELECT id FROM {table} WHERE image_id = ?", (image_id,))
            if cursor.fetchone():
                cursor.execute(
                    f"UPDATE {table} SET embedding = vec_f32(?) WHERE image_id = ?",
                    (vector_json, image_id),
                )
            else:
                cursor.execute(
                    f"INSERT INTO {table}(image_id, embedding) VALUES (?, vec_f32(?))",
                    (image_id, vector_json),
                )
            connection.commit()
            return True
        except Exception as e:
            print(f"向量写入失败 [{vector_type}] image_id={image_id}: {e}")
            return False

    def search(
        self,
        connection,
        query_vector: List[float],
        vector_type: str,
        limit: int = 20,
        offset: int = 0,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        if vector_type not in self.VECTOR_TYPES:
            raise ValueError(f"vector_type 必须是 {self.VECTOR_TYPES}")
        if not self._ensure_extension(connection):
            return []
        try:
            query_json = json.dumps(query_vector)
            table = f"{vector_type}_vectors"
            sql = f"""
                SELECT
                    vec.image_id,
                    (1 - vec.distance) AS score
                FROM
                    {table} AS vec
                WHERE
                    vec.embedding MATCH '{query_json}'
                    AND k = {limit + offset}
                ORDER BY score DESC
                LIMIT {limit} OFFSET {offset}
            """
            cursor = connection.cursor()
            cursor.execute(sql)
            return [dict(row) if hasattr(row, "keys") else {"image_id": row[0], "score": row[1]}
                    for row in cursor.fetchall()]
        except Exception as e:
            print(f"向量搜索失败 [{vector_type}]: {e}")
            return []

    def multi_search(
        self,
        connection,
        query_vector: List[float],
        search_targets: List[str],
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 20,
        offset: int = 0,
        exclude_image_id: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """多目标检索，复用原 search_func 逻辑"""
        try:
            from ..db_func.search_func.multi_vector_search import _vector_search
            return _vector_search(
                conn=connection,
                query_embedding=query_vector,
                search_targets=search_targets,
                filters=filters,
                limit=limit,
                offset=offset,
                exclude_image_id=exclude_image_id,
            )
        except Exception as e:
            print(f"多向量搜索失败: {e}")
            traceback.print_exc()
            return []

    def delete(self, connection, image_id: int) -> bool:
        if not self._ensure_extension(connection):
            return False
        try:
            for vtype in self.VECTOR_TYPES:
                connection.execute(
                    f"DELETE FROM {vtype}_vectors WHERE image_id = ?", (image_id,)
                )
            connection.commit()
            return True
        except Exception as e:
            print(f"向量删除失败: {e}")
            return False

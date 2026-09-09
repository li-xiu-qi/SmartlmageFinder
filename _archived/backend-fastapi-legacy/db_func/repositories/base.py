"""
数据仓库基类，提供通用的数据库操作模式
"""
import sqlite3
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from contextlib import contextmanager

from ..core.connection import get_db_connection_from_pool, get_db_connection
from ..utils.common import row_to_dict, rows_to_dicts


class BaseRepository(ABC):
    """基础数据仓库类

    支持两种使用方式:
    1. 无参构造: 每次操作自动从连接池 / 单连接获取连接
    2. 传入外部已打开的 sqlite3.Connection: 复用该连接（不负责关闭）
    """

    def __init__(self, conn: sqlite3.Connection | None = None):
        self._external_conn = conn  # 外部提供的连接（可选）
    
    @contextmanager
    def get_connection(self):
        """获取数据库连接

        优先复用构造时传入的连接；否则使用连接池 / 单连接。
        当复用外部连接时不负责关闭。"""
        if self._external_conn is not None:
            # 直接复用外部连接
            yield self._external_conn
            return
        try:
            with get_db_connection_from_pool() as conn:
                yield conn
        except RuntimeError:
            with get_db_connection() as conn:
                yield conn
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """
        执行查询并返回结果列表
        
        Args:
            query: SQL查询语句
            params: 查询参数
            
        Returns:
            查询结果列表
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return rows_to_dicts(rows)
    
    def execute_query_one(self, query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        """
        执行查询并返回单个结果
        
        Args:
            query: SQL查询语句
            params: 查询参数
            
        Returns:
            单个查询结果或None
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            row = cursor.fetchone()
            return row_to_dict(row) if row else None
    
    def execute_insert(self, query: str, params: tuple = ()) -> int:
        """
        执行插入操作并返回新记录的ID
        
        Args:
            query: SQL插入语句
            params: 插入参数
            
        Returns:
            新插入记录的ID
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.lastrowid
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """
        执行更新操作并返回受影响的行数
        
        Args:
            query: SQL更新语句
            params: 更新参数
            
        Returns:
            受影响的行数
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount
    
    def execute_delete(self, query: str, params: tuple = ()) -> int:
        """
        执行删除操作并返回受影响的行数
        
        Args:
            query: SQL删除语句
            params: 删除参数
            
        Returns:
            受影响的行数
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount
    
    def execute_batch(self, queries: List[tuple]) -> None:
        """
        批量执行SQL语句（事务）
        
        Args:
            queries: SQL语句和参数的列表，格式为 [(query, params), ...]
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                for query, params in queries:
                    cursor.execute(query, params)
                conn.commit()
            except Exception as e:
                conn.rollback()
                raise e

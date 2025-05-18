"""
数据库连接池实现，提供线程安全的数据库连接管理
"""
import sqlite3
import threading
import queue
from typing import Dict, List, Any, Optional
from contextlib import contextmanager

# 导入配置模块
from ..config import settings

class DatabaseConnectionPool:
    """SQLite数据库连接池，提供线程安全的连接管理"""
    
    def __init__(self, database_path: str, max_connections: int = 10):
        """
        初始化数据库连接池
        
        Args:
            database_path: 数据库文件路径
            max_connections: 最大连接数，默认为10
        """
        self.database_path = database_path
        self.max_connections = max_connections
        self.connections = queue.Queue(maxsize=max_connections)
        self.connection_count = 0
        self._lock = threading.Lock()
    def _create_connection(self) -> sqlite3.Connection:
        """创建新的数据库连接"""
        connection = sqlite3.connect(self.database_path, check_same_thread=False)
        connection.row_factory = sqlite3.Row
        
        # 在创建连接时就加载向量扩展
        try:
            connection.enable_load_extension(True)
            connection.execute(f"SELECT load_extension('{settings.get_config().VECTOR_DB_DRIVER}')")
            # 验证扩展是否正确加载
            cursor = connection.cursor()
            cursor.execute("SELECT vec_version()")
            result = cursor.fetchone()
            version = result[0] if result else "未知"
            print(f"连接创建，成功加载sqlite-vec扩展，版本: {version}")
        except Exception as e:
            print(f"连接创建时加载向量扩展失败: {e}")
        
        return connection
    
    def get_connection(self) -> sqlite3.Connection:
        """
        从连接池获取一个连接
        如果池中有可用连接，则返回已有连接
        如果池中无可用连接且未达到最大连接数，则创建新连接
        如果池已满，则等待连接可用
        """
        try:
            # 尝试从连接池获取连接
            return self.connections.get(block=False)
        except queue.Empty:
            # 连接池为空，创建新连接（如果未达到最大连接数）
            with self._lock:
                if self.connection_count < self.max_connections:
                    self.connection_count += 1
                    return self._create_connection()
                # 已达到最大连接数，等待连接可用
                return self.connections.get()
    
    def release_connection(self, connection: sqlite3.Connection):
        """将连接归还到连接池"""
        self.connections.put(connection)
    
    def close_all(self):
        """关闭所有连接"""
        while not self.connections.empty():
            conn = self.connections.get()
            conn.close()
        with self._lock:
            self.connection_count = 0

# 单例模式，确保整个应用只有一个连接池实例
_connection_pool: Optional[DatabaseConnectionPool] = None

def initialize_connection_pool(database_path: str, max_connections: int = 10):
    """初始化连接池"""
    global _connection_pool
    if _connection_pool is None:
        _connection_pool = DatabaseConnectionPool(database_path, max_connections)
    return _connection_pool

def get_connection_pool() -> DatabaseConnectionPool:
    """获取连接池实例"""
    global _connection_pool
    if _connection_pool is None:
        raise RuntimeError("Connection pool not initialized. Call initialize_connection_pool first.")
    return _connection_pool

@contextmanager
def get_db_connection_from_pool():
    """从连接池获取数据库连接的上下文管理器"""
    pool = get_connection_pool()
    conn = pool.get_connection()
    try:
        yield conn
    finally:
        pool.release_connection(conn)

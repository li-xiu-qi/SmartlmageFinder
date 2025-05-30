"""
SQLite向量扩展加载器
统一管理向量扩展的加载和验证逻辑，避免重复代码
"""
import sqlite3
from typing import Optional, Tuple
from ..config import settings


class VectorExtensionLoader:
    """向量扩展加载器，提供统一的加载和验证接口"""
    
    @staticmethod
    def load_extension(connection: sqlite3.Connection, silent: bool = False) -> Tuple[bool, Optional[str]]:
        """
        为数据库连接加载向量扩展
        
        Args:
            connection: SQLite数据库连接
            silent: 是否静默模式（不打印日志）
            
        Returns:
            tuple: (是否成功, 版本信息或错误信息)
        """
        try:
            # 启用扩展加载
            connection.enable_load_extension(True)
            
            # 加载向量扩展
            extension_path = settings.get_config().VECTOR_DB_DRIVER
            connection.execute(f"SELECT load_extension('{extension_path}')")
            
            # 验证扩展是否正确加载
            cursor = connection.cursor()
            cursor.execute("SELECT vec_version()")
            result = cursor.fetchone()
            version = result[0] if result else "未知"
            
            if not silent:
                print(f"成功加载sqlite-vec扩展，版本: {version}")
            
            return True, version
            
        except Exception as e:
            error_msg = f"加载sqlite-vec扩展失败: {e}"
            if not silent:
                print(error_msg)
                print("无法使用向量功能，请确保扩展文件存在并可访问")
                print(f"扩展文件路径: {settings.get_config().VECTOR_DB_DRIVER}")
            
            return False, str(e)
    
    @staticmethod
    def verify_extension(connection: sqlite3.Connection) -> Tuple[bool, Optional[str]]:
        """
        验证向量扩展是否已加载
        
        Args:
            connection: SQLite数据库连接
            
        Returns:
            tuple: (是否已加载, 版本信息或错误信息)
        """
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT vec_version()")
            result = cursor.fetchone()
            version = result[0] if result else "未知"
            return True, version
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def setup_connection_with_extension(connection: sqlite3.Connection, silent: bool = False) -> bool:
        """
        为连接设置向量扩展和优化配置
        
        Args:
            connection: SQLite数据库连接
            silent: 是否静默模式
            
        Returns:
            bool: 是否成功设置
        """
        try:
            # 设置基本的SQLite优化配置
            connection.execute("PRAGMA journal_mode=WAL")
            connection.execute("PRAGMA synchronous=NORMAL")
            connection.execute("PRAGMA cache_size=1000")
            connection.execute("PRAGMA temp_store=memory")
            
            # 加载向量扩展
            success, info = VectorExtensionLoader.load_extension(connection, silent)
            
            return success
            
        except Exception as e:
            if not silent:
                print(f"设置数据库连接失败: {e}")
            return False


# 提供便捷的全局函数
def load_vector_extension(connection: sqlite3.Connection, silent: bool = False) -> Tuple[bool, Optional[str]]:
    """
    全局函数：为数据库连接加载向量扩展
    
    Args:
        connection: SQLite数据库连接
        silent: 是否静默模式
        
    Returns:
        tuple: (是否成功, 版本信息或错误信息)
    """
    return VectorExtensionLoader.load_extension(connection, silent)


def verify_vector_extension(connection: sqlite3.Connection) -> Tuple[bool, Optional[str]]:
    """
    全局函数：验证向量扩展是否已加载
    
    Args:
        connection: SQLite数据库连接
        
    Returns:
        tuple: (是否已加载, 版本信息或错误信息)
    """
    return VectorExtensionLoader.verify_extension(connection)


def setup_connection(connection: sqlite3.Connection, silent: bool = False) -> bool:
    """
    全局函数：为连接设置向量扩展和优化配置
    
    Args:
        connection: SQLite数据库连接
        silent: 是否静默模式
        
    Returns:
        bool: 是否成功设置
    """
    return VectorExtensionLoader.setup_connection_with_extension(connection, silent)
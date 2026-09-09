"""简化版本: 仅使用配置指定的 VECTOR_DB_DRIVER 路径加载 sqlite-vec。
失败即退出 (SystemExit)。不做平台扫描/回退。
"""
import sqlite3
import os
from typing import Optional, Tuple

from ....config import settings
from ....config.platform_detector import PlatformDetector


class VectorExtensionLoader:
    """极简加载器: 只信任 settings.get_config().VECTOR_DB_DRIVER。"""
    
    @staticmethod
    def load_extension(connection: sqlite3.Connection, silent: bool = False) -> Tuple[bool, Optional[str]]:
        """
        为数据库连接加载向量扩展（非致命：失败返回 False + 错误信息）
        
        Args:
            connection: SQLite数据库连接
            silent: 是否静默模式（不打印日志）
            
        Returns:
            tuple: (是否成功, 版本信息或错误信息)
        """
        try:
            # 如果已经可以调用 vec_version 直接返回成功，避免重复加载产生二次初始化错误
            try:
                cursor = connection.cursor()
                cursor.execute("SELECT vec_version()")
                row = cursor.fetchone()
                if row:
                    if not silent:
                        print(f"sqlite-vec 已加载，版本: {row[0]} ")
                    return True, row[0]
            except Exception:
                pass  # 继续尝试真正加载
            config = settings.get_config()
            driver_path = getattr(config, 'VECTOR_DB_DRIVER', None)
            if not driver_path:
                msg = "未配置 VECTOR_DB_DRIVER，向量功能不可用"
                if not silent:
                    print(f"警告: {msg}")
                return False, msg
            if not os.path.exists(driver_path):
                msg = f"驱动文件不存在: {driver_path}"
                if not silent:
                    print(f"警告: {msg}")
                return False, msg
            if not silent:
                print(f"使用配置中的 VECTOR_DB_DRIVER: {driver_path}")

            # 启用扩展加载
            connection.enable_load_extension(True)
            connection.execute(f"SELECT load_extension('{driver_path}')")

            # 验证扩展是否正确加载
            cursor = connection.cursor()
            cursor.execute("SELECT vec_version()")
            result = cursor.fetchone()
            version = result[0] if result else "未知"

            if not silent:
                platform_info = PlatformDetector.detect_platform()
                print(f"成功加载sqlite-vec扩展，版本: {version} (平台: {platform_info})")

            return True, version
        except Exception as e:
            error_msg = f"加载sqlite-vec扩展失败: {e}"
            if not silent:
                print(f"警告: {error_msg}（向量功能将不可用）")
            return False, error_msg
    
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

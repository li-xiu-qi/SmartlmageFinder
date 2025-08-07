"""
SQLite向量扩展加载器
统一管理向量扩展的加载和验证逻辑，避免重复代码
支持多平台自动检测和驱动设置
"""
import sqlite3
import os
from typing import Optional, Tuple

from ....config import settings
from ....config.platform_detector import auto_setup_driver, PlatformDetector


class VectorExtensionLoader:
    """向量扩展加载器，提供统一的加载和验证接口"""
    
    @staticmethod
    def _ensure_driver_available() -> Tuple[bool, Optional[str]]:
        """
        确保当前平台的数据库驱动可用
        从配置的驱动目录中自动选择适合当前平台的驱动文件
        
        Returns:
            tuple: (是否成功, 驱动文件路径)
        """
        config = settings.get_config()
        driver_dir = config.VECTOR_DB_DRIVER_DIR
        
        if not driver_dir:
            error_msg = "配置中未指定VECTOR_DB_DRIVER_DIR"
            print(error_msg)
            return False, None
        
        # 获取当前平台对应的驱动文件路径
        driver_path = PlatformDetector.get_driver_path(driver_dir)
        
        if driver_path and os.path.exists(driver_path):
            print(f"找到适合当前平台的驱动文件: {driver_path}")
            return True, driver_path
        else:
            print(f"未找到适合当前平台的驱动文件")
            print(f"驱动目录: {driver_dir}")
            print(f"当前平台: {PlatformDetector.detect_platform()}")
            print(f"期望的驱动文件: {PlatformDetector.get_extension_filename()}")
            
            # 列出驱动目录中的内容以帮助调试
            if os.path.exists(driver_dir):
                print("驱动目录中的内容:")
                for item in os.listdir(driver_dir):
                    item_path = os.path.join(driver_dir, item)
                    if os.path.isdir(item_path):
                        print(f"  目录: {item}/")
                        try:
                            sub_items = os.listdir(item_path)
                            for sub_item in sub_items:
                                print(f"    {sub_item}")
                        except:
                            pass
                    else:
                        print(f"  文件: {item}")
            
            return False, None
    
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
            # 确保驱动可用
            driver_success, driver_path = VectorExtensionLoader._ensure_driver_available()
            if not driver_success:
                error_msg = "无法找到或设置适合当前平台的数据库驱动"
                if not silent:
                    print(error_msg)
                    print("请检查驱动文件是否存在于 backend/config_files/vector_db_driver/ 目录中")
                return False, error_msg
              
            # 启用扩展加载
            connection.enable_load_extension(True)
            
            # 加载向量扩展
            extension_path = driver_path
            connection.execute(f"SELECT load_extension('{extension_path}')")
            
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
                print(error_msg)
                print("无法使用向量功能，请确保扩展文件存在并可访问")
                print("当前平台信息:")
                platform_info = PlatformDetector.get_platform_info()
                for key, value in platform_info.items():
                    print(f"  {key}: {value}")
            
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

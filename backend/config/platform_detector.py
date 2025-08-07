"""
跨平台数据库驱动检测器
自动检测当前运行平台并选择合适的sqlite-vec扩展
"""
import os
import platform
from typing import Optional, Dict, Tuple
from pathlib import Path


# 全局变量，用于缓存检测到的平台信息，避免重复检测
_cached_platform_key: Optional[str] = None


class PlatformDetector:
    """平台检测器，用于识别当前运行环境并选择合适的数据库驱动"""
    
    # 平台到驱动目录的映射
    PLATFORM_DRIVER_DIR_MAP = {
        'windows_x86_64': 'sqlite-vec-0.1.6-loadable-windows-x86_64',
        'linux_x86_64': 'sqlite-vec-0.1.6-loadable-linux-x86_64',
        'linux_aarch64': 'sqlite-vec-0.1.6-loadable-linux-aarch64',
        'macos_x86_64': 'sqlite-vec-0.1.6-loadable-macos-x86_64',
        'macos_aarch64': 'sqlite-vec-0.1.6-loadable-macos-aarch64',
    }
    
    # 不同平台的扩展文件名
    PLATFORM_EXTENSION_MAP = {
        'windows_x86_64': 'vec0.dll',
        'linux_x86_64': 'vec0.so',
        'linux_aarch64': 'vec0.so',
        'macos_x86_64': 'vec0.dylib',
        'macos_aarch64': 'vec0.dylib',
    }

    @staticmethod
    def detect_platform() -> str:
        """
        检测当前运行平台
        
        Returns:
            str: 平台标识符，格式为 '{system}_{architecture}'
        """
        global _cached_platform_key
        
        # 如果已经检测过了，直接返回缓存的结果
        if _cached_platform_key is not None:
            return _cached_platform_key
        
        system = platform.system().lower()
        machine = platform.machine().lower()
        
        # 标准化架构名称
        if machine in ['x86_64', 'amd64']:
            arch = 'x86_64'
        elif machine in ['aarch64', 'arm64']:
            arch = 'aarch64'
        else:
            # 对于其他架构，尝试使用x86_64作为fallback
            arch = 'x86_64'
            print(f"警告: 未识别的架构 {machine}，将尝试使用 x86_64")
        
        # 标准化系统名称
        if system == 'darwin':
            system = 'macos'
        elif system not in ['windows', 'linux', 'macos']:
            print(f"警告: 未识别的系统 {system}，将尝试使用 linux")
            system = 'linux'
        
        platform_key = f"{system}_{arch}"
        print(f"检测到平台: {platform_key} (系统: {platform.system()}, 架构: {platform.machine()})")
        
        # 缓存检测结果
        _cached_platform_key = platform_key
        
        return platform_key

    @classmethod
    def get_driver_path(cls, driver_dir: str) -> Optional[str]:
        """
        获取当前平台对应的驱动文件路径
        
        Args:
            driver_dir: 驱动文件根目录
            
        Returns:
            Optional[str]: 驱动文件的完整路径，如果不存在则返回None
        """
        platform_key = cls.detect_platform()
        
        if platform_key not in cls.PLATFORM_DRIVER_DIR_MAP:
            print(f"错误: 不支持的平台 {platform_key}")
            return None
        
        # 构建驱动文件路径
        platform_dir = cls.PLATFORM_DRIVER_DIR_MAP[platform_key]
        extension_filename = cls.get_extension_filename()
        
        driver_path = os.path.join(driver_dir, platform_dir, extension_filename)
        
        if os.path.exists(driver_path):
            print(f"找到平台驱动文件: {driver_path}")
            return driver_path
        else:
            print(f"平台驱动文件不存在: {driver_path}")
            # 列出可用的驱动文件以帮助调试
            if os.path.exists(os.path.join(driver_dir, platform_dir)):
                available_files = os.listdir(os.path.join(driver_dir, platform_dir))
                print(f"该平台目录中可用的文件: {available_files}")
            return None

    @classmethod
    def get_extension_filename(cls) -> str:
        """
        获取当前平台的扩展文件名
        
        Returns:
            str: 扩展文件名 (如 vec0.dll, vec0.so, vec0.dylib)
        """
        platform_key = cls.detect_platform()
        return cls.PLATFORM_EXTENSION_MAP.get(platform_key, 'vec0.so')
    
    @classmethod
    def get_platform_info(cls) -> Dict[str, str]:
        """
        获取当前平台的详细信息
        
        Returns:
            Dict[str, str]: 包含平台信息的字典
        """
        return {
            'system': platform.system(),
            'machine': platform.machine(),
            'platform': platform.platform(),
            'python_version': platform.python_version(),
            'detected_key': cls.detect_platform(),
            'extension_filename': cls.get_extension_filename()
        }
    
    @classmethod
    def clear_platform_cache(cls) -> None:
        """
        清除平台检测缓存
        主要用于测试场景，正常使用中不需要调用此方法
        """
        global _cached_platform_key
        _cached_platform_key = None


def auto_setup_driver(driver_dir: str, force_extract: bool = False) -> Tuple[bool, Optional[str]]:
    """
    自动设置数据库驱动
    
    Args:
        driver_dir: 驱动文件目录
        force_extract: 保留参数以兼容现有代码，但在新版本中不使用
        
    Returns:
        Tuple[bool, Optional[str]]: (是否成功, 驱动文件路径)
    """
    try:
        # 确保驱动目录存在
        os.makedirs(driver_dir, exist_ok=True)
        
        # 直接从解压目录获取驱动文件
        driver_path = PlatformDetector.get_driver_path(driver_dir)
        
        if driver_path and os.path.exists(driver_path):
            print(f"数据库驱动自动设置成功: {driver_path}")
            return True, driver_path
        else:
            print("数据库驱动自动设置失败")
            print(f"请确保已将适合当前平台的驱动文件放置在正确的子目录中")
            return False, None
            
    except Exception as e:
        print(f"自动设置数据库驱动时发生错误: {e}")
        return False, None

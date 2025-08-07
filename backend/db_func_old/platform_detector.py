"""
跨平台数据库驱动检测器
自动检测当前运行平台并选择合适的sqlite-vec扩展
"""
import os
import platform
import tarfile
import shutil
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
        """    @staticmethod
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


if __name__ == "__main__":
    print("=" * 40)
    print("数据库驱动平台检测与自动设置测试")
    print("=" * 40)
    print("此脚本用于测试当前平台是否能被正确检测，")
    print("以及是否能根据检测到的平台找到对应的数据库驱动文件。")
    print("-" * 40)

    print("\\n=== 1. 平台详细信息 ===")
    platform_info = PlatformDetector.get_platform_info()
    for key, value in platform_info.items():
        print(f"  {key}: {value}")
    
    print("\\n=== 2. 驱动自动设置测试 ===")
    
    # 构建到 vector_db_driver 目录的绝对路径
    # __file__ 是 platform_detector.py 的路径
    # Path(__file__).resolve().parent 是 backend/db_func 目录的绝对路径
    # Path(__file__).resolve().parent.parent 是 backend 目录的绝对路径
    # Path(__file__).resolve().parent.parent.parent 是项目根目录 (SmartImageFinder)
    project_root = Path(__file__).resolve().parent.parent.parent
    # VECTOR_DB_DRIVER_DIR 在 config.yaml 中通常定义为类似 ./backend/config_files/vector_db_driver
    # 这里我们直接构建到该目录的路径
    test_driver_root_dir = project_root / "backend" / "config_files" / "vector_db_driver"
    
    print(f"\\n目标驱动根目录 (config.yaml 中的 VECTOR_DB_DRIVER_DIR 应指向此处):")
    print(f"  路径: {test_driver_root_dir}")

    if not test_driver_root_dir.exists() or not test_driver_root_dir.is_dir():
        print(f"\\n错误: 目标驱动根目录不存在或不是一个目录:")
        print(f"  '{test_driver_root_dir}'")
        print("请确保 'backend/config_files/vector_db_driver' 目录存在，并且其中包含各平台驱动的子目录。")
    else:
        print(f"  目录状态: 存在且为目录。")
        print("\\n开始调用 auto_setup_driver 进行测试...")
        
        # auto_setup_driver 需要字符串路径
        success, driver_path_found = auto_setup_driver(str(test_driver_root_dir))
        
        print(f"\\n--- 驱动自动设置测试结果 ---")
        if success and driver_path_found:
            print(f"  状态: 成功")
            print(f"  找到并确认的驱动路径: {driver_path_found}")
            print(f"  驱动文件是否存在: {'是' if os.path.exists(driver_path_found) else '否 (这不应该发生如果成功)'}")
        else:
            print(f"  状态: 失败")
            print(f"  未能自动找到或设置驱动。")
            if driver_path_found: # auto_setup_driver 可能返回路径即使 success 为 False
                 print(f"  尝试的驱动路径 (可能未找到或无效): {driver_path_found}")
            print(f"  请检查以上日志中的平台检测信息、期望的驱动文件名以及在目标驱动根目录下的实际文件结构。")
            print(f"  确保 '{PlatformDetector.get_extension_filename()}' 文件存在于 '{test_driver_root_dir / PlatformDetector.PLATFORM_DRIVER_DIR_MAP.get(PlatformDetector.detect_platform(), 'unknown_platform_dir')}'")

    print("\\n" + "=" * 40)
    print("测试结束。请检查输出以确认平台和驱动是否正确。")
    print("=" * 40)

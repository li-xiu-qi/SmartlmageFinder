#!/usr/bin/env python3
"""
SmartImageFinder 环境检查模块
提供环境状态检查功能
"""

import os
import sys
import yaml
from pathlib import Path


def is_environment_ready():
    """检查环境是否已初始化"""
    base_path = Path(__file__).parent.parent.absolute()
    marker_file = base_path / ".env_ready"
    return marker_file.exists()


def check_config_file():
    """检查配置文件"""
    base_path = Path(__file__).parent.parent.absolute()
    # 配置文件实际位于 backend/config/files/config.yaml
    config_file = base_path / "backend" / "config" / "files" / "config.yaml"
    return config_file.exists()


def check_model_exists():
    """检查模型是否存在"""
    base_path = Path(__file__).parent.parent.absolute()
    # 与 check_config_file 保持一致的真实路径
    config_file = base_path / "backend" / "config" / "files" / "config.yaml"
    if not config_file.exists():
        return False
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            model_path = config.get('MODEL_PATH', '')
            
            if not model_path:
                return False
            
            # 检查绝对路径或相对路径
            if os.path.isabs(model_path):
                return os.path.exists(model_path)
            else:
                full_path = base_path / model_path
                return full_path.exists()
    except Exception:
        return False


def check_python_version() -> bool:
    """检查Python版本"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✓ Python版本: {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ Python版本过低: {version.major}.{version.minor}.{version.micro} (需要 >= 3.8)")
        return False


def check_node_version() -> bool:
    """检查Node.js版本"""
    try:
        import subprocess
        result = subprocess.run(
            ["node", "--version"], 
            capture_output=True, 
            text=True, 
            shell=True
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✓ Node.js版本: {version}")
            return True
        else:
            print("❌ Node.js未安装或不在PATH中")
            return False
    except Exception:
        print("❌ Node.js未安装或不在PATH中")
        return False


def check_npm_version() -> bool:
    """检查npm版本"""
    try:
        import subprocess
        result = subprocess.run(
            ["npm", "--version"], 
            capture_output=True, 
            text=True, 
            shell=True
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✓ npm版本: {version}")
            return True
        else:
            print("❌ npm未安装或不在PATH中")
            return False
    except Exception:
        print("❌ npm未安装或不在PATH中")
        return False


def mark_environment_ready():
    """创建环境就绪标记"""
    base_path = Path(__file__).parent.parent.absolute()
    marker_file = base_path / ".env_ready"
    marker_file.touch()
    print(f"✓ 环境就绪标记已创建: {marker_file}")


def install_python_dependencies() -> bool:
    """安装Python依赖"""
    base_path = Path(__file__).parent.parent.absolute()
    requirements_file = base_path / "requirements.txt"
    
    if not requirements_file.exists():
        print("❌ requirements.txt文件不存在")
        return False
    
    print("📦 正在安装Python依赖...")
    try:
        import subprocess
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)],
            cwd=base_path,
            capture_output=True,
            text=True,
            shell=sys.platform == "win32"
        )
        if result.returncode == 0:
            print("✓ Python依赖安装成功")
            return True
        else:
            print(f"❌ Python依赖安装失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Python依赖安装失败: {e}")
        return False


def install_frontend_dependencies() -> bool:
    """安装前端依赖"""
    base_path = Path(__file__).parent.parent.absolute()
    frontend_dir = base_path / "frontend"
    package_json = frontend_dir / "package.json"
    
    if not package_json.exists():
        print("❌ frontend/package.json文件不存在")
        return False

    node_modules = frontend_dir / "node_modules"
    if node_modules.exists():
        print("✓ 前端依赖已安装")
        return True

    print("📦 正在安装前端依赖...")
    try:
        import subprocess
        result = subprocess.run(
            ["npm", "install"],
            cwd=frontend_dir,
            capture_output=True,
            text=True,
            shell=sys.platform == "win32"
        )
        if result.returncode == 0:
            print("✓ 前端依赖安装成功")
            return True
        else:
            print(f"❌ 前端依赖安装失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ 前端依赖安装失败: {e}")
        return False
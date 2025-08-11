#!/usr/bin/env python3
"""
SmartImageFinder 启动脚本模块
提供统一的启动入口
"""

import sys
import os
import subprocess
from pathlib import Path

def apply_start_config():
    """读取可选的 start_config.yaml 并设置相关环境变量，用于覆盖启动参数"""
    try:
        base_path = Path(__file__).parent.absolute()
        cfg_path = base_path / "start_config.yaml"
        if not cfg_path.exists():
            return
        import yaml
        with open(cfg_path, 'r', encoding='utf-8') as f:
            cfg = yaml.safe_load(f) or {}
        # 映射到环境变量（仅在未显式设置时覆盖）
        if cfg.get('backend_host') and not os.getenv('SIF_HOST'):
            os.environ['SIF_HOST'] = str(cfg['backend_host'])
        if cfg.get('backend_port') and not os.getenv('SIF_PORT'):
            os.environ['SIF_PORT'] = str(cfg['backend_port'])
        if cfg.get('reload') is not None and not os.getenv('SIF_RELOAD'):
            os.environ['SIF_RELOAD'] = '1' if bool(cfg['reload']) else '0'
        if cfg.get('frontend_port') and not os.getenv('SIF_FRONTEND_PORT'):
            os.environ['SIF_FRONTEND_PORT'] = str(cfg['frontend_port'])
        # 可选：后端代理源（供前端代理使用，如 http://localhost:10050）
        if cfg.get('backend_origin') and not os.getenv('SIF_BACKEND_ORIGIN'):
            os.environ['SIF_BACKEND_ORIGIN'] = str(cfg['backend_origin'])
    except Exception as e:
        print(f"⚠️ 读取 start_config.yaml 失败(忽略): {e}")


def main():
    """主函数"""
    if len(sys.argv) > 1 and sys.argv[1] == "init":
        # 运行环境初始化
        print("正在启动环境初始化...")
        subprocess.run([sys.executable, "scripts/init_environment.py"])
    else:
        # 启动前应用 start_config.yaml（如存在）
        apply_start_config()
        # 运行项目启动
        subprocess.run([sys.executable, "scripts/start_project.py"] + sys.argv[1:])


if __name__ == "__main__":
    main()
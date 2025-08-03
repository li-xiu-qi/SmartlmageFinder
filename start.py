#!/usr/bin/env python3
"""
SmartImageFinder 启动脚本模块
提供统一的启动入口
"""

import sys
import os
import subprocess
from pathlib import Path


def main():
    """主函数"""
    if len(sys.argv) > 1 and sys.argv[1] == "init":
        # 运行环境初始化
        print("正在启动环境初始化...")
        subprocess.run([sys.executable, "scripts/init_environment.py"])
    else:
        # 运行项目启动
        subprocess.run([sys.executable, "scripts/start_project.py"] + sys.argv[1:])


if __name__ == "__main__":
    main()
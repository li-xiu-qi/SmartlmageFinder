#!/usr/bin/env python3
"""
SmartImager 模型管理模块
负责模型下载和管理
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


def install_modelscope():
    """安装ModelScope依赖"""
    print("正在检查并安装ModelScope依赖...")
    try:
        import modelscope
        print("✓ ModelScope已安装")
        return True
    except ImportError:
        print("正在安装ModelScope...")
        os.system(f"{sys.executable} -m pip install modelscope")
        try:
            import modelscope
            print("✓ ModelScope安装成功")
            return True
        except ImportError:
            print("❌ ModelScope安装失败，请手动安装: pip install modelscope")
            return False


def merge_dirs(src_dir: str, dst_dir: str):
    """递归合并目录，只复制不存在的文件和子目录，保留现有文件"""
    if not os.path.isdir(src_dir):
        return
    os.makedirs(dst_dir, exist_ok=True)
    for item in os.listdir(src_dir):
        s = os.path.join(src_dir, item)
        d = os.path.join(dst_dir, item)
        if os.path.isdir(s):
            merge_dirs(s, d)
        else:
            # 仅复制不存在的文件，避免覆盖
            if not os.path.exists(d):
                shutil.copy2(s, d)


def download_model(model_name: str, cache_dir: str) -> str:
    """使用ModelScope下载模型"""
    try:
        from modelscope import snapshot_download

        print(f"正在下载模型 {model_name} 到 {cache_dir}...")
        print("注意: 首次下载可能需要一些时间，请耐心等待...")

        model_path = snapshot_download(
            model_name, cache_dir=cache_dir, revision="master"
        )

        # 确保返回绝对路径
        absolute_model_path = str(Path(model_path).absolute())
        print(f"✓ 模型下载成功，路径: {absolute_model_path}")

        # 同步本地 huggingface 缓存到全局 ~/.cache/huggingface
        local_hf = os.path.join(absolute_model_path, 'huggingface')
        sync_marker = os.path.join(absolute_model_path, 'huggingface_sync_done.txt')
        if os.path.isdir(local_hf):
            if os.path.exists(sync_marker):
                print("检测到已同步标记，跳过缓存同步")
            else:
                hf_cache = os.getenv('HF_HOME', os.path.join(os.path.expanduser('~'), '.cache', 'huggingface'))
                print(f"正在同步本地 huggingface 缓存到 {hf_cache} (仅新增文件)...")
                merge_dirs(local_hf, hf_cache)
                # 同步完成后写入标记文件，下次跳过
                with open(sync_marker, 'w', encoding='utf-8') as mf:
                    mf.write('synced')
                print("✓ 全局 Hugging Face 缓存已更新（保留原有文件，仅新增缺失项），并创建同步标记")

        return absolute_model_path
    except Exception as e:
        print(f"❌ 模型下载失败: {e}")
        print("请检查网络连接或手动下载模型")
        return None


def test_network_connectivity():
    """测试网络连接"""
    print("正在测试网络连接...")
    
    test_sites = [
        ("百度", "www.baidu.com"),
        ("GitHub", "github.com"),
    ]
    
    all_passed = True
    
    for site_name, site_url in test_sites:
        print(f"正在测试 {site_name} ({site_url})...")
        try:
            # 尝试ping测试
            result = subprocess.run(['ping', '-c', '3', '-W', '3', site_url], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"✓ {site_name} 连接正常")
            else:
                print(f"❌ {site_name} 连接失败")
                all_passed = False
        except subprocess.TimeoutExpired:
            print(f"❌ {site_name} 连接超时")
            all_passed = False
        except FileNotFoundError:
            # 如果ping命令不可用，尝试socket连接
            try:
                import socket
                socket.gethostbyname(site_url)
                print(f"✓ {site_name} DNS解析正常")
            except socket.gaierror:
                print(f"❌ {site_name} DNS解析失败")
                all_passed = False
    
    if all_passed:
        print("✓ 网络连接测试通过")
        return True
    else:
        print("❌ 网络连接测试失败，请检查网络连接")
        return False
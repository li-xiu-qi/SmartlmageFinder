#!/usr/bin/env python3
"""
SmartImageFinder 环境初始化模块
负责完整的环境初始化流程
"""

import sys
from pathlib import Path

# 导入其他模块
from environment_checker import (
    check_python_version, check_node_version, check_npm_version,
    install_python_dependencies, install_frontend_dependencies,
    mark_environment_ready, is_environment_ready
)
from model_manager import install_modelscope, test_network_connectivity, download_model
from config_manager import (
    get_user_input, load_example_config, create_config_file,
    configure_api_settings, configure_vision_model, configure_chat_model
)


def main():
    """主函数"""
    print("=" * 60)
    print("      SmartImageFinder 环境初始化脚本")
    print("=" * 60)
    print("\n🚀 此脚本将为您完成以下工作：")
    print("   1. 检查运行环境 (Python, Node.js, npm)")
    print("   2. 安装项目依赖 (Python + 前端)")
    print("   3. 下载模型文件")
    print("   4. 创建配置文件")
    print("   5. 创建环境就绪标记")
    print("=" * 60)

    # 检查是否已经初始化
    if is_environment_ready():
        print("\n⚠️ 检测到环境已初始化完成")
        reinit = get_user_input("是否要重新初始化环境? (y/n)", "n").lower()
        if reinit not in ["y", "yes", "是"]:
            print("初始化已取消")
            return

    # 1. 检查运行环境
    print("\n🔍 第1步：检查运行环境...")
    if not check_python_version():
        print("❌ Python版本检查失败，脚本退出")
        return
    
    if not check_node_version() or not check_npm_version():
        print("❌ Node.js/npm检查失败，脚本退出")
        return

    # 2. 测试网络连接
    print("\n🌐 第2步：测试网络连接...")
    if not test_network_connectivity():
        print("❌ 网络连接测试失败，脚本退出")
        return

    # 3. 安装依赖
    print("\n📦 第3步：安装项目依赖...")
    if not install_python_dependencies():
        print("❌ Python依赖安装失败，脚本退出")
        return
    
    if not install_frontend_dependencies():
        print("❌ 前端依赖安装失败，脚本退出")
        return

    # 获取当前脚本所在目录作为项目根目录
    base_path = Path(__file__).parent.parent.absolute()
    print(f"\n📁 项目根目录: {base_path}")

    # 检查是否已有配置文件
    config_path = base_path / "backend" / "config" / "files" / "config.yaml"
    if config_path.exists():
        overwrite = get_user_input(f"\n配置文件已存在，是否覆盖? (y/n)", "n").lower()
        if overwrite not in ["y", "yes", "是"]:
            print("❌ 配置文件已存在，初始化取消")
            return

    # 4. 读取示例配置
    print("\n⚙️ 第4步：读取示例配置...")
    config_data = load_example_config(base_path)
    if not config_data:
        print("❌ 无法读取示例配置，脚本退出")
        return

    # 5. 安装ModelScope
    print("\n🤖 第5步：检查ModelScope依赖...")
    if not install_modelscope():
        return

    # 6. 处理模型
    print("\n🧠 第6步：处理模型文件...")
    models_dir = base_path / "models"
    models_dir.mkdir(exist_ok=True)
    print(f"✓ 创建models目录: {models_dir}")
    
    # 从模板配置中读取默认模型名（例如: org/repo）
    default_model_name = str(config_data.get('MODEL_PATH', 'jinaai/jina-embeddings-v4')).strip()
    selected_model_name = default_model_name

    model_path = None
    
    # 检查models目录下是否已存在模型
    _repo_leaf = selected_model_name.split('/')[-1] if selected_model_name else 'jina-embeddings-v4'
    existing_models = list(models_dir.glob(f"*{_repo_leaf}*"))
    if existing_models:
        print(f"\n发现models目录下已存在的模型: {existing_models[0]}")
        use_existing = get_user_input("是否使用现有模型? (y/n)", "y").lower()
        if use_existing in ["y", "yes", "是"]:
            model_path = str(existing_models[0].absolute())
            print(f"✓ 使用现有模型: {model_path}")

    # 如果没有现有模型，询问是否使用自定义路径
    if not model_path:
        print("\n模型获取选项:")
        print("1. 下载模型到本地")
        print("2. 使用已有的本地模型路径")
        
        choice = get_user_input("请选择 (1/2)", "1").strip()
        
        if choice == "2":
            # 用户选择使用自定义路径
            custom_path = get_user_input("请输入本地模型的绝对路径", "").strip()
            if custom_path:
                custom_path_obj = Path(custom_path)
                if custom_path_obj.exists():
                    model_path = str(custom_path_obj.absolute())
                    print(f"✓ 使用自定义模型路径: {model_path}")
                else:
                    print(f"❌ 路径不存在: {custom_path}")
                    print("将改为下载模型...")
        else:
            # 选择下载模型，允许用户指定模型名（默认读取模板中的 MODEL_PATH）
            user_model = get_user_input("请输入要下载的模型名 (ModelScope 仓库标识)", default_model_name).strip()
            if user_model:
                selected_model_name = user_model
            # 更新用于本地已存在模型的再次匹配（若用户更改了模型名）
            _repo_leaf = selected_model_name.split('/')[-1]
            # 不在这里重新搜了，仅用于下载逻辑
    
    # 如果仍然没有模型路径，则下载模型
    if not model_path:
        print(f"\n正在下载模型: {selected_model_name} ...")
        model_path = download_model(selected_model_name, str(models_dir))

        if not model_path:
            print("❌ 模型下载失败，脚本退出")
            return

    # 6.1 询问并设置模型输出向量维度
    try:
        default_dim = int(config_data.get('EMBEDDING_DIMENSION', 2048))
    except Exception:
        default_dim = 2048
    dim_input = get_user_input("请输入模型输出的向量维度 (整数)", str(default_dim)).strip()
    try:
        embed_dim = int(dim_input) if dim_input else default_dim
    except ValueError:
        print("❌ 无效的向量维度输入，使用默认值")
        embed_dim = default_dim
    config_data['EMBEDDING_DIMENSION'] = embed_dim

    # 7. 可选配置
    print("\n⚙️ 第7步：可选配置...")
    
    # 配置API设置
    config_data = configure_api_settings(config_data)
    
    # 配置聊天模型
    config_data = configure_chat_model(config_data)
    
    # 配置视觉多模态模型
    config_data = configure_vision_model(config_data)
        
    # 8. 创建配置文件
    print("\n📄 第8步：创建配置文件...")
    if create_config_file(base_path, config_data, model_path):
        print(f"✓ 配置文件已创建: {config_path}")
    else:
        print("❌ 配置文件创建失败")
        return

    # 9. 创建环境就绪标记
    print("\n🎯 第9步：创建环境就绪标记...")
    mark_environment_ready()

    # 完成提示
    print("\n" + "=" * 60)
    print("    ✅ 环境初始化完成！")
    print("=" * 60)
    print(f"🧠 模型路径: {model_path}")
    print(f"⚙️ 配置文件: {config_path}")
    print("\n🚀 现在您可以运行以下命令启动项目：")
    print("   python start.py")
    print("\n📝 配置基于 config.example.yaml 生成")
    print("如需更多配置修改，请直接编辑 config.yaml 文件")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n用户取消操作")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
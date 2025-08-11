#!/usr/bin/env python3
"""
SmartImageFinder 配置管理模块
负责配置文件的创建和管理
"""

import os
import sys
import yaml
from pathlib import Path


def get_user_input(prompt: str, default: str = "") -> str:
    """获取用户输入"""
    if default:
        display_prompt = f"{prompt} (默认: {default}): "
    else:
        display_prompt = f"{prompt}: "

    user_input = input(display_prompt).strip()
    return user_input if user_input else default


def load_example_config(base_path: Path) -> dict:
    """读取示例配置文件"""
    example_config_path = base_path / "backend" / "config" / "files" / "config.example.yaml"
    
    try:
        with open(example_config_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        print(f"✓ 已读取示例配置: {example_config_path}")
        return config_data
    except Exception as e:
        print(f"❌ 读取示例配置失败: {e}")
        return None


def create_config_file(base_path: Path, config_data: dict, model_path: str):
    """创建配置文件"""
    config_path = base_path / "backend" / "config" / "files" / "config.yaml"
    
    # 更新模型路径为下载的绝对路径（模型路径需要保持绝对路径）
    config_data['MODEL_PATH'] = model_path
    
    # 使用相对路径
    config_data['VECTOR_DB_DRIVER_DIR'] = "./backend/config/files/vector_db_driver"
    config_data['UPLOAD_DIR'] = "./data/images"
    config_data['TEMP_DIR'] = "./data/temp"
    config_data['DB_PATH'] = "./data/db/smartimagefinder.db"
    config_data['TEXT_VECTOR_CACHE_DIR'] = "./data/caches/text_vector_cache"
    config_data['IMAGE_VECTOR_CACHE_DIR'] = "./data/caches/image_vector_cache"

    try:
        # 确保配置文件目录存在
        config_path.parent.mkdir(parents=True, exist_ok=True)

        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(
                config_data,
                f,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False,
            )
        print(f"✓ 配置文件已创建: {config_path}")
        return True
    except Exception as e:
        print(f"❌ 创建配置文件失败: {e}")
        return False


def select_vision_model(config_data: dict) -> str:
    """选择视觉多模态模型"""
    print("\n配置视觉多模态模型:")
    
    # 获取示例配置中的默认值
    default_vision_model = config_data.get('VISION_MODEL')
    available_models = config_data.get('AVAILABLE_VISION_MODELS')
    
    # 显示当前的模型列表
    if available_models:
        print(f"\n当前可用的模型 (默认选择: {default_vision_model}):")
        for i, model in enumerate(available_models, 1):
            marker = " ✓" if model == default_vision_model else ""
            print(f"{i}. {model}{marker}")
    else:
        print("\n当前没有配置任何可用模型。")
        
    # 询问是否使用默认配置
    use_default = get_user_input(f"\n是否使用默认视觉模型 '{default_vision_model}'? (y/n)", "y").lower()
    if use_default in ["y", "yes", "是"]:
        print(f"✓ 使用默认视觉模型: {default_vision_model}")
        return default_vision_model
        
    # 询问是否要清空现有模型列表
    clear_models = get_user_input("\n是否要清空现有的模型列表? (y/n)", "n").lower()
    if clear_models in ["y", "yes", "是"]:
        available_models = []
        config_data['AVAILABLE_VISION_MODELS'] = available_models
        print("✓ 已清空模型列表")
        
    # 询问是否要添加新模型
    add_model = get_user_input("\n是否要添加新的模型? (y/n)", "n").lower()
    while add_model in ["y", "yes", "是"]:
        new_model = get_user_input("请输入新模型的完整路径(例如: Qwen/Qwen2.5-VL-7B)", "").strip()
        if new_model and new_model not in available_models:
            available_models.append(new_model)
            print(f"✓ 已添加模型: {new_model}")
            config_data['AVAILABLE_VISION_MODELS'] = available_models
        
        add_model = get_user_input("是否继续添加新模型? (y/n)", "n").lower()
    
    # 重新显示所有可用模型并选择
    if available_models:
        print("\n所有可用的模型:")
        for i, model in enumerate(available_models, 1):
            print(f"{i}. {model}")
        
        while True:
            choice = get_user_input(f"请选择要使用的模型 (1-{len(available_models)})", "1")
            try:
                index = int(choice) - 1
                if 0 <= index < len(available_models):
                    selected_model = available_models[index]
                    print(f"✓ 已选择模型: {selected_model}")
                    return selected_model
                else:
                    print("❌ 无效的选择，请重新输入")
            except ValueError:
                print("❌ 请输入有效的数字")
    else:
        print("❌ 没有可用的模型，使用默认模型")
        return default_vision_model


def configure_api_settings(config_data: dict) -> dict:
    """配置API设置"""
    print("\n" + "=" * 30)
    print("   可选配置")
    print("=" * 30)
    
    # 获取示例配置中的默认值
    default_api_key = config_data.get('OPENAI_API_KEY', '')
    default_api_base = config_data.get('OPENAI_API_BASE', 'https://api.siliconflow.cn/v1')
    
    print("如需修改API配置，请输入新值。直接回车使用示例配置的默认值。")
    
    # 询问是否使用默认API配置
    use_default_api = get_user_input(f"\n是否使用默认API配置? (y/n)", "y").lower()
    if use_default_api in ["y", "yes", "是"]:
        print(f"✓ 使用默认API Base: {default_api_base}")
        if default_api_key:
            print(f"✓ 使用默认API Key: {default_api_key[:8]}...")
        else:
            print("✓ API Key 未设置 (可在后续配置)")
        return config_data
    
    # 手动配置API设置
    new_api_key = get_user_input(f"OpenAI API密钥 (当前: {'已设置' if default_api_key else '未设置'})", default_api_key)
    if new_api_key != default_api_key:
        config_data['OPENAI_API_KEY'] = new_api_key

    new_api_base = get_user_input(f"API Base URL", default_api_base)
    if new_api_base != default_api_base:
        config_data['OPENAI_API_BASE'] = new_api_base

    return config_data


def configure_chat_model(config_data: dict) -> dict:
    """配置聊天模型"""
    # 获取示例配置中的默认值
    default_chat_model = config_data.get('CHAT_MODEL', 'THUDM/GLM-Z1-9B-0414')
    
    # 询问是否使用默认聊天模型
    use_default = get_user_input(f"\n是否使用默认聊天模型 '{default_chat_model}'? (y/n)", "y").lower()
    if use_default in ["y", "yes", "是"]:
        print(f"✓ 使用默认聊天模型: {default_chat_model}")
        return config_data
    
    # 手动配置聊天模型
    new_chat_model = get_user_input(f"聊天模型名称", default_chat_model)
    if new_chat_model != default_chat_model:
        config_data['CHAT_MODEL'] = new_chat_model
        print(f"✓ 已设置聊天模型: {new_chat_model}")
    
    return config_data


def configure_vision_model(config_data: dict) -> dict:
    """配置视觉多模态模型"""
    # 获取示例配置中的默认值
    default_vision_model = config_data.get('VISION_MODEL', 'Qwen/Qwen2.5-VL-32B-Instruct')
    
    new_vision_model = select_vision_model(config_data)
    if new_vision_model != default_vision_model:
        config_data['VISION_MODEL'] = new_vision_model
        print(f"✓ 已设置视觉模型: {new_vision_model}")
    
    return config_data


def configure_storage_settings(config_data: dict) -> dict:
    """配置存储设置"""
    print("\n配置存储设置:")
    
    # 获取示例配置中的默认值
    default_upload_dir = config_data.get('UPLOAD_DIR', './data/images')
    default_cache_size = config_data.get('MAX_CACHE_SIZE_GB', 1.5)
    
    # 询问是否使用默认存储配置
    use_default = get_user_input(f"\n是否使用默认存储配置? (y/n)", "y").lower()
    if use_default in ["y", "yes", "是"]:
        print(f"✓ 使用默认上传目录: {default_upload_dir}")
        print(f"✓ 使用默认缓存大小: {default_cache_size}GB")
        return config_data
    
    # 手动配置存储设置
    new_upload_dir = get_user_input(f"图片上传目录", default_upload_dir)
    if new_upload_dir != default_upload_dir:
        config_data['UPLOAD_DIR'] = new_upload_dir
    
    new_cache_size = get_user_input(f"最大缓存大小(GB)", str(default_cache_size))
    try:
        cache_size_float = float(new_cache_size)
        if cache_size_float != default_cache_size:
            config_data['MAX_CACHE_SIZE_GB'] = cache_size_float
    except ValueError:
        print("❌ 无效的缓存大小，使用默认值")

    return config_data


def configure_port_settings(config_data: dict) -> dict:
    """配置端口设置"""
    print("\n配置端口设置:")
    
    # 获取示例配置中的默认值
    default_host = config_data.get('HOST', '0.0.0.0')
    default_port = config_data.get('PORT', 10050)
    
    # 询问是否使用默认端口配置
    use_default = get_user_input(f"\n是否使用默认端口配置 (主机: {default_host}, 端口: {default_port})? (y/n)", "y").lower()
    if use_default in ["y", "yes", "是"]:
        print(f"✓ 使用默认主机: {default_host}")
        print(f"✓ 使用默认端口: {default_port}")
        return config_data
    
    # 手动配置端口设置
    new_host = get_user_input(f"主机地址", default_host)
    if new_host != default_host:
        config_data['HOST'] = new_host
    
    new_port = get_user_input(f"端口号", str(default_port))
    try:
        port_int = int(new_port)
        if port_int != default_port:
            config_data['PORT'] = port_int
    except ValueError:
        print("❌ 无效的端口号，使用默认值")
    
    return config_data


def configure_all_settings(config_data: dict) -> dict:
    """配置所有设置的主函数"""
    print("\n" + "=" * 50)
    print("   SmartImageFinder 配置向导")
    print("=" * 50)
    print("我们将引导您完成配置过程。对于每个设置，您可以选择:")
    print("- 使用示例配置的默认值 (推荐)")
    print("- 手动自定义配置")
    print("=" * 50)
    
    # 1. 配置聊天模型
    config_data = configure_chat_model(config_data)
    
    # 2. 配置视觉模型
    config_data = configure_vision_model(config_data)
    
    # 3. 配置API设置
    config_data = configure_api_settings(config_data)
    
    # 4. 配置存储设置
    config_data = configure_storage_settings(config_data)
    
    # 5. 配置端口设置
    config_data = configure_port_settings(config_data)
    
    print("\n" + "=" * 50)
    print("   配置完成")
    print("=" * 50)
    
    return config_data
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
    example_config_path = base_path / "backend" / "config_files" / "config.example.yaml"
    
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
    config_path = base_path / "backend" / "config_files" / "config.yaml"
    
    # 更新模型路径为下载的绝对路径（模型路径需要保持绝对路径）
    config_data['MODEL_PATH'] = model_path
    
    # 使用相对路径
    config_data['VECTOR_DB_DRIVER_DIR'] = "./backend/config_files/vector_db_driver"
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
    
    # 1. 获取当前可用的模型列表
    available_models = config_data.get('AVAILABLE_VISION_MODELS', [])
    
    # 显示当前的模型列表
    if available_models:
        print("\n当前可用的模型:")
        for i, model in enumerate(available_models, 1):
            print(f"{i}. {model}")
            
        # 询问是否要清空现有模型列表
        clear_models = get_user_input("\n是否要清空现有的模型列表? (y/n)", "n").lower()
        if clear_models in ["y", "yes", "是"]:
            available_models = []
            config_data['AVAILABLE_VISION_MODELS'] = available_models
            print("✓ 已清空模型列表")
    else:
        print("\n当前没有配置任何可用模型。")
        
    # 2. 询问是否要添加新模型
    add_model = get_user_input("\n是否要添加新的模型? (y/n)", "n").lower()
    while add_model in ["y", "yes", "是"]:
        new_model = get_user_input("请输入新模型的完整路径(例如: Qwen/Qwen2.5-VL-7B)", "").strip()
        if new_model and new_model not in available_models:
            available_models.append(new_model)
            print(f"✓ 已添加模型: {new_model}")
            config_data['AVAILABLE_VISION_MODELS'] = available_models
        
        add_model = get_user_input("是否继续添加新模型? (y/n)", "n").lower()
    
    # 3. 重新显示所有可用模型并选择
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


def configure_api_settings(config_data: dict) -> dict:
    """配置API设置"""
    print("\n" + "=" * 30)
    print("   可选配置")
    print("=" * 30)
    print("如需修改API配置，请输入新值。直接回车保持默认值。")
    
    current_api_key = config_data.get('OPENAI_API_KEY', '')
    new_api_key = get_user_input("OpenAI API密钥", current_api_key)
    if new_api_key != current_api_key:
        config_data['OPENAI_API_KEY'] = new_api_key

    current_api_base = config_data.get('OPENAI_API_BASE', 'https://api.siliconflow.cn/v1')
    new_api_base = get_user_input("API Base URL", current_api_base)
    if new_api_base != current_api_base:
        config_data['OPENAI_API_BASE'] = new_api_base

    return config_data


def configure_chat_model(config_data: dict) -> dict:
    """配置聊天模型"""
    current_chat_model = config_data.get('CHAT_MODEL', 'THUDM/GLM-Z1-9B-0414')
    new_chat_model = get_user_input("聊天模型名称", current_chat_model)
    if new_chat_model != current_chat_model:
        config_data['CHAT_MODEL'] = new_chat_model
    
    return config_data


def configure_vision_model(config_data: dict) -> dict:
    """配置视觉多模态模型"""
    current_vision_model = config_data.get('VISION_MODEL', '')
    new_vision_model = select_vision_model(config_data)
    if new_vision_model != current_vision_model:
        config_data['VISION_MODEL'] = new_vision_model
    
    return config_data
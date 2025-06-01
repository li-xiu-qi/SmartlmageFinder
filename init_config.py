#!/usr/bin/env python3
"""
SmartImageFinder 配置初始化脚本
用于下载模型和创建配置文件
"""

import os
import sys
import yaml
from pathlib import Path

# 设置标准输出编码为 utf-8
if sys.platform == 'win32':
    # Windows 平台
    try:
        # Python 3.7+ 支持 reconfigure
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        # 较旧的 Python 版本
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
else:
    # 其他平台默认使用 utf-8
    pass


def install_modelscope():
    """安装ModelScope依赖"""
    print("正在检查并安装ModelScope依赖...")
    try:
        import modelscope
        print("✓ ModelScope已安装")
    except ImportError:
        print("正在安装ModelScope...")
        os.system(f"{sys.executable} -m pip install modelscope")
        try:
            import modelscope
            print("✓ ModelScope安装成功")
        except ImportError:
            print("❌ ModelScope安装失败，请手动安装: pip install modelscope")
            return False
    return True


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
        return absolute_model_path
    except Exception as e:
        print(f"❌ 模型下载失败: {e}")
        print("请检查网络连接或手动下载模型")
        return None


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
    
    # 更新模型路径为下载的绝对路径
    config_data['MODEL_PATH'] = model_path
    
    # 将其他相对路径转换为绝对路径
    config_data['VECTOR_DB_DRIVER_DIR'] = str((base_path / "backend" / "config_files" / "vector_db_driver").absolute())
    config_data['UPLOAD_DIR'] = str((base_path / "data" / "images").absolute())
    config_data['TEMP_DIR'] = str((base_path / "data" / "temp").absolute())
    config_data['DB_PATH'] = str((base_path / "data" / "db" / "smartimagefinder.db").absolute())
    config_data['TEXT_VECTOR_CACHE_DIR'] = str((base_path / "data" / "caches" / "text_vector_cache").absolute())
    config_data['IMAGE_VECTOR_CACHE_DIR'] = str((base_path / "data" / "caches" / "image_vector_cache").absolute())

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


def main():
    """主函数"""
    print("=" * 50)
    print("  SmartImageFinder 配置初始化脚本")
    print("=" * 50)

    # 获取当前脚本所在目录作为项目根目录
    base_path = Path(__file__).parent.absolute()
    print(f"项目根目录: {base_path}")

    # 检查是否已有配置文件
    config_path = base_path / "backend" / "config_files" / "config.yaml"
    if config_path.exists():
        overwrite = get_user_input(f"配置文件已存在，是否覆盖? (y/n)", "n").lower()
        if overwrite not in ["y", "yes", "是"]:
            print("初始化已取消")
            return

    # 读取示例配置
    print("\n正在读取示例配置...")
    config_data = load_example_config(base_path)
    if not config_data:
        print("❌ 无法读取示例配置，脚本退出")
        return

    # 安装ModelScope
    if not install_modelscope():
        return

    # 创建models目录
    models_dir = base_path / "models"
    models_dir.mkdir(exist_ok=True)
    print(f"✓ 创建models目录: {models_dir}")    # 检查模型路径选项
    model_path = None
    
    # 1. 检查models目录下是否已存在模型
    existing_models = list(models_dir.glob("*jina-clip*"))
    if existing_models:
        print(f"\n发现models目录下已存在的模型: {existing_models[0]}")
        use_existing = get_user_input("是否使用现有模型? (y/n)", "y").lower()
        if use_existing in ["y", "yes", "是"]:
            model_path = str(existing_models[0].absolute())
            print(f"✓ 使用现有模型: {model_path}")

    # 2. 如果没有现有模型，询问是否使用自定义路径
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
                    print("将改为下载模型...")    # 3. 如果仍然没有模型路径，则下载模型
    if not model_path:
        print("\n正在下载JINA CLIP V2模型...")
        model_path = download_model("yizhixiaoke/xiaoke-jina-clip-v2", str(models_dir))

        if not model_path:
            print("❌ 模型下载失败，脚本退出")
            return

    # 可选：询问用户是否需要修改API密钥
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

    # 选择视觉多模态模型
    current_vision_model = config_data.get('VISION_MODEL', '')
    new_vision_model = select_vision_model(config_data)
    if new_vision_model != current_vision_model:
        config_data['VISION_MODEL'] = new_vision_model
        
    # 创建配置文件
    print("\n正在创建配置文件...")
    if create_config_file(base_path, config_data, model_path):
        print("\n" + "=" * 50)
        print("    ✅ 初始化完成！")
        print("=" * 50)
        print(f"模型路径: {model_path}")
        print(f"配置文件: {config_path}")
        print("\n配置基于 config.example.yaml 生成")
        print("如需更多配置修改，请直接编辑 config.yaml 文件")
    else:
        print("❌ 配置文件创建失败")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n用户取消操作")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback

        traceback.print_exc()

from typing import Optional, Dict, Any, List
import os
import yaml
from pydantic import BaseModel, ValidationError, Field


# Pydantic 配置模型
class AppConfig(BaseModel):
    MODEL_PATH: str  # 不提供默认值，必须在 config.yaml 中提供或通过更新设置
    VECTOR_DB_DRIVER: Optional[str] = None
    EMBEDDING_DIMENSION: Optional[int] = None
    UPLOAD_DIR: str = "./data/images"
    TEMP_DIR: str = "./data/temp"  # 添加临时目录配置
    DB_PATH: str = "./data/db/smartimagefinder.db"
    TEXT_VECTOR_CACHE_DIR: str = "./data/caches/text_vector_cache"
    IMAGE_VECTOR_CACHE_DIR: str = "./data/caches/image_vector_cache"
    USE_CACHE: bool = True
    MAX_CACHE_SIZE_GB: float = 1.5
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_API_BASE: Optional[str] = None
    VISION_MODEL: Optional[str] = None
    AVAILABLE_VISION_MODELS: List[str] = Field(
        default_factory=lambda: [
            "Qwen/Qwen2.5-VL-32B-Instruct",
            "Pro/Qwen/Qwen2.5-VL-7B-Instruct",
        ]
    )
    AI_ENABLED: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 1000  # 根据当前 config.yaml 设置

    class Config:
        validate_assignment = True  # 验证赋值


def ensure_directories_exist(file_paths=None, dir_paths=None):
    """确保所有必要的目录存在，如果不存在则创建它们"""
    if file_paths:
        for file_path in file_paths:
            dir_name = os.path.dirname(file_path)
            if dir_name and not os.path.exists(dir_name):
                os.makedirs(dir_name, exist_ok=True)
                print(f"已创建目录: {dir_name}")

    if dir_paths:
        for dir_path in dir_paths:
            if dir_path and not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)
                print(f"已创建目录: {dir_path}")


class Settings:
    """
    应用配置类，使用 Pydantic 模型管理配置，支持从 YAML 文件加载和保存。
    """

    _instance = None
    _config_file_path: Optional[str] = None
    _config_model: Optional[AppConfig] = None

    def __new__(cls, config_file_path: Optional[str] = None):
        if cls._instance is None:
            cls._instance = super(Settings, cls).__new__(cls)
            cls._instance._initialized = False
            if config_file_path is not None:  # 首次实例化时设置路径（如果提供）
                cls._config_file_path = os.path.abspath(config_file_path)
        elif config_file_path is not None and cls._config_file_path != os.path.abspath(
            config_file_path
        ):
            # 如果为现有实例提供了新路径，允许重新配置
            cls._config_file_path = os.path.abspath(config_file_path)
            cls._instance._initialized = False  # 强制重新初始化
        return cls._instance

    def __init__(self, config_file_path: Optional[str] = None):
        if getattr(self, "_initialized", False) and (
            config_file_path is None
            or os.path.abspath(config_file_path) == self.__class__._config_file_path
        ):
            return

        if config_file_path is not None:  # 优先使用传递给 init 的路径
            self.__class__._config_file_path = os.path.abspath(config_file_path)

        if self.__class__._config_file_path is None:  # 回退到默认路径
            current_script_dir = os.path.dirname(os.path.abspath(__file__))
            self.__class__._config_file_path = os.path.join(
                current_script_dir, "config", "config.yaml"
            )

        self.config_file = self.__class__._config_file_path

        config_dir = os.path.dirname(self.config_file)
        if not os.path.exists(config_dir):
            os.makedirs(config_dir, exist_ok=True)
            print(f"配置目录已创建: {config_dir}")

        self._config_model = None  # 加载前初始化
        self.reload()

        # 确保所有必要的目录在配置加载后立即创建
        if self._config_model:
            self._create_required_directories()

        self._initialized = True

    def _create_required_directories(self):
        """根据配置创建所有必要的目录"""
        dirs_to_create = [
            self._config_model.UPLOAD_DIR,
            os.path.dirname(self._config_model.DB_PATH),
            self._config_model.TEXT_VECTOR_CACHE_DIR,
            self._config_model.IMAGE_VECTOR_CACHE_DIR,
        ]
        ensure_directories_exist(dir_paths=dirs_to_create)
        print("所有必要的应用目录已初始化")

    def reload(self) -> bool:
        raw_data: Dict[str, Any] = {}
        config_source_is_file = False
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, "r", encoding="utf-8") as file:
                    loaded_yaml = yaml.safe_load(file)
                    if isinstance(loaded_yaml, dict):
                        raw_data = loaded_yaml
                        config_source_is_file = True
                    elif loaded_yaml is not None:
                        print(
                            f"警告: 配置文件 {self.config_file} 格式不正确，应为字典。将使用默认配置。"
                        )
                    # 如果 loaded_yaml 为 None（空文件），raw_data 保持为 {}
            else:
                print(f"提示: 配置文件 {self.config_file} 不存在。将使用默认配置。")

            self._config_model = AppConfig(**raw_data)
            if config_source_is_file:
                print(f"配置已从 {self.config_file} 加载并使用 Pydantic 模型验证。")
            else:
                print(f"配置已根据 Pydantic 模型默认值初始化。")

            if not os.path.exists(self.config_file) or not raw_data:
                if (
                    self._config_model.MODEL_PATH
                ):  # 仅在关键路径如 MODEL_PATH 已设置（或有默认值）时保存
                    print(
                        f"配置文件 {self.config_file} 不存在或为空，将使用当前（可能为默认）配置创建/覆盖。"
                    )
                    self.save()  # 注意：如果 MODEL_PATH 不是必需的或有默认值，这可能会用默认值覆盖空文件
                else:
                    print(
                        f"提示: MODEL_PATH 未设置，配置文件 {self.config_file} 将不会自动创建/覆盖。请确保配置文件中包含 MODEL_PATH。"
                    )

            return True
        except ValidationError as e:
            print(
                f"错误: 配置验证失败 (源: {self.config_file if config_source_is_file else '默认值'}). {e}"
            )
            print("将回退到 Pydantic 模型定义的默认配置。")
            self._config_model = AppConfig()  # 回退到 Pydantic 默认值
            return False
        except Exception as e:
            print(f"错误: 加载配置文件 {self.config_file} 失败: {e}")
            print("将回退到 Pydantic 模型定义的默认配置。")
            self._config_model = AppConfig()  # 回退
            return False

    def save(self) -> bool:
        if self._config_model is None:
            print("错误: 没有配置模型可保存。")
            return False

        # 在保存前确保 MODEL_PATH 已设置（如果它是关键的且没有默认值）
        if not self._config_model.MODEL_PATH:
            print(
                f"错误: MODEL_PATH 未在配置中设置。保存已中止以避免创建不完整的配置文件。"
            )

        try:
            config_dir = os.path.dirname(self.config_file)
            if not os.path.exists(config_dir):
                os.makedirs(config_dir, exist_ok=True)

            with open(self.config_file, "w", encoding="utf-8") as file:
                yaml.dump(
                    self._config_model.model_dump(),
                    file,
                    allow_unicode=True,
                    sort_keys=False,
                )
            print(f"配置已保存到 {self.config_file}")
            return True
        except Exception as e:
            print(f"错误: 保存配置文件 {self.config_file} 失败: {e}")
            return False

    def get_config(self) -> Optional[AppConfig]:
        """获取当前加载的 AppConfig 模型实例。"""
        return self._config_model

    def update_config(self, new_data: Dict[str, Any], auto_save: bool = True) -> bool:
        """
        使用新数据更新配置。新数据将与现有配置合并，然后通过 Pydantic 模型进行验证。
        """
        try:
            current_config_dict = (
                self._config_model.model_dump() if self._config_model else {}
            )
            merged_data = {**current_config_dict, **new_data}

            # 验证并更新模型
            self._config_model = AppConfig(**merged_data)

            # 确保所有必要的目录在配置更新后立即创建
            self._create_required_directories()

            print("配置已在内存中更新并通过验证。")
            if auto_save:
                if not self._config_model.MODEL_PATH:
                    print(
                        f"警告: MODEL_PATH 未设置，配置已在内存中更新但未保存到文件。"
                    )
                    return True  # 在内存中更新了，但未保存
                return self.save()
            return True
        except ValidationError as e:
            print(f"错误: 更新配置失败，数据验证错误: {e}")
            # 由于完成赋值前发生异常，self._config_model 保持为旧的有效值
            return False
        except Exception as e:
            print(f"错误: 更新配置时发生意外错误: {e}")
            return False


# 创建全局设置实例
settings = Settings(
    config_file_path=os.path.join(
        os.path.dirname(__file__), "config_files", "config.yaml"
    )
)

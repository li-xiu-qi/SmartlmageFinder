import os
import yaml
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, ValidationError, Field
from pathlib import Path
from .platform_detector import PlatformDetector


# Pydantic 配置模型
class AppConfig(BaseModel):
    MODEL_PATH: str  # 不提供默认值，必须在 config.yaml 中提供或通过更新设置
    VECTOR_DB_DRIVER_DIR: str = "./backend/config/files/vector_db_driver"  # 更新默认路径
    VECTOR_DB_DRIVER: Optional[str] = None  # 将由代码动态填充
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

    CHAT_MODEL: Optional[str] = "Qwen/Qwen3-8B"  # 新增聊天模型字段，默认值
    VISION_MODEL: Optional[str] = None
    AVAILABLE_VISION_MODELS: List[str] = Field(
        default_factory=lambda: [
            "Qwen/Qwen2.5-VL-32B-Instruct",
            "Pro/Qwen/Qwen2.5-VL-7B-Instruct",
        ]
    )
    HOST: str = "0.0.0.0"
    PORT: int = 8000  # 根据当前 config.yaml 设置

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
            if config_file_path is not None:
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
                current_script_dir, "files", "config.yaml"
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

    def _determine_and_set_vector_db_driver(self, config_model_instance: AppConfig) -> None:
        """根据 VECTOR_DB_DRIVER_DIR 动态确定并设置 VECTOR_DB_DRIVER"""
        if not config_model_instance or not hasattr(config_model_instance, "VECTOR_DB_DRIVER_DIR") or not config_model_instance.VECTOR_DB_DRIVER_DIR:
            if config_model_instance:
                config_model_instance.VECTOR_DB_DRIVER = None
            print("警告: VECTOR_DB_DRIVER_DIR 未配置, 无法自动确定驱动路径。")
            return

        try:
            # self.config_file 是 config.yaml 的绝对路径
            # VECTOR_DB_DRIVER_DIR (例如 "./backend/config_files/vector_db_driver") 是相对于项目根目录的
            project_root = Path(self.config_file).resolve().parent.parent.parent.parent

            relative_driver_dir_str = config_model_instance.VECTOR_DB_DRIVER_DIR

            path_inside_project = relative_driver_dir_str.lstrip("./").lstrip(".\\\\")

            absolute_vector_db_driver_dir = (project_root / path_inside_project).resolve()

            driver_path = PlatformDetector.get_driver_path(str(absolute_vector_db_driver_dir))

            if driver_path and os.path.exists(driver_path):
                config_model_instance.VECTOR_DB_DRIVER = driver_path
            else:
                config_model_instance.VECTOR_DB_DRIVER = None
                print(f"警告: 无法在 {absolute_vector_db_driver_dir} 中找到适用于当前平台的驱动程序。VECTOR_DB_DRIVER 未设置。")
        except Exception as e:
            if config_model_instance:
                config_model_instance.VECTOR_DB_DRIVER = None
            print(f"错误: 在确定 VECTOR_DB_DRIVER 时发生异常: {e}")

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
        if not self.config_file or not os.path.exists(self.config_file):
            print(f"配置文件 {self.config_file} 不存在。使用默认配置。")
            try:
                # 尝试使用 Pydantic 模型的默认值（如果 AppConfig 字段都有默认值）
                # 如果关键字段（如 MODEL_PATH, VECTOR_DB_DRIVER_DIR）没有默认值，这里会失败
                self._config_model = AppConfig()
            except ValidationError as e:
                print(f"无法使用默认值创建配置模型: {e}")
                # 如果 VECTOR_DB_DRIVER_DIR 等是必需的，则需要一个空的 AppConfig 或处理
                # 为了安全起见，如果关键路径不存在，则不应继续
                self._config_model = None  # 明确设置为 None
                return False  # 指示加载失败

            if self._config_model:
                # 即使使用默认配置，也尝试确定驱动程序（如果 VECTOR_DB_DRIVER_DIR 有默认值）
                self._determine_and_set_vector_db_driver(self._config_model)
                if self._config_model.VECTOR_DB_DRIVER:
                    print(f"动态设置 VECTOR_DB_DRIVER 为: {self._config_model.VECTOR_DB_DRIVER}")
                else:
                    # 如果 VECTOR_DB_DRIVER_DIR 本身就没有或无法解析，则会打印警告
                    pass  # _determine_and_set_vector_db_driver 内部会打印警告
                self._create_required_directories()
                # 检查 OpenAI 配置
                if not self._config_model.OPENAI_API_KEY:
                    print("警告: OPENAI_API_KEY 未配置，OpenAI 相关功能将不可用！")
                if not self._config_model.OPENAI_API_BASE:
                    print("警告: OPENAI_API_BASE 未配置，将使用默认 OpenAI API 地址！")
            return True  # 返回 True 表示已处理（即使是默认配置）

        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                yaml_data = yaml.safe_load(f)

            if yaml_data is None:  # 处理空配置文件的情况
                yaml_data = {}

            self._config_data_from_yaml = yaml_data  # 存储从YAML加载的原始数据

            # 使用从YAML加载的数据实例化AppConfig
            # Pydantic 会使用字段的默认值（如果在AppConfig中定义）来补充YAML中缺失的字段
            self._config_model = AppConfig(**self._config_data_from_yaml)

            # 动态设置 VECTOR_DB_DRIVER
            self._determine_and_set_vector_db_driver(self._config_model)
            if self._config_model.VECTOR_DB_DRIVER:
                print(f"动态设置 VECTOR_DB_DRIVER 为: {self._config_model.VECTOR_DB_DRIVER}")
            else:
                # _determine_and_set_vector_db_driver 内部会打印相关警告
                pass

            # 确保在模型完全设置后创建目录
            self._create_required_directories()
            # 检查 OpenAI 配置
            if not self._config_model.OPENAI_API_KEY:
                print("警告: OPENAI_API_KEY 未配置，OpenAI 相关功能将不可用！")
            if not self._config_model.OPENAI_API_BASE:
                print("警告: OPENAI_API_BASE 未配置，将使用默认 OpenAI API 地址！")
            print("配置已成功加载并应用。")
            return True
        except ValidationError as e:
            print(f"配置验证错误: {e}")
            self._config_model = None  # 确保出错时 _config_model 为 None
            return False
        except Exception as e:
            print(f"加载配置文件时发生错误: {e}")
            self._config_model = None
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
            return False

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
        if self._config_model is None:  # 如果模型未加载或加载失败
            # 尝试重新加载，这也会处理配置文件不存在的情况
            print("配置模型未初始化，尝试重新加载...")
            self.reload()
            # 再次检查，如果 reload 后仍然是 None，则确实无法获取配置
            if self._config_model is None:
                print("错误：配置模型无法初始化。请检查配置文件和错误日志。")
                return None
        return self._config_model

    def update_config(self, new_data: Dict[str, Any], auto_save: bool = True) -> bool:
        if not self._config_model:
            print("错误: 配置模型未初始化，无法更新。")
            # 尝试加载配置，如果成功则可以继续
            if not self.reload() or not self._config_model:
                print("错误: 尝试重新加载配置失败，更新操作中止。")
                return False

        # 获取当前配置的字典表示
        # 使用 .model_dump() (Pydantic V2) or .dict() (Pydantic V1)
        try:
            current_config_dict = self._config_model.model_dump()
        except AttributeError:  # 兼容 Pydantic V1
            current_config_dict = self._config_model.dict()

        # 合并旧配置和新数据
        potential_new_config_dict = {**current_config_dict, **new_data}

        try:
            # 使用合并后的数据创建新的 AppConfig 实例
            new_app_config = AppConfig(**potential_new_config_dict)

            # 为新的配置实例重新计算 VECTOR_DB_DRIVER
            self._determine_and_set_vector_db_driver(new_app_config)

            self._config_model = new_app_config  # 应用新的配置模型

            if auto_save:
                if not self.save():
                    print("警告: 配置已在内存中更新，但保存到文件失败。")
                    # 即使保存失败，内存中的配置已更新，返回True
            print("配置已成功更新。")
            return True
        except ValidationError as e:
            print(f"更新配置时验证错误: {e}")
            return False
        except Exception as e:
            print(f"更新配置时发生未知错误: {e}")
            return False


# 创建全局设置实例
settings = Settings(
    config_file_path=os.path.join(
        os.path.dirname(__file__), "files", "config.yaml"
    )
)

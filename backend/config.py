from typing import Optional, Dict, Any, List
import os
import pathlib
import yaml

def ensure_directories_exist(file_paths=None, dir_paths=None):
    """确保所有必要的目录存在，如果不存在则创建它们"""
    if file_paths:
        for file_path in file_paths:
            dir_name = os.path.dirname(file_path)
            if (dir_name and not os.path.exists(dir_name)):
                os.makedirs(dir_name, exist_ok=True)
                print(f"已创建目录: {dir_name}")
    
    if dir_paths:
        for dir_path in dir_paths:
            if dir_path and not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)
                print(f"已创建目录: {dir_path}")

class Settings:
    """
    应用配置类，支持单例模式、热加载、重载和设置变量功能
    所有配置统一从config.yaml加载，避免在代码中硬编码配置值
    """
    _instance = None  # 单例模式
    _config_dir = None  # 配置目录路径

    def __new__(cls, config_dir=None):
        if cls._instance is None:
            cls._instance = super(Settings, cls).__new__(cls)
            cls._instance._initialized = False
            # 在__new__中保存config_dir，确保即使在单例模式下也能使用新路径
            if config_dir is not None:
                cls._config_dir = config_dir
        elif config_dir is not None and cls._config_dir != config_dir:
            # 如果传入了新的配置目录且与当前不同，则更新路径并重置初始化标志
            cls._config_dir = config_dir
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, config_dir=None):
        if getattr(self, "_initialized", False):
            return

        # 默认配置目录路径
        if config_dir is None and self.__class__._config_dir is None:
            # 获取当前文件所在目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.__class__._config_dir = os.path.join(current_dir, 'config')
        elif config_dir is not None:
            # 如果明确传入了config_dir，使用它覆盖类变量中的路径
            self.__class__._config_dir = config_dir
            
        # 确保配置目录存在
        os.makedirs(self.__class__._config_dir, exist_ok=True)
        
        # 配置文件路径
        self.config_file = os.path.join(self.__class__._config_dir, 'config.yaml')
        
        # 初始化默认配置（只定义结构，不设置具体值）
        self._initialize_config_structure()
        
        # 从配置文件加载设置
        self.reload()
        
        # 确保所有必要的目录存在
        self._ensure_directories()
        
        self._initialized = True

    def _initialize_config_structure(self):
        """
        初始化配置结构，但不设置具体值
        实际的值将从config.yaml中加载
        
        注意: 这些是配置项的定义，具体值在 config.yaml 中设置
        YAML文件中已经包含的配置项:
        - AI_ENABLED: 是否启用AI功能 (布尔值)
        - AVAILABLE_VISION_MODELS: 可用的视觉模型列表 (字符串列表)
        - DB_PATH: 数据库路径 (字符串)
        - DESCRIPTION_INDEX_PATH: 描述向量索引文件路径 (字符串)
        - HOST: 服务器主机地址 (字符串)
        - PORT: 服务器端口号 (整数)
        - IMAGE_INDEX_PATH: 图像向量索引文件路径 (字符串)
        - IMAGE_VECTOR_CACHE_DIR: 图像向量缓存目录 (字符串)
        - MAX_CACHE_SIZE_GB: 最大缓存大小(GB) (浮点数，存储时为GB单位，使用时转换为字节)
        - MODEL_PATH: 模型路径 (字符串)
        - OPENAI_API_BASE: OpenAI API基础URL (字符串)
        - OPENAI_API_KEY: OpenAI API密钥 (字符串)
        - TEXT_VECTOR_CACHE_DIR: 文本向量缓存目录 (字符串)
        - TITLE_INDEX_PATH: 标题向量索引文件路径 (字符串)
        - UPLOAD_DIR: 上传图片存储目录 (字符串)
        - USE_CACHE: 是否使用缓存 (布尔值)
        - UUID_MAP_PATH: UUID映射文件路径 (字符串)
        - VECTOR_DIM: 向量维度 (整数)
        - VISION_MODEL: 当前使用的视觉模型 (字符串)
        """
        # 模型相关配置
        self.MODEL_PATH = ""  # 用于向量编码的模型路径，例如: "C:/models/jina-clip-v2"
        self.VECTOR_DIM = 1024  # 向量维度，大多数CLIP模型为1024
        
        # 图片存储相关配置
        self.UPLOAD_DIR = ""  # 上传图片存储目录，例如: "./data/images"
        
        # 索引文件路径
        self.TITLE_INDEX_PATH = ""  # 标题向量索引文件，例如: "./data/faiss/title_vectors.faiss"
        self.DESCRIPTION_INDEX_PATH = ""  # 描述向量索引文件，例如: "./data/faiss/description_vectors.faiss"
        self.IMAGE_INDEX_PATH = ""  # 图像向量索引文件，例如: "./data/faiss/image_vectors.faiss"
        self.UUID_MAP_PATH = ""  # UUID映射文件，例如: "./data/faiss/uuid_map.pickle"
        
        # 数据库配置
        self.DB_PATH = ""  # SQLite数据库路径，例如: "./data/db/smartimagefinder.db"
        
        # 缓存设置
        self.TEXT_VECTOR_CACHE_DIR = ""  # 文本向量缓存目录，例如: "./data/caches/text_vector_cache"
        self.IMAGE_VECTOR_CACHE_DIR = ""  # 图像向量缓存目录，例如: "./data/caches/image_vector_cache"
        self.USE_CACHE = True  # 是否启用缓存功能
        self.MAX_CACHE_SIZE_GB = 1.5  # 最大缓存大小，单位为GB (YAML中存储为1.5，使用时需乘以2**30转换为字节)
        
        # API设置
        self.OPENAI_API_KEY = ""  # OpenAI API密钥
        self.OPENAI_API_BASE = ""  # OpenAI API基础URL，例如: "https://api.openai.com/v1"
        
        # 视觉模型设置
        self.VISION_MODEL = ""  # 当前使用的视觉模型，例如: "Qwen/Qwen2.5-VL-32B-Instruct"
        self.AVAILABLE_VISION_MODELS = []  # 可用的视觉模型列表
        
        # AI功能开关
        self.AI_ENABLED = True  # 是否启用AI功能
        
        # 服务设置
        self.HOST = ""  # 服务器主机地址，例如: "0.0.0.0"
        self.PORT = 8000  # 服务器端口号

    def _ensure_directories(self):
        """确保所有必要的目录结构存在"""
        ensure_directories_exist(
            file_paths=[
                self.DB_PATH,
                self.TITLE_INDEX_PATH,
                self.DESCRIPTION_INDEX_PATH, 
                self.IMAGE_INDEX_PATH,
                self.UUID_MAP_PATH
            ],
            dir_paths=[
                self.TEXT_VECTOR_CACHE_DIR,
                self.IMAGE_VECTOR_CACHE_DIR,
                self.UPLOAD_DIR,
            ]
        )

    def reload(self) -> bool:
        """
        从配置文件重新加载设置
        
        Returns:
            bool: 加载是否成功
        """
        try:
            # 如果配置文件不存在，先保存当前配置
            if not os.path.exists(self.config_file):
                self.save()
                return True
                
            with open(self.config_file, 'r', encoding='utf-8') as file:
                config_data = yaml.safe_load(file)
                if not config_data:
                    return False
                    
                # 更新实例属性
                for key, value in config_data.items():
                    setattr(self, key, value)
                    
            return True
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            return False

    def save(self) -> bool:
        """
        将当前设置保存到配置文件
        
        Returns:
            bool: 保存是否成功
        """
        try:
            # 收集所有配置项（不再限制只保存大写属性）
            config_data = {}
            for key in dir(self):
                # 排除内部属性和方法
                if not key.startswith('_') and not callable(getattr(self, key)):
                    value = getattr(self, key)
                    # 确保值是可序列化的
                    if isinstance(value, (str, int, float, bool, list, dict, type(None))):
                        config_data[key] = value
            
            # 确保配置文件所在目录存在
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            # 保存到YAML文件
            with open(self.config_file, 'w', encoding='utf-8') as file:
                yaml.dump(config_data, file, allow_unicode=True, sort_keys=False)
                
            return True
        except Exception as e:
            print(f"保存配置文件失败: {e}")
            return False

    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置项值
        
        Args:
            key: 配置项名称
            default: 如未找到配置项时返回的默认值
            
        Returns:
            配置项的值或默认值
        """
        return getattr(self, key, default)

    def set(self, key: str, value: Any, auto_save: bool = False) -> bool:
        """
        设置配置项值
        
        Args:
            key: 配置项名称
            value: 配置项值
            auto_save: 是否自动保存到配置文件
            
        Returns:
            设置是否成功
        """
        try:
            setattr(self, key, value)
            if auto_save:
                return self.save()
            return True
        except Exception as e:
            print(f"设置配置项失败: {e}")
            return False

    def update(self, config_dict: Dict[str, Any], auto_save: bool = False) -> bool:
        """
        批量更新配置
        
        Args:
            config_dict: 包含配置项的字典
            auto_save: 是否自动保存到配置文件
            
        Returns:
            更新是否成功
        """
        try:
            for key, value in config_dict.items():
                self.set(key, value, auto_save=False)
                
            if auto_save:
                return self.save()
            return True
        except Exception as e:
            print(f"批量更新配置失败: {e}")
            return False

    def list_all(self) -> Dict[str, Any]:
        """
        列出所有配置项
        
        Returns:
            所有配置项的字典
        """
        result = {}
        for key in dir(self):
            # 排除内部属性和方法（不再限制只列出大写属性）
            if not key.startswith('_') and not callable(getattr(self, key)):
                value = getattr(self, key)
                # 特殊处理MAX_CACHE_SIZE_GB，确保它是以GB为单位而不是字节
                result[key] = value
        return result

    def reset_to_default(self, auto_save: bool = True) -> bool:
        """
        重置为默认配置
        
        Args:
            auto_save: 是否自动保存到配置文件
            
        Returns:
            重置是否成功
        """
        try:
            self._initialize_config_structure()
            if auto_save:
                return self.save()
            return True
        except Exception as e:
            print(f"重置配置失败: {e}")
            return False

# 创建全局设置实例
settings = Settings()

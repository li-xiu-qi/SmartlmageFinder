"""
向量能力门

统一判断向量功能是否可用，永不抛异常，永不 SystemExit。
结果缓存，启动时探测一次。
"""
import os
import sqlite3
import threading
from dataclasses import dataclass
from typing import Optional

from ..config import settings
from ..config.platform_detector import PlatformDetector


@dataclass
class VectorStatus:
    """向量引擎完整状态"""
    enabled: bool = False
    driver_available: bool = False
    driver_path: str = ""
    driver_error: str = ""
    driver_version: str = ""
    model_available: bool = False
    model_path: str = ""
    model_error: str = ""
    model_dimension: int = 0

    def to_dict(self) -> dict:
        return {
            "enabled": self.enabled,
            "driver": {
                "available": self.driver_available,
                "path": self.driver_path,
                "error": self.driver_error,
                "version": self.driver_version,
            },
            "model": {
                "available": self.model_available,
                "path": self.model_path,
                "error": self.model_error,
                "dimension": self.model_dimension,
            },
        }


_lock = threading.Lock()
_cached_status: Optional[VectorStatus] = None


def _resolve_driver_path() -> Optional[str]:
    """根据配置解析 sqlite-vec 驱动路径，失败返回 None"""
    try:
        config = settings.get_config()
        driver_dir = getattr(config, "VECTOR_DB_DRIVER_DIR", None)
        if not driver_dir:
            return None
        project_root = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        )
        rel = driver_dir.lstrip("./").lstrip(".\\")
        abs_dir = os.path.normpath(os.path.join(project_root, rel))
        return PlatformDetector.get_driver_path(abs_dir)
    except Exception:
        return None


def _probe_driver(driver_path: Optional[str]) -> VectorStatus:
    """探测 sqlite-vec 驱动是否可加载"""
    status = VectorStatus()
    status.driver_path = driver_path or ""

    if not driver_path:
        status.driver_error = "VECTOR_DB_DRIVER 未配置或未找到适用于当前平台的驱动"
        return status

    if not os.path.exists(driver_path):
        status.driver_error = f"驱动文件不存在: {driver_path}"
        return status

    # 尝试在内存数据库上加载扩展
    try:
        conn = sqlite3.connect(":memory:")
        conn.enable_load_extension(True)
        conn.execute(f"SELECT load_extension('{driver_path}')")
        cur = conn.cursor()
        cur.execute("SELECT vec_version()")
        row = cur.fetchone()
        status.driver_version = row[0] if row else "未知"
        status.driver_available = True
        conn.close()
    except Exception as e:
        status.driver_error = f"驱动加载失败: {e}"
    return status


def _probe_model() -> tuple:
    """探测 embedding 模型是否可用，返回 (available, path, error, dimension)"""
    try:
        config = settings.get_config()
        model_path = getattr(config, "MODEL_PATH", None)
        if not model_path:
            return False, "", "MODEL_PATH 未配置", 0

        # 解析为绝对路径
        if not os.path.isabs(model_path):
            project_root = os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            )
            model_path = os.path.normpath(os.path.join(project_root, model_path.lstrip("./")))

        if not os.path.isdir(model_path):
            return False, model_path, f"模型目录不存在: {model_path}", 0

        # 检查是否有模型文件（至少要有 config.json 或 model file）
        has_config = os.path.exists(os.path.join(model_path, "config.json"))
        has_modules = os.path.exists(os.path.join(model_path, "modules.json"))
        has_weights = any(
            f.endswith((".safetensors", ".bin", ".pt"))
            for f in os.listdir(model_path)
        ) if os.path.isdir(model_path) else False

        if not (has_config or has_modules or has_weights):
            return False, model_path, f"模型目录缺少必要文件: {model_path}", 0

        # 维度从配置读取，不加载模型
        dim = getattr(config, "EMBEDDING_DIMENSION", None) or 0
        return True, model_path, "", dim
    except Exception as e:
        return False, "", f"模型探测异常: {e}", 0


def get_vector_status(force_refresh: bool = False) -> VectorStatus:
    """获取向量引擎状态（缓存）"""
    global _cached_status
    with _lock:
        if _cached_status is not None and not force_refresh:
            return _cached_status

        status = VectorStatus()

        # 探测驱动
        driver_path = _resolve_driver_path()
        status = _probe_driver(driver_path)

        # 探测模型
        model_available, model_path, model_error, model_dim = _probe_model()
        status.model_available = model_available
        status.model_path = model_path
        status.model_error = model_error
        status.model_dimension = model_dim

        # 综合判断
        status.enabled = status.driver_available and status.model_available

        _cached_status = status
        return status


def is_vector_enabled() -> bool:
    """向量功能是否可用（不抛异常）"""
    return get_vector_status().enabled


# 延迟导入，避免循环依赖
_provider_instance = None
_store_instance = None


def get_provider():
    """获取 EmbeddingProvider 实例（延迟初始化）"""
    global _provider_instance
    if _provider_instance is None:
        from .provider import SentenceTransformerProvider
        _provider_instance = SentenceTransformerProvider()
    return _provider_instance


def get_store():
    """获取 VectorStore 实例（延迟初始化）"""
    global _store_instance
    if _store_instance is None:
        from .store import SqliteVecStore
        _store_instance = SqliteVecStore()
    return _store_instance

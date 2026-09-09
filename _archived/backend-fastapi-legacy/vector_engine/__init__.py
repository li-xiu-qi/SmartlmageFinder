"""
向量引擎抽象层

定义两个接口：
  - EmbeddingProvider：负责将文本/图片编码为向量
  - VectorStore：负责向量的存储与检索

默认实现：
  - SentenceTransformerProvider：基于本地 SentenceTransformer 模型
  - SqliteVecStore：基于 sqlite-vec 扩展

能力门：
  - is_vector_enabled()：统一判断向量功能是否可用
  - 缺模型或缺扩展时均返回 False，不崩溃
"""
from .base import EmbeddingProvider, VectorStore, VectorUnavailableError
from .provider import SentenceTransformerProvider
from .store import SqliteVecStore
from .capability import (
    is_vector_enabled,
    get_provider,
    get_store,
    get_vector_status,
    VectorStatus,
)

__all__ = [
    "EmbeddingProvider",
    "VectorStore",
    "VectorUnavailableError",
    "SentenceTransformerProvider",
    "SqliteVecStore",
    "is_vector_enabled",
    "get_provider",
    "get_store",
    "get_vector_status",
    "VectorStatus",
]

"""迁移配置最小加载：只读取所需键，无额外兼容逻辑。"""
from pydantic import BaseModel
from typing import Optional
import yaml, os


class MigrationConfig(BaseModel):
	old_model_path: Optional[str] = None
	old_embedding_dim: Optional[int] = None
	new_model_path: str
	new_embedding_dim: Optional[int] = None
	db_path: Optional[str] = None
	batch_size: int = 64


def load_migration_config(path: str) -> MigrationConfig:
	if not os.path.exists(path):
		raise FileNotFoundError(f"迁移配置文件不存在: {path}")
	with open(path, "r", encoding="utf-8") as f:
		data = yaml.safe_load(f) or {}
	if not data.get("new_model_path"):
		raise ValueError("migration.yaml 中 new_model_path 必填")
	if not data.get("batch_size"):
		data["batch_size"] = 64
	return MigrationConfig(**data)


__all__ = ["MigrationConfig", "load_migration_config"]

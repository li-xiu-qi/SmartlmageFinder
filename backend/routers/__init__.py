# routers模块初始化
# 只需导入主路由，子路由已在search/__init__.py中组织
from .search import router as search_router
from .images import router as images_router
from .system import router as system_router
from .tags import router as tags_router
from .ai_router import router as ai_router
from .metadata import router as metadata_router
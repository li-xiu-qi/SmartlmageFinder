from fastapi import APIRouter
from .similar_search import router as similar_search_router
from .unified_search import router as unified_search_router

# 创建一个主路由，包含所有搜索相关子路由
router = APIRouter(prefix="/api/v1/search", tags=["search"])

# 包含各个子路由
router.include_router(unified_search_router)  # 新的统一搜索路由
router.include_router(similar_search_router)  # 相似搜索路由

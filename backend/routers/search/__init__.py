from fastapi import APIRouter
from .text_search import router as text_search_router
from .image_search import router as image_search_router
from .vector_search import router as vector_search_router
from .filtered_search import router as filtered_search_router
from .similar_search import router as similar_search_router
from .unified_search import router as unified_search_router

# 创建一个主路由，包含所有搜索相关子路由
router = APIRouter(prefix="/api/v1/search", tags=["search"])

# 包含各个子路由
router.include_router(unified_search_router)  # 新的统一搜索路由
router.include_router(text_search_router)
router.include_router(image_search_router)
router.include_router(vector_search_router)
router.include_router(filtered_search_router)
router.include_router(similar_search_router)

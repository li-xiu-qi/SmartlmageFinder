from fastapi import APIRouter

# 子路由
from .analysis import router as analysis_router
from .recommendation import router as recommendation_router

# 统一 AI 路由前缀与标签
router = APIRouter(prefix="/api/v1/ai", tags=["ai"])

# 聚合子路由
router.include_router(analysis_router)
router.include_router(recommendation_router)

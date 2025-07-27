from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

from app.routers.ai_recommendations import router as ai_router
from app.config import settings

# 创建FastAPI应用
app = FastAPI(
    title="AI智能图片推荐服务",
    description="基于SmartImageFinder的智能图片推荐和AI分析服务",
    version="1.0.0",
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，生产环境应该配置具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含路由
app.include_router(ai_router)

@app.get("/")
async def root():
    return {
        "message": "AI智能图片推荐服务已启动",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ai-recommendation"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        log_level="info",
        reload=True
    )
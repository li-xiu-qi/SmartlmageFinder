from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import time
import uvicorn
import os

from backend.routers import images, search, tags, metadata, ai, system
from backend.config import settings  # 导入配置
from backend.db import init_db  # 导入数据库初始化函数
from backend.vector_db import init_indices  # 导入向量索引初始化函数

# 初始化数据库
init_db()

# 初始化向量索引
init_indices()

# 创建FastAPI应用
app = FastAPI(
   
)

# 配置CORS
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",  # Vite默认端口
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# 挂载静态文件目录
app.mount("/static/images", StaticFiles(directory=settings.UPLOAD_DIR), name="images")

# 包含路由模块
app.include_router(images.router, prefix="/api/v1", tags=["images"])
app.include_router(search.router, prefix="/api/v1", tags=["search"])
app.include_router(tags.router, prefix="/api/v1", tags=["tags"])
app.include_router(metadata.router, prefix="/api/v1", tags=["metadata"])
app.include_router(ai.router, prefix="/api/v1", tags=["ai"])
app.include_router(system.router, prefix="/api/v1", tags=["system"])

# 请求处理时间中间件
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "data": None,
            "error": {
                "code": "SYSTEM_ERROR",
                "message": f"系统错误: {str(exc)}",
            },
            "metadata": {}
        }
    )

@app.get("/api/v1/")
async def api_root():
    return {
        "status": "success",
        "data": {
            "message": "欢迎使用SmartImageFinder API",
            "version": "1.0.0",
        },
        "error": None,
        "metadata": {}
    }
    
    
@app.get("/")
async def root():
    # 返回一个简单的欢迎信息html
    
    return  """
    <html>
        <head>
            <title>SmartImageFinder API</title>
        </head>
        <body>
            <h1>欢迎使用 SmartImageFinder API</h1>
            <p>API 文档请访问: <a href="/docs">/docs</a></p>
        </body>
    </html>
    """
    

if __name__ == "__main__":
    # 启动FastAPI应用
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, log_level="info",reload=True)
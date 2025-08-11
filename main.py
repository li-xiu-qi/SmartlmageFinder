from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import time
import uvicorn
import os
import argparse

from backend.routers import ai_router, images, search, tags, system, metadata # 导入配置
from backend.config import settings  # 导入配置
from backend.db_func.core.database import init_db  # 导入数据库初始化函数
from backend.db_func.core.connection import initialize_connection_pool  # 导入连接池初始化函数

# 初始化数据库
init_db()

# 初始化数据库连接池
db_path = settings.get_config().DB_PATH
initialize_connection_pool(db_path, max_connections=20)  # 设置最大连接数为20


# 创建FastAPI应用
app = FastAPI(
    title="SmartImageFinder API",
    description="SmartImageFinder API for image search and analysis",
    version="1.0.0",
)

# 初始化Jinja2模板
templates = Jinja2Templates(directory="templates")

# 配置CORS - 允许所有源访问
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# 挂载静态文件目录
app.mount("/static/images", StaticFiles(directory=settings.get_config().UPLOAD_DIR), name="images")

# 包含路由模块
app.include_router(images.router, prefix="/api/v1/images", tags=["images"])
app.include_router(search.router)
app.include_router(tags.router)
app.include_router(ai_router)
app.include_router(system.router)
app.include_router(metadata.router)

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
    import traceback
    error_traceback = traceback.format_exc()
    print(f"全局异常处理器捕获异常:")
    print(f"请求URL: {request.url}")
    print(f"请求方法: {request.method}")
    print(f"异常类型: {type(exc).__name__}")
    print(f"异常信息: {str(exc)}")
    print(f"异常堆栈:")
    print(error_traceback)
    
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "data": None,
            "error": {
                "code": "SYSTEM_ERROR",
                "message": f"系统错误: {str(exc)}",
                "details": error_traceback if exc else None
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
async def root(request: Request):
    # 使用Jinja2模板渲染欢迎页面
    return templates.TemplateResponse("index.html", {
        "request": request,
        "version": app.version,
        "status": "运行中"
    })
    

if __name__ == "__main__":
    # 启动FastAPI应用：优先级 CLI > 环境变量 > 默认值
    parser = argparse.ArgumentParser(description="Run SmartImageFinder API server")
    parser.add_argument("--host", type=str, default=None, help="Host to bind (overrides env)")
    parser.add_argument("--port", type=int, default=None, help="Port to bind (overrides env)")
    parser.add_argument("--reload", action="store_true", help="Enable hot reload (development mode)")
    args, _ = parser.parse_known_args()

    # 环境变量读取
    env_host = os.getenv("SIF_HOST")
    env_port = os.getenv("SIF_PORT")
    env_reload = os.getenv("SIF_RELOAD")

    # 解析得到最终值
    host = args.host or env_host or "0.0.0.0"
    try:
        port = args.port or (int(env_port) if env_port else None) or 8000
    except ValueError:
        port = args.port or 8000
    reload_enabled = args.reload or (str(env_reload).strip() in ("1", "true", "True"))

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        log_level="info",
        reload=reload_enabled,
    )

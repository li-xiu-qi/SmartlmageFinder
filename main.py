from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import time
import uvicorn
import os

from backend.routers import ai_router, images, search, tags, system, metadata, ai_recommendation_router # 导入配置
from backend.config import settings  # 导入配置
from backend.db_func.core import init_db  # 导入数据库初始化函数
from backend.db_func.connection_pool import initialize_connection_pool  # 导入连接池初始化函数

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
app.include_router(images.router)
app.include_router(search.router)
app.include_router(tags.router)
app.include_router(ai_router)
app.include_router(ai_recommendation_router, prefix="/api/v1/ai")
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
    # 启动FastAPI应用
    uvicorn.run("main:app", host=settings.get_config().HOST, port=settings.get_config().PORT, log_level="info",reload=True)

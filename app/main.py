from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import os

from app.api.routes import router
from app.models.database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时执行
    init_db()
    yield
    # 关闭时执行
    pass

app = FastAPI(
    title="本地智能文档问答助手",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# 添加根路由
@app.get("/")
async def root():
    return {
        "message": "欢迎使用本地智能文档问答助手",
        "docs_url": "/docs",
        "api_prefix": "/api"
    }

# 注册路由
app.include_router(router, prefix="/api")

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    ) 
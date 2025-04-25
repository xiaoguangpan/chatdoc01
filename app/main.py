from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Request
from contextlib import asynccontextmanager
import uvicorn
import os

from app.api.routes import router
from app.models.database import init_db

# 初始化模板
templates = Jinja2Templates(directory="app/templates")

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
origins = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "null",  # 允许通过文件系统直接打开的页面
    "file://"  # 允许通过文件系统直接打开的页面
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# 添加根路由
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# 注册路由
app.include_router(router, prefix="/api")

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    ) 
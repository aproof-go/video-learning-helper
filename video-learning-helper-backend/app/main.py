from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os

from app.config import settings
from app.api.v1.api import api_router

# 创建FastAPI应用
app = FastAPI(
    title="Video Learning Helper API",
    description="AI拉片助手后端API",
    version="1.0.0",
    debug=settings.debug,
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含API路由
app.include_router(api_router, prefix="/api/v1")

# 创建上传目录
os.makedirs(settings.upload_dir, exist_ok=True)


@app.get("/")
async def root():
    """根路径"""
    return {"message": "Video Learning Helper API v1.0.0"}


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    ) 
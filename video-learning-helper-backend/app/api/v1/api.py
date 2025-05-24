from fastapi import APIRouter
from app.api.v1 import auth, videos

api_router = APIRouter()

# 包含认证路由
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])

# 包含视频管理路由
api_router.include_router(videos.router, prefix="/videos", tags=["videos"])

# 包含分析任务路由
api_router.include_router(videos.router, prefix="/analysis", tags=["analysis"]) 
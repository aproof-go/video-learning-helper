from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import shutil
import uuid
from pathlib import Path
import json

from app.database_supabase import get_db
from app.core.security import decode_access_token
from app.crud.video import video_crud, analysis_task_crud
from app.schemas.video import (
    VideoResponse, VideoCreate, VideoUpdate, 
    AnalysisTaskResponse, AnalysisTaskCreate, AnalysisTaskUpdate,
    UploadResponse, VideoWithTasks
)

router = APIRouter()
security = HTTPBearer()

# 配置上传目录
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_VIDEO_FORMATS = {".mp4", ".avi", ".mov", ".wmv", ".flv", ".webm", ".mkv"}
MAX_FILE_SIZE = 1024 * 1024 * 1024  # 1GB

async def get_current_user_id(token: str = Depends(security)):
    """获取当前用户ID"""
    try:
        payload = decode_access_token(token.credentials)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="无效的token")
        return user_id
    except Exception:
        raise HTTPException(status_code=401, detail="无效的token")

def get_file_info(file_path: str):
    """获取视频文件信息（这里简化处理，实际应该使用ffprobe）"""
    # 实际实现中应该使用 ffprobe 或类似工具获取视频信息
    file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
    return {
        "file_size": file_size,
        "duration": None,  # 需要ffprobe
        "resolution": None,  # 需要ffprobe
        "fps": None,  # 需要ffprobe
        "format": Path(file_path).suffix[1:].lower()
    }

# 视频管理API
@router.post("/upload", response_model=UploadResponse)
async def upload_video(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: str = Form(""),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """上传视频文件"""
    
    # 验证文件格式
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_VIDEO_FORMATS:
        raise HTTPException(
            status_code=400, 
            detail=f"不支持的文件格式。支持的格式: {', '.join(ALLOWED_VIDEO_FORMATS)}"
        )
    
    # 验证文件大小
    if file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="文件大小超过限制")
    
    try:
        # 生成唯一文件名
        file_id = str(uuid.uuid4())
        filename = f"{file_id}{file_ext}"
        file_path = UPLOAD_DIR / filename
        
        # 保存文件
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 获取文件大小
        file_size = file_path.stat().st_size
        
        # 创建视频记录
        video_data = VideoCreate(
            title=title,
            filename=file.filename,
            file_size=file_size,
            format=file_ext[1:]  # 去掉点号
        )
        
        video = video_crud.create_video(db, video_data, user_id)
        
        return UploadResponse(
            message="视频上传成功",
            video_id=str(video.id)
        )
        
    except Exception as e:
        # 清理已上传的文件
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")

@router.get("/", response_model=List[VideoResponse])
async def get_user_videos(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """获取用户的视频列表"""
    videos = video_crud.get_user_videos(db, user_id, skip, limit)
    return videos

@router.get("/{video_id}", response_model=VideoResponse)
async def get_video(
    video_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """获取视频详情"""
    video = video_crud.get_video(db, video_id)
    if not video:
        raise HTTPException(status_code=404, detail="视频不存在")
    
    if video.user_id != user_id:
        raise HTTPException(status_code=403, detail="无权访问此视频")
    
    return video

@router.put("/{video_id}", response_model=VideoResponse)
async def update_video(
    video_id: str,
    video_update: VideoUpdate,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """更新视频信息"""
    video = video_crud.get_video(db, video_id)
    if not video:
        raise HTTPException(status_code=404, detail="视频不存在")
    
    if video.user_id != user_id:
        raise HTTPException(status_code=403, detail="无权修改此视频")
    
    updated_video = video_crud.update_video(db, video_id, video_update)
    return updated_video

@router.delete("/{video_id}")
async def delete_video(
    video_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """删除视频"""
    video = video_crud.get_video(db, video_id)
    if not video:
        raise HTTPException(status_code=404, detail="视频不存在")
    
    if video.user_id != user_id:
        raise HTTPException(status_code=403, detail="无权删除此视频")
    
    # 删除文件
    try:
        file_path = UPLOAD_DIR / f"{video_id}{Path(video.filename).suffix}"
        if file_path.exists():
            file_path.unlink()
    except Exception as e:
        print(f"删除文件失败: {e}")
    
    # 删除数据库记录
    success = video_crud.delete_video(db, video_id)
    if not success:
        raise HTTPException(status_code=500, detail="删除失败")
    
    return {"message": "视频删除成功"}

# 分析任务相关路由
@router.post("/analysis/tasks", response_model=AnalysisTaskResponse)
async def create_analysis_task(
    task_data: AnalysisTaskCreate,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """创建分析任务"""
    # 验证视频是否存在且属于当前用户
    video = video_crud.get_video(db, task_data.video_id)
    if not video:
        raise HTTPException(status_code=404, detail="视频不存在")
    
    if video.user_id != user_id:
        raise HTTPException(status_code=403, detail="无权访问此视频")
    
    task = analysis_task_crud.create_task(db, task_data, user_id)
    return task

@router.get("/analysis/tasks", response_model=List[AnalysisTaskResponse])
async def get_user_analysis_tasks(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """获取用户的分析任务列表"""
    tasks = analysis_task_crud.get_user_tasks(db, user_id, skip, limit)
    return tasks

@router.get("/analysis/tasks/{task_id}", response_model=AnalysisTaskResponse)
async def get_analysis_task(
    task_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """获取分析任务详情"""
    task = analysis_task_crud.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    if task.user_id != user_id:
        raise HTTPException(status_code=403, detail="无权访问此任务")
    
    return task

@router.get("/analysis/videos/{video_id}/tasks", response_model=List[AnalysisTaskResponse])
async def get_video_analysis_tasks(
    video_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """获取视频的分析任务列表"""
    # 验证视频是否存在且属于当前用户
    video = video_crud.get_video(db, video_id)
    if not video:
        raise HTTPException(status_code=404, detail="视频不存在")
    
    if video.user_id != user_id:
        raise HTTPException(status_code=403, detail="无权访问此视频")
    
    tasks = analysis_task_crud.get_video_tasks(db, video_id)
    return tasks 
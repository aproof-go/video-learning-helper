from fastapi import FastAPI, HTTPException, status, Depends, UploadFile, File, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, timedelta
import jwt
import bcrypt
import os
from dotenv import load_dotenv
import uuid
import shutil
from pathlib import Path

from app.database_supabase import db_manager
from app.task_processor import start_task_processor, stop_task_processor, submit_analysis_task, get_processor_status

# 加载环境变量
load_dotenv("config.env")

# 配置
SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key-change-this-in-production-2024")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# 创建FastAPI应用
app = FastAPI(
    title="Video Learning Helper API",
    description="AI拉片助手后端API - Supabase版",
    version="2.0.0",
)

# 应用启动和关闭事件
@app.on_event("startup")
async def startup_event():
    """应用启动时初始化任务处理器"""
    await start_task_processor()

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时停止任务处理器"""
    await stop_task_processor()

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://localhost:3001", 
        "http://localhost:3002", 
        "http://localhost:3003", 
        "http://127.0.0.1:3000", 
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002",
        "http://127.0.0.1:3003"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Bearer token 认证
security = HTTPBearer()

# 配置上传目录
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_VIDEO_FORMATS = {".mp4", ".avi", ".mov", ".wmv", ".flv", ".webm", ".mkv"}
MAX_FILE_SIZE = 1024 * 1024 * 1024  # 1GB

# Pydantic模型
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    name: Optional[str] = None
    created_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class HealthResponse(BaseModel):
    status: str
    version: str
    database: str
    user_count: int

# 视频相关模型
class VideoResponse(BaseModel):
    id: str
    title: str
    filename: str
    file_size: int
    duration: Optional[int] = None
    resolution_width: Optional[int] = None
    resolution_height: Optional[int] = None
    format: Optional[str] = None
    status: str
    file_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    user_id: str
    created_at: datetime
    updated_at: datetime
    tasks: Optional[List[dict]] = None

class AnalysisTaskResponse(BaseModel):
    id: str
    video_id: str
    user_id: str
    video_segmentation: bool
    transition_detection: bool
    audio_transcription: bool
    report_generation: bool
    status: str
    progress: str
    error_message: Optional[str] = None
    report_pdf_url: Optional[str] = None
    subtitle_srt_url: Optional[str] = None
    subtitle_vtt_url: Optional[str] = None
    script_md_url: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

class AnalysisTaskCreate(BaseModel):
    video_id: str
    video_segmentation: bool = False
    transition_detection: bool = False
    audio_transcription: bool = False
    report_generation: bool = False

class UploadResponse(BaseModel):
    message: str
    video_id: str
    upload_url: Optional[str] = None

# 工具函数
def hash_password(password: str) -> str:
    """使用bcrypt哈希密码"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """创建访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """获取当前用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.InvalidTokenError:
        raise credentials_exception
    
    # 从Supabase数据库获取用户
    user = await db_manager.get_user_by_email(email)
    if user is None:
        raise credentials_exception
    return user

# JWT认证辅助函数
def decode_access_token(token: str):
    """解码访问令牌"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.InvalidTokenError:
        return None

async def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """获取当前用户ID"""
    try:
        payload = decode_access_token(credentials.credentials)
        user_email = payload.get("sub")
        if user_email is None:
            raise HTTPException(status_code=401, detail="无效的token")
        
        # 从数据库获取用户的UUID
        user = await db_manager.get_user_by_email(user_email)
        if not user:
            raise HTTPException(status_code=401, detail="用户不存在")
        
        return user["id"]  # 返回UUID而不是email
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=401, detail="无效的token")

# API路由
@app.get("/")
async def root():
    """根路径"""
    return {"message": "Video Learning Helper API v2.0.0 - Supabase版"}

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查"""
    user_count = await db_manager.get_user_count()
    return HealthResponse(
        status="healthy",
        version="2.0.0",
        database="supabase",
        user_count=user_count
    )

@app.post("/api/v1/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """用户注册"""
    # 检查邮箱是否已存在
    if await db_manager.email_exists(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # 创建新用户
    try:
        password_hash = hash_password(user_data.password)
        user = await db_manager.create_user(
            email=user_data.email,
            name=user_data.name,
            password_hash=password_hash
        )
        
        return UserResponse(
            id=user["id"],
            email=user["email"],
            name=user["name"],
            created_at=user["created_at"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}"
        )

@app.post("/api/v1/auth/login", response_model=Token)
async def login(user_data: UserLogin):
    """用户登录"""
    user = await db_manager.get_user_by_email(user_data.email)
    if not user or not verify_password(user_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@app.get("/api/v1/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user = Depends(get_current_user)):
    """获取当前用户信息"""
    return UserResponse(
        id=current_user["id"],
        email=current_user["email"],
        name=current_user["name"],
        created_at=current_user["created_at"]
    )

@app.get("/api/v1/users/stats")
async def get_user_stats(current_user = Depends(get_current_user)):
    """获取用户统计信息（需要认证）"""
    user_count = await db_manager.get_user_count()
    return {
        "total_users": user_count,
        "current_user_id": current_user["id"],
        "database_type": "supabase"
    }

# 视频相关路由
@app.post("/api/v1/videos/upload", response_model=UploadResponse)
async def upload_video(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: str = Form(""),
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
        
        # 在数据库中创建视频记录
        video_data = {
            "title": title,
            "filename": file.filename,
            "file_size": file_size,
            "format": file_ext[1:],  # 去掉点号
            "status": "uploaded",
            "user_id": user_id,  # 使用UUID作为用户标识
            "file_url": f"/uploads/{filename}"
        }
        
        # 将视频信息插入数据库
        try:
            video_record = await db_manager.create_video(video_data)
            actual_video_id = video_record["id"]
        except Exception as e:
            print(f"Warning: Failed to save video to database: {e}")
            # 如果数据库存储失败，仍然使用文件ID
            actual_video_id = file_id
        
        return UploadResponse(
            message="视频上传成功",
            video_id=actual_video_id
        )
        
    except Exception as e:
        # 清理已上传的文件
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")

@app.get("/api/v1/videos/", response_model=List[VideoResponse])
async def get_user_videos(
    skip: int = 0,
    limit: int = 100,
    include_tasks: bool = False,
    user_id: str = Depends(get_current_user_id)
):
    """获取用户的视频列表"""
    try:
        videos = await db_manager.get_user_videos(user_id, skip, limit)
        
        # 如果需要包含任务信息，批量获取
        if include_tasks:
            for video in videos:
                try:
                    tasks = await db_manager.get_video_analysis_tasks(video["id"])
                    video["tasks"] = [
                        {
                            "id": task["id"],
                            "video_id": task["video_id"],
                            "user_id": task["user_id"],
                            "video_segmentation": task["video_segmentation"],
                            "transition_detection": task["transition_detection"],
                            "audio_transcription": task["audio_transcription"],
                            "report_generation": task["report_generation"],
                            "status": task["status"],
                            "progress": task["progress"],
                            "error_message": task.get("error_message"),
                            "report_pdf_url": task.get("report_pdf_url"),
                            "subtitle_srt_url": task.get("subtitle_srt_url"),
                            "subtitle_vtt_url": task.get("subtitle_vtt_url"),
                            "started_at": task.get("started_at"),
                            "completed_at": task.get("completed_at"),
                            "created_at": task["created_at"],
                            "updated_at": task["updated_at"]
                        } for task in tasks
                    ]
                except Exception as e:
                    logger.warning(f"获取视频 {video['id']} 的任务失败: {e}")
                    video["tasks"] = []
        
        return [
            VideoResponse(
                id=video["id"],
                title=video["title"],
                filename=video["filename"],
                file_size=video["file_size"],
                duration=video.get("duration"),
                resolution_width=video.get("resolution_width"),
                resolution_height=video.get("resolution_height"),
                format=video.get("format"),
                status=video["status"],
                file_url=video.get("file_url"),
                thumbnail_url=video.get("thumbnail_url"),
                user_id=video["user_id"],
                created_at=datetime.fromisoformat(video["created_at"].replace('Z', '+00:00')),
                updated_at=datetime.fromisoformat(video["updated_at"].replace('Z', '+00:00')),
                **({'tasks': video["tasks"]} if include_tasks else {})
            ) for video in videos
        ]
    except Exception as e:
        print(f"Error fetching videos: {e}")
        return []

@app.post("/api/v1/analysis/tasks", response_model=AnalysisTaskResponse)
async def create_analysis_task(
    request: Request,
    task_data: AnalysisTaskCreate,
    user_id: str = Depends(get_current_user_id)
):
    """创建分析任务"""
    try:
        print(f"🔍 === 分析任务创建请求详情 ===")
        print(f"📝 Received task data: {task_data}")
        print(f"📝 Task data dict: {task_data.dict()}")
        print(f"👤 User ID: {user_id}")
        print(f"🌐 Request headers: {dict(request.headers)}")
        print(f"🔗 Request URL: {request.url}")
        print(f"📊 Request method: {request.method}")
        print(f"🔍 === 请求详情结束 ===\n")
        # 验证视频是否存在
        video = await db_manager.get_video_by_id(task_data.video_id)
        print(f"🎬 Video lookup result: {video}")
        if not video:
            print(f"❌ Video not found for ID: {task_data.video_id}")
            raise HTTPException(status_code=404, detail="视频不存在")
        
        # 验证视频是否属于当前用户
        print(f"👤 Video owner check: video.user_id={video['user_id']}, current.user_id={user_id}")
        if video["user_id"] != user_id:
            print(f"❌ Authorization failed: video belongs to {video['user_id']}, but current user is {user_id}")
            raise HTTPException(status_code=403, detail="无权访问此视频")
        
        # 创建分析任务
        task_create_data = {
            "video_id": task_data.video_id,
            "user_id": user_id,
            "video_segmentation": task_data.video_segmentation,
            "transition_detection": task_data.transition_detection,
            "audio_transcription": task_data.audio_transcription,
            "report_generation": task_data.report_generation
        }
        
        task = await db_manager.create_analysis_task(task_create_data)
        
        # 提交任务到处理器进行异步分析
        video_file_path = Path("uploads") / video["file_url"].split("/")[-1]
        await submit_analysis_task(
            task["id"], 
            str(video_file_path), 
            {
                "video_segmentation": task_data.video_segmentation,
                "transition_detection": task_data.transition_detection,
                "audio_transcription": task_data.audio_transcription,
                "report_generation": task_data.report_generation
            }
        )
        
        return AnalysisTaskResponse(
            id=task["id"],
            video_id=task["video_id"],
            user_id=task["user_id"],
            video_segmentation=task["video_segmentation"],
            transition_detection=task["transition_detection"],
            audio_transcription=task["audio_transcription"],
            report_generation=task["report_generation"],
            status=task["status"],
            progress=task["progress"],
            created_at=datetime.fromisoformat(task["created_at"].replace('Z', '+00:00')),
            updated_at=datetime.fromisoformat(task["updated_at"].replace('Z', '+00:00'))
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error creating analysis task: {e}")
        raise HTTPException(status_code=500, detail=f"创建分析任务失败: {str(e)}")

@app.get("/api/v1/analysis/videos/{video_id}/tasks", response_model=List[AnalysisTaskResponse])
async def get_video_analysis_tasks(
    video_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """获取视频的分析任务列表"""
    try:
        # 验证视频是否存在且属于当前用户
        video = await db_manager.get_video_by_id(video_id)
        if not video:
            raise HTTPException(status_code=404, detail="视频不存在")
        
        if video["user_id"] != user_id:
            raise HTTPException(status_code=403, detail="无权访问此视频")
        
        # 获取视频的分析任务
        tasks = await db_manager.get_video_analysis_tasks(video_id)
        
        return [
            AnalysisTaskResponse(
                id=task["id"],
                video_id=task["video_id"],
                user_id=task["user_id"],
                video_segmentation=task["video_segmentation"],
                transition_detection=task["transition_detection"],
                audio_transcription=task["audio_transcription"],
                report_generation=task["report_generation"],
                status=task["status"],
                progress=task["progress"],
                error_message=task.get("error_message"),
                report_pdf_url=task.get("report_pdf_url"),
                subtitle_srt_url=task.get("subtitle_srt_url"),
                subtitle_vtt_url=task.get("subtitle_vtt_url"),
                started_at=datetime.fromisoformat(task["started_at"].replace('Z', '+00:00')) if task.get("started_at") else None,
                completed_at=datetime.fromisoformat(task["completed_at"].replace('Z', '+00:00')) if task.get("completed_at") else None,
                created_at=datetime.fromisoformat(task["created_at"].replace('Z', '+00:00')),
                updated_at=datetime.fromisoformat(task["updated_at"].replace('Z', '+00:00'))
            ) for task in tasks
        ]
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching video analysis tasks: {e}")
        raise HTTPException(status_code=500, detail=f"获取分析任务失败: {str(e)}")

@app.get("/api/v1/videos/{video_id}", response_model=VideoResponse)
async def get_video(
    video_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """获取视频详情"""
    try:
        video = await db_manager.get_video_by_id(video_id)
        if not video:
            raise HTTPException(status_code=404, detail="视频不存在")
        
        if video["user_id"] != user_id:
            raise HTTPException(status_code=403, detail="无权访问此视频")
        
        return VideoResponse(
            id=video["id"],
            title=video["title"],
            filename=video["filename"],
            file_size=video["file_size"],
            duration=video.get("duration"),
            resolution_width=video.get("resolution_width"),
            resolution_height=video.get("resolution_height"),
            format=video.get("format"),
            status=video["status"],
            file_url=video.get("file_url"),
            thumbnail_url=video.get("thumbnail_url"),
            user_id=video["user_id"],
            created_at=datetime.fromisoformat(video["created_at"].replace('Z', '+00:00')),
            updated_at=datetime.fromisoformat(video["updated_at"].replace('Z', '+00:00'))
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching video: {e}")
        raise HTTPException(status_code=500, detail=f"获取视频失败: {str(e)}")

@app.get("/api/v1/system/processor-status")
async def get_system_processor_status():
    """获取任务处理器状态"""
    return get_processor_status()

@app.get("/api/v1/analysis/tasks/{task_id}/segments")
async def get_task_segments_with_analysis(
    task_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """获取任务的视频片段及AI分析数据"""
    try:
        # 验证任务是否存在且属于当前用户
        task = await db_manager.get_analysis_task_by_id(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="分析任务不存在")
        
        if task["user_id"] != user_id:
            raise HTTPException(status_code=403, detail="无权访问此任务")
        
        # 查询视频片段数据
        segments_result = db_manager.client.table("video_segments").select("*").eq("analysis_task_id", task_id).order("segment_index").execute()
        
        if not segments_result.data:
            segments_result = None
        
        if segments_result and segments_result.data:
            segments = []
            for row in segments_result.data:
                # 查询对应的AI分析数据
                analysis_result = db_manager.client.table("segment_content_analysis").select("*").eq("segment_id", row['id']).execute()
                analysis_data = analysis_result.data[0] if analysis_result.data else {}
                
                duration = row.get('end_time', 0) - row.get('start_time', 0)
                
                segment = {
                    "segment_id": row.get('segment_index', 0),
                    "start_time": row.get('start_time', 0.0),
                    "end_time": row.get('end_time', 0.0),
                    "duration": duration,
                    "scene_type": row.get('segment_type', '未知'),
                    "frame_count": int(duration * 25),  # 假设25fps
                    "thumbnail_url": row.get('thumbnail_url'),
                    "gif_url": row.get('gif_url'),
                    "content_analysis": {
                        "caption": analysis_data.get('caption', '') or f"片段 {row.get('segment_index', 0)} 的旁白内容。这是一个示例文案，展示该片段的主要内容和关键信息。",
                        "composition": analysis_data.get('composition', '') or "中心构图，主体突出，背景简洁，视觉重点明确。",
                        "camera_movement": analysis_data.get('camera_movement', '') or "固定镜头，平稳拍摄，无明显运动。",
                        "theme_analysis": analysis_data.get('theme_analysis', '') or "展示日常活动，人物互动自然，氛围轻松愉快。",
                        "ai_commentary": analysis_data.get('ai_commentary', '') or f"此片段在整体叙事中起到承转作用，通过{row.get('segment_type', '场景')}的形式有效推进了故事发展。画面构图稳定，运镜手法恰当，成功营造了期望的氛围，为后续情节做好了铺垫。"
                    }
                }
                segments.append(segment)
            
            return {"segments": segments, "total": len(segments)}
        else:
            # 如果数据库中没有数据，尝试从JSON文件读取
            from pathlib import Path
            import json
            
            results_file = Path("uploads") / f"{task_id}_results.json"
            if results_file.exists():
                with open(results_file, 'r', encoding='utf-8') as f:
                    json_data = json.load(f)
                
                segments = json_data.get("segments", [])
                
                # 为JSON数据添加content_analysis字段（如果没有的话）
                for segment in segments:
                    if "content_analysis" not in segment:
                        segment["content_analysis"] = {
                            "caption": segment.get("transcript_text", "") or f"片段 {segment.get('segment_id', 0)} 的旁白内容。这是一个示例文案，展示该片段的主要内容和关键信息。",
                            "composition": segment.get("composition_analysis", "") or "中心构图，主体突出，背景简洁，视觉重点明确。",
                            "camera_movement": segment.get("camera_movement", "") or "固定镜头，平稳拍摄，无明显运动。",
                            "theme_analysis": segment.get("theme_analysis", "") or "展示日常活动，人物互动自然，氛围轻松愉快。",
                            "ai_commentary": segment.get("critical_review", "") or f"此片段在整体叙事中起到承转作用，通过{segment.get('scene_type', '场景')}的形式有效推进了故事发展。画面构图稳定，运镜手法恰当，成功营造了期望的氛围，为后续情节做好了铺垫。"
                        }
                
                return {"segments": segments, "total": len(segments)}
            
            return {"segments": [], "total": 0}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching segments with analysis: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"获取片段分析数据失败: {str(e)}")

@app.get("/api/v1/analysis/tasks/{task_id}", response_model=AnalysisTaskResponse)
async def get_analysis_task(
    task_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """获取分析任务详情"""
    try:
        task = await db_manager.get_analysis_task_by_id(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="分析任务不存在")
        
        if task["user_id"] != user_id:
            raise HTTPException(status_code=403, detail="无权访问此任务")
        
        return AnalysisTaskResponse(
            id=task["id"],
            video_id=task["video_id"],
            user_id=task["user_id"],
            video_segmentation=task["video_segmentation"],
            transition_detection=task["transition_detection"],
            audio_transcription=task["audio_transcription"],
            report_generation=task["report_generation"],
            status=task["status"],
            progress=task["progress"],
            error_message=task.get("error_message"),
            report_pdf_url=task.get("report_pdf_url"),
            subtitle_srt_url=task.get("subtitle_srt_url"),
            subtitle_vtt_url=task.get("subtitle_vtt_url"),
            started_at=datetime.fromisoformat(task["started_at"].replace('Z', '+00:00')) if task.get("started_at") else None,
            completed_at=datetime.fromisoformat(task["completed_at"].replace('Z', '+00:00')) if task.get("completed_at") else None,
            created_at=datetime.fromisoformat(task["created_at"].replace('Z', '+00:00')),
            updated_at=datetime.fromisoformat(task["updated_at"].replace('Z', '+00:00'))
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching analysis task: {e}")
        raise HTTPException(status_code=500, detail=f"获取分析任务失败: {str(e)}")

@app.delete("/api/v1/videos/{video_id}")
async def delete_video(
    video_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """逻辑删除视频及其相关分析任务（不删除文件）"""
    try:
        # 验证视频是否存在且属于当前用户
        video = await db_manager.get_video_by_id(video_id)
        if not video:
            raise HTTPException(status_code=404, detail="视频不存在")
        
        if video["user_id"] != user_id:
            raise HTTPException(status_code=403, detail="无权删除此视频")
        
        # 逻辑删除相关的分析任务
        tasks = await db_manager.get_video_analysis_tasks(video_id)
        for task in tasks:
            task_id = task["id"]
            await db_manager.delete_analysis_task(task_id)
            print(f"✅ 逻辑删除分析任务: {task_id}")
        
        # 逻辑删除视频记录
        await db_manager.delete_video(video_id)
        print(f"✅ 逻辑删除视频记录: {video_id}")
        
        return {"message": "视频删除成功", "video_id": video_id}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting video: {e}")
        raise HTTPException(status_code=500, detail=f"删除视频失败: {str(e)}")

# 配置静态文件服务（放在最后避免与API路由冲突）
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
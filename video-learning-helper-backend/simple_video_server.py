from fastapi import FastAPI, HTTPException, status, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, timedelta
import jwt
import bcrypt
import os
import uuid
import shutil
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv("config.env")

# 配置
SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key-change-this-in-production-2024")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# 创建FastAPI应用
app = FastAPI(
    title="Video Learning Helper API",
    description="AI拉片助手后端API - 简化版",
    version="2.0.0",
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000", "http://127.0.0.1:3001"],
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
class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    id: str
    email: str
    name: Optional[str] = None
    created_at: datetime

class UploadResponse(BaseModel):
    message: str
    video_id: str
    upload_url: Optional[str] = None

class AnalysisTaskCreate(BaseModel):
    video_id: str
    video_segmentation: bool = False
    transition_detection: bool = False
    audio_transcription: bool = False
    report_generation: bool = False

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
    created_at: datetime
    updated_at: datetime

# 模拟用户数据
users_db = {
    "admin@example.com": {
        "id": "admin-id",
        "email": "admin@example.com",
        "name": "管理员",
        "password_hash": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # admin123456
        "created_at": datetime.utcnow()
    },
    "teacher@example.com": {
        "id": "teacher-id",
        "email": "teacher@example.com",
        "name": "电影老师王五",
        "password_hash": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # teacher123456
        "created_at": datetime.utcnow()
    }
}

# 工具函数
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

def decode_access_token(token: str):
    """解码访问令牌"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

async def get_current_user_email(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """获取当前用户邮箱"""
    try:
        payload = decode_access_token(credentials.credentials)
        user_email = payload.get("sub")
        if user_email is None:
            raise HTTPException(status_code=401, detail="无效的token")
        return user_email
    except Exception:
        raise HTTPException(status_code=401, detail="无效的token")

# API路由
@app.get("/")
async def root():
    """根路径"""
    return {"message": "Video Learning Helper API v2.0.0 - 简化版"}

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "database": "memory",
        "user_count": len(users_db)
    }

@app.post("/api/v1/auth/login", response_model=Token)
async def login(user_data: UserLogin):
    """用户登录"""
    user = users_db.get(user_data.email)
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
async def get_current_user_info(user_email: str = Depends(get_current_user_email)):
    """获取当前用户信息"""
    user = users_db.get(user_email)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return UserResponse(
        id=user["id"],
        email=user["email"],
        name=user["name"],
        created_at=user["created_at"]
    )

@app.post("/api/v1/videos/upload", response_model=UploadResponse)
async def upload_video(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: str = Form(""),
    user_email: str = Depends(get_current_user_email)
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
        
        return UploadResponse(
            message="视频上传成功",
            video_id=file_id
        )
        
    except Exception as e:
        # 清理已上传的文件
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")

@app.post("/api/v1/analysis/tasks", response_model=AnalysisTaskResponse)
async def create_analysis_task(
    task_data: AnalysisTaskCreate,
    user_email: str = Depends(get_current_user_email)
):
    """创建分析任务"""
    task_id = str(uuid.uuid4())
    return AnalysisTaskResponse(
        id=task_id,
        video_id=task_data.video_id,
        user_id=user_email,
        video_segmentation=task_data.video_segmentation,
        transition_detection=task_data.transition_detection,
        audio_transcription=task_data.audio_transcription,
        report_generation=task_data.report_generation,
        status="pending",
        progress="{}",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
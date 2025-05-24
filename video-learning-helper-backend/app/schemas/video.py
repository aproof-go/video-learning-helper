from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class VideoStatus(str, Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class AnalysisType(str, Enum):
    SCENE_DETECTION = "scene_detection"
    AUDIO_TRANSCRIPTION = "audio_transcription"
    TRANSITION_DETECTION = "transition_detection"
    FULL_ANALYSIS = "full_analysis"

# 视频相关模式
class VideoBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)

class VideoCreate(VideoBase):
    filename: str
    file_size: int
    duration: Optional[int] = None
    resolution_width: Optional[int] = None
    resolution_height: Optional[int] = None
    format: Optional[str] = None

class VideoUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[str] = None
    file_url: Optional[str] = None
    thumbnail_url: Optional[str] = None

class VideoResponse(VideoBase):
    id: str
    filename: str
    file_size: int
    duration: Optional[int]
    resolution_width: Optional[int]
    resolution_height: Optional[int]
    format: Optional[str]
    status: str
    file_url: Optional[str]
    thumbnail_url: Optional[str]
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# 项目相关模式
class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None

class ProjectCreate(ProjectBase):
    video_id: int
    analysis_types: List[AnalysisType] = [AnalysisType.FULL_ANALYSIS]

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    progress: Optional[float] = None

class ProjectResponse(ProjectBase):
    id: int
    video_id: int
    user_id: str
    status: str
    progress: float
    analysis_types: str  # JSON字符串
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# 分析结果相关模式
class AnalysisResultCreate(BaseModel):
    project_id: int
    video_id: int
    analysis_type: AnalysisType
    result_data: str  # JSON字符串
    confidence_score: Optional[float] = None
    processing_time: Optional[float] = None

class AnalysisResultResponse(BaseModel):
    id: int
    project_id: int
    video_id: int
    analysis_type: AnalysisType
    result_data: str
    confidence_score: Optional[float]
    processing_time: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True

# 分析任务相关模式
class AnalysisTaskBase(BaseModel):
    video_segmentation: bool = False
    transition_detection: bool = False
    audio_transcription: bool = False
    report_generation: bool = False

class AnalysisTaskCreate(AnalysisTaskBase):
    video_id: str

class AnalysisTaskUpdate(BaseModel):
    video_segmentation: Optional[bool] = None
    transition_detection: Optional[bool] = None
    audio_transcription: Optional[bool] = None
    report_generation: Optional[bool] = None
    status: Optional[str] = None
    progress: Optional[str] = None
    error_message: Optional[str] = None

class AnalysisTaskResponse(AnalysisTaskBase):
    id: str
    video_id: str
    user_id: str
    status: str
    progress: str
    error_message: Optional[str]
    report_pdf_url: Optional[str]
    subtitle_srt_url: Optional[str]
    subtitle_vtt_url: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# 上传响应模式
class UploadResponse(BaseModel):
    message: str
    video_id: str
    upload_url: Optional[str] = None

# 分析请求模式
class AnalysisRequest(BaseModel):
    video_id: int
    project_name: str
    description: Optional[str] = None
    analysis_types: List[AnalysisType] = [AnalysisType.FULL_ANALYSIS]

# 综合响应模式（包含关联数据）
class ProjectWithDetails(ProjectResponse):
    video: VideoResponse
    analysis_results: List[AnalysisResultResponse] = []

class VideoWithProjects(VideoResponse):
    projects: List[ProjectResponse] = []

class VideoWithTasks(VideoResponse):
    tasks: List[AnalysisTaskResponse] = [] 
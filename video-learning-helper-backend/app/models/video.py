from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, Enum, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum
import uuid

Base = declarative_base()

class VideoStatus(str, enum.Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class Video(Base):
    __tablename__ = "videos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    filename = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)  # 文件大小（字节）
    file_url = Column(Text)  # 文件URL
    thumbnail_url = Column(Text)  # 缩略图URL
    duration = Column(Integer)  # 视频时长（秒）
    resolution_width = Column(Integer)  # 分辨率宽度
    resolution_height = Column(Integer)  # 分辨率高度
    format = Column(String(50))  # 视频格式
    
    # 处理状态
    status = Column(String(50), default="uploaded")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    user = relationship("User", back_populates="videos")
    analysis_tasks = relationship("AnalysisTask", back_populates="video")

class AnalysisTask(Base):
    __tablename__ = "analysis_tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # 分析配置选项
    video_segmentation = Column(Boolean, default=False)
    transition_detection = Column(Boolean, default=False)
    audio_transcription = Column(Boolean, default=False)
    report_generation = Column(Boolean, default=False)
    
    # 任务状态
    status = Column(String(50), default="pending")  # pending, processing, completed, failed
    progress = Column(Text, default="{}")  # JSON字符串，存储进度信息
    error_message = Column(Text)
    
    # 结果URL
    report_pdf_url = Column(Text)
    subtitle_srt_url = Column(Text)
    subtitle_vtt_url = Column(Text)
    script_md_url = Column(Text)
    
    # 时间戳
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    video = relationship("Video", back_populates="analysis_tasks")
    user = relationship("User", back_populates="analysis_tasks")
    video_segments = relationship("VideoSegment", back_populates="analysis_task")
    transitions = relationship("Transition", back_populates="analysis_task")
    transcriptions = relationship("Transcription", back_populates="analysis_task")
    reports = relationship("Report", back_populates="analysis_task")

class VideoSegment(Base):
    __tablename__ = "video_segments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id"), nullable=False)
    analysis_task_id = Column(UUID(as_uuid=True), ForeignKey("analysis_tasks.id"), nullable=False)
    
    segment_index = Column(Integer, nullable=False)
    start_time = Column(Float, nullable=False)
    end_time = Column(Float, nullable=False)
    segment_type = Column(String(50))
    description = Column(Text)
    
    # 生成的资源
    gif_url = Column(Text)
    gif_size = Column(Integer)
    thumbnail_url = Column(Text)
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    analysis_task = relationship("AnalysisTask", back_populates="video_segments")

class Transition(Base):
    __tablename__ = "transitions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id"), nullable=False)
    analysis_task_id = Column(UUID(as_uuid=True), ForeignKey("analysis_tasks.id"), nullable=False)
    
    timestamp = Column(Float, nullable=False)
    transition_type = Column(String(50), nullable=False)
    description = Column(Text)
    confidence = Column(Float)
    
    from_segment_id = Column(UUID(as_uuid=True), ForeignKey("video_segments.id"))
    to_segment_id = Column(UUID(as_uuid=True), ForeignKey("video_segments.id"))
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关联关系
    analysis_task = relationship("AnalysisTask", back_populates="transitions")

class Transcription(Base):
    __tablename__ = "transcriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id"), nullable=False)
    analysis_task_id = Column(UUID(as_uuid=True), ForeignKey("analysis_tasks.id"), nullable=False)
    
    sequence_number = Column(Integer, nullable=False)
    start_time = Column(Float, nullable=False)
    end_time = Column(Float, nullable=False)
    text = Column(Text, nullable=False)
    speaker = Column(String(100))
    confidence = Column(Float)
    language = Column(String(10), default="zh")
    
    segment_id = Column(UUID(as_uuid=True), ForeignKey("video_segments.id"))
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关联关系
    analysis_task = relationship("AnalysisTask", back_populates="transcriptions")

class Report(Base):
    __tablename__ = "reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id"), nullable=False)
    analysis_task_id = Column(UUID(as_uuid=True), ForeignKey("analysis_tasks.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    title = Column(String(255), nullable=False)
    report_type = Column(String(50), default="standard")
    content = Column(Text, default="{}")  # JSON内容
    
    # 统计信息
    total_segments = Column(Integer, default=0)
    total_transitions = Column(Integer, default=0)
    total_transcription_lines = Column(Integer, default=0)
    video_duration = Column(Float)
    
    # 生成的文件URL
    pdf_url = Column(Text)
    html_url = Column(Text)
    
    # 状态
    status = Column(String(50), default="generating")  # generating, completed, failed
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    analysis_task = relationship("AnalysisTask", back_populates="reports") 
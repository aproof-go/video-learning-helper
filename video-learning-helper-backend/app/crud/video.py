from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
import json
from app.models.video import Video, AnalysisTask, VideoSegment, Transition, Transcription, Report
from app.schemas.video import VideoCreate, VideoUpdate, AnalysisTaskCreate, AnalysisTaskUpdate

class VideoCRUD:
    def create_video(self, db: Session, video: VideoCreate, user_id: str) -> Video:
        """创建视频记录"""
        db_video = Video(
            title=video.title,
            filename=video.filename,
            file_size=video.file_size,
            duration=video.duration,
            resolution_width=video.resolution_width,
            resolution_height=video.resolution_height,
            format=video.format,
            user_id=user_id,
            status="uploaded"
        )
        db.add(db_video)
        db.commit()
        db.refresh(db_video)
        return db_video

    def get_video(self, db: Session, video_id: str) -> Optional[Video]:
        """根据ID获取视频"""
        return db.query(Video).filter(Video.id == video_id).first()

    def get_user_videos(self, db: Session, user_id: str, skip: int = 0, limit: int = 100) -> List[Video]:
        """获取用户的视频列表"""
        return db.query(Video).filter(Video.user_id == user_id).offset(skip).limit(limit).all()

    def update_video(self, db: Session, video_id: str, video_update: VideoUpdate) -> Optional[Video]:
        """更新视频信息"""
        db_video = db.query(Video).filter(Video.id == video_id).first()
        if db_video:
            update_data = video_update.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_video, field, value)
            db.commit()
            db.refresh(db_video)
        return db_video

    def delete_video(self, db: Session, video_id: str) -> bool:
        """删除视频"""
        db_video = db.query(Video).filter(Video.id == video_id).first()
        if db_video:
            db.delete(db_video)
            db.commit()
            return True
        return False

class AnalysisTaskCRUD:
    def create_task(self, db: Session, task: AnalysisTaskCreate, user_id: str) -> AnalysisTask:
        """创建分析任务"""
        db_task = AnalysisTask(
            video_id=task.video_id,
            user_id=user_id,
            video_segmentation=task.video_segmentation,
            transition_detection=task.transition_detection,
            audio_transcription=task.audio_transcription,
            report_generation=task.report_generation,
            status="pending"
        )
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        return db_task

    def get_task(self, db: Session, task_id: str) -> Optional[AnalysisTask]:
        """根据ID获取任务"""
        return db.query(AnalysisTask).filter(AnalysisTask.id == task_id).first()

    def get_user_tasks(self, db: Session, user_id: str, skip: int = 0, limit: int = 100) -> List[AnalysisTask]:
        """获取用户的任务列表"""
        return db.query(AnalysisTask).filter(AnalysisTask.user_id == user_id).offset(skip).limit(limit).all()

    def get_video_tasks(self, db: Session, video_id: str) -> List[AnalysisTask]:
        """获取视频的所有任务"""
        return db.query(AnalysisTask).filter(AnalysisTask.video_id == video_id).all()

    def update_task(self, db: Session, task_id: str, task_update: AnalysisTaskUpdate) -> Optional[AnalysisTask]:
        """更新任务信息"""
        db_task = db.query(AnalysisTask).filter(AnalysisTask.id == task_id).first()
        if db_task:
            update_data = task_update.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_task, field, value)
            db.commit()
            db.refresh(db_task)
        return db_task

    def update_task_progress(self, db: Session, task_id: str, progress: dict, status: str = None) -> Optional[AnalysisTask]:
        """更新任务进度"""
        db_task = db.query(AnalysisTask).filter(AnalysisTask.id == task_id).first()
        if db_task:
            db_task.progress = json.dumps(progress)
            if status:
                db_task.status = status
            db.commit()
            db.refresh(db_task)
        return db_task

    def delete_task(self, db: Session, task_id: str) -> bool:
        """删除任务"""
        db_task = db.query(AnalysisTask).filter(AnalysisTask.id == task_id).first()
        if db_task:
            db.delete(db_task)
            db.commit()
            return True
        return False

# 创建CRUD实例
video_crud = VideoCRUD()
analysis_task_crud = AnalysisTaskCRUD() 
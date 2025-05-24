import os
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import datetime
import uuid

# 加载环境变量
load_dotenv("config.env")

# Supabase配置
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://tjxqzmrmybrcmkflaimq.supabase.co")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRqeHF6bXJteWJyY21rZmxhaW1xIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDgwMTQ2NDIsImV4cCI6MjA2MzU5MDY0Mn0.uOYYkrZP2VFLwNkoU96Qo94A5oh9wJbTIlGnChH2pCg")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")  # Optional service key

# 创建Supabase客户端
if SUPABASE_SERVICE_KEY:
    # Use service key if available (bypasses RLS)
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    print("✅ Using Supabase service key (RLS bypassed)")
else:
    # Fall back to anon key
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    print("⚠️ Using Supabase anon key (RLS restrictions apply)")

# In-memory storage for videos when RLS blocks insertion
_video_storage = {}
_task_storage = {}

class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self):
        self.client = supabase
    
    # 用户相关方法
    async def create_user(self, email: str, name: Optional[str], password_hash: str) -> dict:
        """创建新用户"""
        user_data = {
            "email": email,
            "name": name,
            "password_hash": password_hash
        }
        
        result = self.client.table("users").insert(user_data).execute()
        
        if result.data:
            return result.data[0]
        else:
            raise Exception(f"Failed to create user: {result}")
    
    async def get_user_by_email(self, email: str) -> Optional[dict]:
        """根据邮箱获取用户"""
        result = self.client.table("users").select("*").eq("email", email).execute()
        
        if result.data:
            return result.data[0]
        return None
    
    async def get_user_by_id(self, user_id: str) -> Optional[dict]:
        """根据ID获取用户"""
        result = self.client.table("users").select("*").eq("id", user_id).execute()
        
        if result.data:
            return result.data[0]
        return None
    
    async def email_exists(self, email: str) -> bool:
        """检查邮箱是否已存在"""
        result = self.client.table("users").select("id").eq("email", email).execute()
        return len(result.data) > 0
    
    async def get_user_count(self) -> int:
        """获取用户总数"""
        result = self.client.table("users").select("id", count="exact").execute()
        return result.count or 0
    
    # 视频相关方法
    async def create_video(self, video_data: Dict[str, Any]) -> dict:
        """创建视频记录"""
        video_record = {
            "id": str(uuid.uuid4()),
            "title": video_data.get("title"),
            "filename": video_data.get("filename"),
            "file_size": video_data.get("file_size"),
            "duration": video_data.get("duration"),
            "resolution_width": video_data.get("resolution_width"),
            "resolution_height": video_data.get("resolution_height"),
            "format": video_data.get("format"),
            "status": video_data.get("status", "uploaded"),
            "file_url": video_data.get("file_url"),
            "thumbnail_url": video_data.get("thumbnail_url"),
            "user_id": video_data.get("user_id"),
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        try:
            # Try to insert into Supabase
            result = self.client.table("videos").insert(video_record).execute()
            if result.data:
                print(f"✅ Video stored in Supabase: {video_record['id']}")
                return result.data[0]
            else:
                raise Exception(f"Supabase insert failed: {result}")
        except Exception as e:
            error_msg = str(e)
            if "row-level security" in error_msg:
                # RLS blocked insertion, use in-memory storage
                print(f"⚠️ RLS blocked Supabase insertion, using memory storage for video: {video_record['id']}")
                _video_storage[video_record['id']] = video_record
                return video_record
            else:
                raise Exception(f"Failed to create video: {e}")
    
    async def get_video_by_id(self, video_id: str) -> Optional[dict]:
        """根据ID获取视频"""
        # First check in-memory storage (only non-deleted)
        if video_id in _video_storage:
            video = _video_storage[video_id]
            if not video.get("deleted_at"):
                return video
        
        # Then check Supabase
        try:
            # 尝试使用 deleted_at 字段过滤
            result = self.client.table("videos").select("*").eq("id", video_id).is_("deleted_at", "null").execute()
            if result.data:
                return result.data[0]
        except Exception as e:
            error_msg = str(e)
            # 如果 deleted_at 字段不存在，回退到普通查询
            if "does not exist" in error_msg or "column" in error_msg:
                print(f"Warning: deleted_at column not found, using fallback query for video {video_id}: {e}")
                try:
                    result = self.client.table("videos").select("*").eq("id", video_id).execute()
                    if result.data:
                        return result.data[0]
                except Exception as e2:
                    print(f"Warning: Failed to query Supabase for video {video_id}: {e2}")
            else:
                print(f"Warning: Failed to query Supabase for video {video_id}: {e}")
        
        return None
    
    async def get_user_videos(self, user_id: str, skip: int = 0, limit: int = 100) -> List[dict]:
        """获取用户的视频列表（最新的在前面）"""
        videos = []
        
        # Get videos from in-memory storage (only non-deleted)
        memory_videos = [v for v in _video_storage.values() 
                        if v.get("user_id") == user_id and not v.get("deleted_at")]
        videos.extend(memory_videos)
        
        # Get videos from Supabase (order by created_at desc)
        try:
            # 尝试使用 deleted_at 字段过滤
            result = self.client.table("videos").select("*").eq("user_id", user_id)\
                .is_("deleted_at", "null")\
                .order("created_at", desc=True)\
                .range(skip, skip + limit - 1).execute()
            if result.data:
                videos.extend(result.data)
        except Exception as e:
            error_msg = str(e)
            # 如果 deleted_at 字段不存在，回退到普通查询
            if "does not exist" in error_msg or "column" in error_msg:
                print(f"Warning: deleted_at column not found, using fallback query for user videos: {e}")
                try:
                    result = self.client.table("videos").select("*").eq("user_id", user_id)\
                        .order("created_at", desc=True)\
                        .range(skip, skip + limit - 1).execute()
                    if result.data:
                        videos.extend(result.data)
                except Exception as e2:
                    print(f"Warning: Failed to query Supabase for user videos: {e2}")
            else:
                print(f"Warning: Failed to query Supabase for user videos: {e}")
        
        # Sort combined results by created_at desc and apply pagination  
        videos.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return videos[skip:skip + limit]
    
    async def update_video(self, video_id: str, update_data: Dict[str, Any]) -> dict:
        """更新视频信息"""
        update_data["updated_at"] = datetime.utcnow().isoformat()
        
        result = self.client.table("videos").update(update_data).eq("id", video_id).execute()
        
        if result.data:
            return result.data[0]
        else:
            raise Exception(f"Failed to update video: {result}")
    
    async def delete_video(self, video_id: str) -> bool:
        """删除视频"""
        result = self.client.table("videos").delete().eq("id", video_id).execute()
        return len(result.data) > 0
    
    # 分析任务相关方法
    async def create_analysis_task(self, task_data: Dict[str, Any]) -> dict:
        """创建分析任务"""
        task_record = {
            "id": str(uuid.uuid4()),
            "video_id": task_data.get("video_id"),
            "user_id": task_data.get("user_id"),
            "video_segmentation": task_data.get("video_segmentation", False),
            "transition_detection": task_data.get("transition_detection", False),
            "audio_transcription": task_data.get("audio_transcription", False),
            "report_generation": task_data.get("report_generation", False),
            "status": "pending",
            "progress": "0",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        try:
            # Try to insert into Supabase
            result = self.client.table("analysis_tasks").insert(task_record).execute()
            if result.data:
                print(f"✅ Analysis task stored in Supabase: {task_record['id']}")
                return result.data[0]
            else:
                raise Exception(f"Supabase insert failed: {result}")
        except Exception as e:
            error_msg = str(e)
            if "row-level security" in error_msg:
                # RLS blocked insertion, use in-memory storage
                print(f"⚠️ RLS blocked Supabase insertion, using memory storage for task: {task_record['id']}")
                _task_storage[task_record['id']] = task_record
                return task_record
            else:
                raise Exception(f"Failed to create analysis task: {e}")
    
    async def get_analysis_task_by_id(self, task_id: str) -> Optional[dict]:
        """根据ID获取分析任务"""
        # First check in-memory storage
        if task_id in _task_storage:
            return _task_storage[task_id]
        
        # Then check Supabase
        try:
            result = self.client.table("analysis_tasks").select("*").eq("id", task_id).execute()
            if result.data:
                return result.data[0]
        except Exception as e:
            print(f"Warning: Failed to query Supabase for analysis task {task_id}: {e}")
        
        return None
    
    async def get_user_analysis_tasks(self, user_id: str, skip: int = 0, limit: int = 100) -> List[dict]:
        """获取用户的分析任务列表"""
        result = self.client.table("analysis_tasks").select("*").eq("user_id", user_id)\
            .range(skip, skip + limit - 1).execute()
        
        return result.data or []
    
    async def get_video_analysis_tasks(self, video_id: str) -> List[dict]:
        """获取视频的分析任务"""
        tasks = []
        
        # Get tasks from in-memory storage
        memory_tasks = [t for t in _task_storage.values() 
                       if t.get("video_id") == video_id]
        tasks.extend(memory_tasks)
        
        # Get tasks from Supabase
        try:
            result = self.client.table("analysis_tasks").select("*").eq("video_id", video_id)\
                .order("created_at", desc=True).execute()
            if result.data:
                tasks.extend(result.data)
        except Exception as e:
            print(f"Warning: Failed to query Supabase for video analysis tasks: {e}")
        
        # Sort by created_at desc
        tasks.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return tasks
    
    async def update_analysis_task(self, task_id: str, update_data: Dict[str, Any]) -> dict:
        """更新分析任务"""
        update_data["updated_at"] = datetime.utcnow().isoformat()
        
        # Update in-memory storage if exists
        if task_id in _task_storage:
            _task_storage[task_id].update(update_data)
            return _task_storage[task_id]
        
        # Update in Supabase
        try:
            result = self.client.table("analysis_tasks").update(update_data).eq("id", task_id).execute()
            if result.data:
                return result.data[0]
            else:
                raise Exception(f"Failed to update analysis task: {result}")
        except Exception as e:
            print(f"Warning: Failed to update analysis task in Supabase: {e}")
            raise
    
    async def delete_analysis_task(self, task_id: str) -> bool:
        """逻辑删除分析任务"""
        deleted_at = datetime.utcnow().isoformat()
        
        # Update in-memory storage if exists
        if task_id in _task_storage:
            _task_storage[task_id]["deleted_at"] = deleted_at
            _task_storage[task_id]["updated_at"] = deleted_at
            print(f"✅ 逻辑删除分析任务: {task_id}")
            return True
        
        # 对于Supabase，如果表没有deleted_at字段，使用物理删除
        try:
            # 先尝试逻辑删除
            update_data = {
                "deleted_at": deleted_at,
                "updated_at": deleted_at
            }
            result = self.client.table("analysis_tasks").update(update_data).eq("id", task_id).execute()
            if result.data:
                print(f"✅ 逻辑删除分析任务: {task_id}")
                return True
            return False
        except Exception as e:
            # 如果逻辑删除失败（可能是字段不存在），尝试物理删除
            print(f"Warning: Failed to logically delete analysis task from Supabase: {e}")
            try:
                result = self.client.table("analysis_tasks").delete().eq("id", task_id).execute()
                if result.data:
                    print(f"✅ 物理删除分析任务: {task_id}")
                    return True
            except Exception as e2:
                print(f"Warning: Failed to physically delete analysis task from Supabase: {e2}")
            return False

    async def delete_video(self, video_id: str) -> bool:
        """逻辑删除视频"""
        deleted_at = datetime.utcnow().isoformat()
        
        # Update in-memory storage if exists
        if video_id in _video_storage:
            _video_storage[video_id]["deleted_at"] = deleted_at
            _video_storage[video_id]["updated_at"] = deleted_at
            print(f"✅ 逻辑删除视频记录: {video_id}")
            return True
        
        # 对于Supabase，如果表没有deleted_at字段，使用物理删除
        try:
            # 先尝试逻辑删除
            update_data = {
                "deleted_at": deleted_at,
                "updated_at": deleted_at
            }
            result = self.client.table("videos").update(update_data).eq("id", video_id).execute()
            if result.data:
                print(f"✅ 逻辑删除视频记录: {video_id}")
                return True
            return False
        except Exception as e:
            # 如果逻辑删除失败（可能是字段不存在），尝试物理删除
            print(f"Warning: Failed to logically delete video from Supabase: {e}")
            try:
                result = self.client.table("videos").delete().eq("id", video_id).execute()
                if result.data:
                    print(f"✅ 物理删除视频记录: {video_id}")
                    return True
            except Exception as e2:
                print(f"Warning: Failed to physically delete video from Supabase: {e2}")
            return False

# 全局数据库实例
db_manager = DatabaseManager() 
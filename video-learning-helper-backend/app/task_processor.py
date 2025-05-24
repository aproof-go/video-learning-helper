import asyncio
import threading
import time
from pathlib import Path
from typing import Dict, Any, Callable
import logging
from datetime import datetime
import json
import traceback

from app.video_analyzer import VideoAnalyzer
from app.database_supabase import db_manager

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TaskProcessor:
    """异步任务处理器"""
    
    def __init__(self, max_concurrent_tasks: int = 2):
        self.max_concurrent_tasks = max_concurrent_tasks
        self.running_tasks = {}
        self.task_queue = asyncio.Queue()
        self.is_running = False
        self.worker_task = None
        self.video_analyzer = VideoAnalyzer()
        
    async def start(self):
        """启动任务处理器"""
        if self.is_running:
            return
            
        self.is_running = True
        self.worker_task = asyncio.create_task(self._worker())
        logger.info("任务处理器已启动")
        
    async def stop(self):
        """停止任务处理器"""
        self.is_running = False
        if self.worker_task:
            self.worker_task.cancel()
            try:
                await self.worker_task
            except asyncio.CancelledError:
                pass
        logger.info("任务处理器已停止")
        
    async def submit_task(self, task_id: str, video_path: str, task_config: Dict[str, bool]):
        """提交分析任务"""
        task_info = {
            "task_id": task_id,
            "video_path": video_path,
            "task_config": task_config,
            "submitted_at": datetime.now().isoformat()
        }
        
        await self.task_queue.put(task_info)
        logger.info(f"任务已提交到队列: {task_id}")
        
    async def _worker(self):
        """工作线程，处理任务队列"""
        while self.is_running:
            try:
                # 检查是否有空闲槽位
                if len(self.running_tasks) >= self.max_concurrent_tasks:
                    await asyncio.sleep(1)
                    continue
                
                # 从队列获取任务
                try:
                    task_info = await asyncio.wait_for(self.task_queue.get(), timeout=1.0)
                except asyncio.TimeoutError:
                    continue
                
                # 启动任务处理
                task_id = task_info["task_id"]
                task_coroutine = self._process_task(task_info)
                self.running_tasks[task_id] = asyncio.create_task(task_coroutine)
                
                logger.info(f"开始处理任务: {task_id}")
                
            except Exception as e:
                logger.error(f"工作线程异常: {e}")
                await asyncio.sleep(5)  # 错误后等待5秒
    
    async def _process_task(self, task_info: Dict[str, Any]):
        """处理单个分析任务"""
        task_id = task_info["task_id"]
        video_path = task_info["video_path"]
        task_config = task_info["task_config"]
        
        try:
            # 更新任务状态为"运行中"
            await self._update_task_status(task_id, "running", "0", "开始分析")
            
            # 创建进度回调函数
            async def progress_callback(progress: str, message: str):
                await self._update_task_status(task_id, "running", progress, message)
            
            # 在独立线程中运行视频分析（避免阻塞事件循环）
            loop = asyncio.get_event_loop()
            
            def sync_analyze():
                def sync_progress_callback(progress, message):
                    # 在同步函数中调用异步更新
                    asyncio.run_coroutine_threadsafe(
                        progress_callback(progress, message), loop
                    ).result()
                
                return self.video_analyzer.analyze_video(
                    video_path, task_config, sync_progress_callback, task_id
                )
            
            # 在线程池中执行同步任务
            results = await loop.run_in_executor(None, sync_analyze)
            
            # 处理分析结果
            await self._handle_analysis_results(task_id, results, video_path)
            
            # 更新任务状态为"完成"
            await self._update_task_status(task_id, "completed", "100", "分析完成")
            
            logger.info(f"任务处理完成: {task_id}")
            
        except Exception as e:
            logger.error(f"任务处理失败 {task_id}: {e}")
            logger.error(traceback.format_exc())
            
            # 更新任务状态为"失败"
            error_message = f"分析失败: {str(e)}"
            await self._update_task_status(task_id, "failed", "0", error_message, str(e))
        
        finally:
            # 从运行任务列表中移除
            if task_id in self.running_tasks:
                del self.running_tasks[task_id]
    
    async def _update_task_status(self, task_id: str, status: str, progress: str, 
                                message: str, error_message: str = None):
        """更新任务状态"""
        try:
            update_data = {
                "status": status,
                "progress": progress,
                "updated_at": datetime.now().isoformat()
            }
            
            if status == "running":
                update_data["started_at"] = datetime.now().isoformat()
            elif status == "completed":
                update_data["completed_at"] = datetime.now().isoformat()
            
            if error_message:
                update_data["error_message"] = error_message
            
            # 尝试更新Supabase
            try:
                result = db_manager.client.table("analysis_tasks").update(update_data).eq("id", task_id).execute()
                if not result.data:
                    logger.warning(f"Supabase更新失败，任务ID: {task_id}")
            except Exception as e:
                logger.warning(f"Supabase更新异常: {e}")
            
            # 同时更新内存存储（用于兼容性）
            from app.database_supabase import _task_storage
            if task_id in _task_storage:
                _task_storage[task_id].update(update_data)
            
            logger.info(f"任务状态更新: {task_id} -> {status} ({progress}%) - {message}")
            
        except Exception as e:
            logger.error(f"更新任务状态失败 {task_id}: {e}")
    
    async def _handle_analysis_results(self, task_id: str, results: Dict[str, Any], video_path: str):
        """处理分析结果，保存文件和URL"""
        try:
            update_data = {}
            uploads_dir = Path("uploads")
            uploads_dir.mkdir(exist_ok=True)
            
            # 处理字幕文件
            transcription = results.get("transcription", {})
            if "subtitle_file" in transcription:
                subtitle_path = Path(transcription["subtitle_file"])
                if subtitle_path.exists():
                    # 检查是否已经在正确位置
                    expected_path = uploads_dir / f"{task_id}_subtitles.srt"
                    if subtitle_path.resolve() == expected_path.resolve():
                        # 文件已经在正确位置
                        update_data["subtitle_srt_url"] = f"/uploads/{expected_path.name}"
                        logger.info(f"字幕文件已在正确位置: {expected_path}")
                    else:
                        # 需要复制文件
                        import shutil
                        shutil.copy2(subtitle_path, expected_path)
                        update_data["subtitle_srt_url"] = f"/uploads/{expected_path.name}"
                        logger.info(f"字幕文件已复制: {subtitle_path} -> {expected_path}")
            
            # 直接检查uploads目录中是否已有分析结果文件
            existing_subtitle = uploads_dir / f"{task_id}_subtitles.srt"
            if existing_subtitle.exists() and "subtitle_srt_url" not in update_data:
                update_data["subtitle_srt_url"] = f"/uploads/{existing_subtitle.name}"
                logger.info(f"发现现有字幕文件: {existing_subtitle}")
            
            # 处理脚本文件
            transcription = results.get("transcription", {})
            if "script_file" in transcription:
                script_path = Path(transcription["script_file"])
                if script_path.exists():
                    # 检查是否已经在正确位置
                    expected_path = uploads_dir / f"{task_id}_script.md"
                    if script_path.resolve() == expected_path.resolve():
                        # 文件已经在正确位置
                        update_data["script_md_url"] = f"/uploads/{expected_path.name}"
                        logger.info(f"脚本文件已在正确位置: {expected_path}")
                    else:
                        # 需要复制文件
                        import shutil
                        shutil.copy2(script_path, expected_path)
                        update_data["script_md_url"] = f"/uploads/{expected_path.name}"
                        logger.info(f"脚本文件已复制: {script_path} -> {expected_path}")
            
            # 检查是否有直接生成的脚本文件
            existing_script = uploads_dir / f"{task_id}_script.md"
            if existing_script.exists() and "script_md_url" not in update_data:
                update_data["script_md_url"] = f"/uploads/{existing_script.name}"
                logger.info(f"发现现有脚本文件: {existing_script}")
            
            # 处理报告文件
            if "report_path" in results:
                report_path = Path(results["report_path"])
                if report_path.exists():
                    # 检查是否已经在正确位置
                    expected_path = uploads_dir / f"{task_id}_report.pdf"
                    if report_path.resolve() == expected_path.resolve():
                        # 文件已经在正确位置
                        update_data["report_pdf_url"] = f"/uploads/{expected_path.name}"
                        logger.info(f"报告文件已在正确位置: {expected_path}")
                    else:
                        # 需要复制文件
                        import shutil
                        shutil.copy2(report_path, expected_path)
                        update_data["report_pdf_url"] = f"/uploads/{expected_path.name}"
                        logger.info(f"报告文件已复制: {report_path} -> {expected_path}")
            
            # 检查是否有直接生成的报告文件
            existing_report = uploads_dir / f"{task_id}_report.pdf"
            if existing_report.exists() and "report_pdf_url" not in update_data:
                update_data["report_pdf_url"] = f"/uploads/{existing_report.name}"
                logger.info(f"发现现有报告文件: {existing_report}")
            
            # 保存分析结果的JSON数据
            results_json = json.dumps(results, ensure_ascii=False, default=str)
            results_file = uploads_dir / f"{task_id}_results.json"
            with open(results_file, 'w', encoding='utf-8') as f:
                f.write(results_json)
            logger.info(f"分析结果JSON已保存: {results_file}")
            
            # 保存视频片段和AI分析数据到数据库
            await self._save_segments_to_database(task_id, results)
            
            # 更新数据库
            if update_data:
                try:
                    await db_manager.update_analysis_task(task_id, update_data)
                    logger.info(f"数据库已更新分析结果URL: {task_id} -> {update_data}")
                except Exception as e:
                    logger.warning(f"保存分析结果到数据库失败: {e}")
                    # 尝试直接更新内存存储
                    from app.database_supabase import _task_storage
                    if task_id in _task_storage:
                        _task_storage[task_id].update(update_data)
                        logger.info(f"内存存储已更新: {task_id}")
            
        except Exception as e:
            logger.error(f"处理分析结果失败 {task_id}: {e}")
            import traceback
            logger.error(traceback.format_exc())
    
    async def _save_segments_to_database(self, task_id: str, results: Dict[str, Any]):
        """保存视频片段和AI分析数据到数据库"""
        try:
            segments = results.get("segments", [])
            if not segments:
                logger.info("没有视频片段数据需要保存")
                return
            
            # 获取任务信息来获取video_id
            task_info = await db_manager.get_analysis_task(task_id)
            if not task_info:
                logger.warning(f"找不到任务信息: {task_id}")
                return
            
            video_id = task_info.get("video_id")
            if not video_id:
                logger.warning(f"任务中没有video_id: {task_id}")
                return
            
            logger.info(f"开始保存 {len(segments)} 个视频片段到数据库")
            
            for segment in segments:
                try:
                    # 保存video_segment记录
                    segment_data = {
                        "video_id": video_id,
                        "analysis_task_id": task_id,
                        "segment_index": segment.get("segment_id", 0),
                        "start_time": segment.get("start_time", 0.0),
                        "end_time": segment.get("end_time", 0.0),
                        "segment_type": segment.get("scene_type", "未知"),
                        "description": f"片段 {segment.get('segment_id', 0)}",
                        "gif_url": segment.get("gif_url"),
                        "thumbnail_url": segment.get("thumbnail_url")
                    }
                    
                    # 使用Supabase执行SQL插入
                    insert_result = db_manager.client.table("video_segments").insert(segment_data).execute()
                    
                    if insert_result.data:
                        segment_id = insert_result.data[0]["id"]
                        logger.info(f"视频片段已保存: segment_id={segment_id}")
                        
                        # 保存AI分析数据到segment_content_analysis表
                        analysis_data = {
                            "segment_id": segment_id,
                            "caption": segment.get("transcript_text", ""),
                            "composition": segment.get("composition_analysis", ""),
                            "camera_movement": segment.get("camera_movement", ""),
                            "theme_analysis": segment.get("theme_analysis", ""),
                            "ai_commentary": segment.get("critical_review", "")
                        }
                        
                        # 只保存非空的分析数据
                        if any(v for v in analysis_data.values() if v):
                            analysis_result = db_manager.client.table("segment_content_analysis").insert(analysis_data).execute()
                            if analysis_result.data:
                                logger.info(f"AI分析数据已保存: segment_id={segment_id}")
                            else:
                                logger.warning(f"AI分析数据保存失败: segment_id={segment_id}")
                    else:
                        logger.warning(f"视频片段保存失败: {segment_data}")
                        
                except Exception as e:
                    logger.error(f"保存视频片段失败: {e}")
                    continue
            
            logger.info(f"完成保存视频片段到数据库: task_id={task_id}")
            
        except Exception as e:
            logger.error(f"保存片段数据到数据库失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
    
    def get_queue_status(self) -> Dict[str, Any]:
        """获取队列状态"""
        return {
            "is_running": self.is_running,
            "queue_size": self.task_queue.qsize(),
            "running_tasks": len(self.running_tasks),
            "max_concurrent_tasks": self.max_concurrent_tasks,
            "running_task_ids": list(self.running_tasks.keys())
        }

# 全局任务处理器实例
task_processor = TaskProcessor()

async def start_task_processor():
    """启动全局任务处理器"""
    await task_processor.start()

async def stop_task_processor():
    """停止全局任务处理器"""
    await task_processor.stop()

async def submit_analysis_task(task_id: str, video_path: str, task_config: Dict[str, bool]):
    """提交分析任务到处理器"""
    await task_processor.submit_task(task_id, video_path, task_config)

def get_processor_status() -> Dict[str, Any]:
    """获取处理器状态"""
    return task_processor.get_queue_status() 
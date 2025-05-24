#!/usr/bin/env python3
"""
修复现有分析任务的文件URL
为已经生成但URL缺失的分析结果更新正确的下载链接
"""

import asyncio
import sys
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from app.database_supabase import db_manager, _task_storage

async def fix_existing_tasks():
    """修复现有分析任务的文件URL"""
    print("🔧 开始修复现有分析任务...")
    
    uploads_dir = Path("uploads")
    
    # 获取所有存在的分析结果文件
    result_files = {}
    for file_path in uploads_dir.glob("*_*.srt"):
        task_id = file_path.stem.split("_subtitles")[0]
        if task_id not in result_files:
            result_files[task_id] = {}
        result_files[task_id]["subtitle_srt_url"] = f"/uploads/{file_path.name}"
    
    for file_path in uploads_dir.glob("*_*.pdf"):
        task_id = file_path.stem.split("_report")[0]
        if task_id not in result_files:
            result_files[task_id] = {}
        result_files[task_id]["report_pdf_url"] = f"/uploads/{file_path.name}"
    
    print(f"📁 发现 {len(result_files)} 个任务的结果文件")
    
    # 更新内存存储中的任务
    updated_count = 0
    for task_id, urls in result_files.items():
        if task_id in _task_storage:
            # 更新内存存储
            _task_storage[task_id].update(urls)
            _task_storage[task_id]["status"] = "completed"
            _task_storage[task_id]["progress"] = "100"
            print(f"✅ 内存存储已更新: {task_id} -> {urls}")
            updated_count += 1
        
        # 尝试更新Supabase
        try:
            update_data = {
                **urls,
                "status": "completed",
                "progress": "100"
            }
            await db_manager.update_analysis_task(task_id, update_data)
            print(f"✅ Supabase已更新: {task_id}")
        except Exception as e:
            print(f"⚠️ Supabase更新失败 {task_id}: {e}")
    
    print(f"\n🎉 修复完成! 共更新了 {updated_count} 个任务")
    
    # 显示当前任务状态
    print("\n📊 当前任务状态:")
    for task_id, task_info in _task_storage.items():
        status = task_info.get("status", "unknown")
        progress = task_info.get("progress", "0")
        video_id = task_info.get("video_id", "unknown")
        has_subtitle = "✅" if task_info.get("subtitle_srt_url") else "❌"
        has_report = "✅" if task_info.get("report_pdf_url") else "❌"
        
        print(f"  {task_id[:8]}... | {status:>10} | {progress:>3}% | 字幕:{has_subtitle} | 报告:{has_report} | 视频:{video_id[:8]}...")

if __name__ == "__main__":
    asyncio.run(fix_existing_tasks()) 
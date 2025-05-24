#!/usr/bin/env python3
"""
测试当前使用的分析器是否为AI版本
"""

import sys
import os
from pathlib import Path
import time

# 添加backend路径
backend_path = Path(__file__).parent / "video-learning-helper-backend"
sys.path.append(str(backend_path))

from app.task_processor import task_processor, submit_analysis_task
from app.database_supabase import db_manager
import asyncio

async def test_current_analyzer():
    """测试当前分析器"""
    print("🔍 测试当前使用的分析器...")
    
    # 测试视频路径
    video_path = "/Users/apulu/Desktop/learning/写给自卑的自己的一封信 - 001 - 写给自卑的自己的一封信.mp4"
    
    if not Path(video_path).exists():
        print(f"❌ 测试视频不存在: {video_path}")
        return
    
    # 生成测试任务ID
    task_id = f"ai_test_{int(time.time())}"
    
    print(f"📋 任务ID: {task_id}")
    print(f"📹 视频: {Path(video_path).name}")
    
    try:
        # 启动任务处理器
        await task_processor.start()
        
        # 创建分析任务
        task_config = {
            "video_segmentation": True,
            "transition_detection": True,
            "audio_transcription": False,  # 暂时跳过音频
            "report_generation": False
        }
        
        # 在数据库中创建任务记录
        task_data = {
            "id": task_id,
            "video_id": "test-video-id",
            "task_config": task_config,
            "status": "pending",
            "progress": "0",
            "created_at": "2025-01-25T08:58:00.000Z",
            "updated_at": "2025-01-25T08:58:00.000Z"
        }
        
        try:
            result = db_manager.client.table("analysis_tasks").insert(task_data).execute()
            print(f"✅ 任务已创建在数据库中")
        except Exception as e:
            print(f"⚠️  数据库插入失败，但继续测试: {e}")
        
        # 提交任务
        await submit_analysis_task(task_id, video_path, task_config)
        print(f"📤 任务已提交到处理器")
        
        # 监控任务进度
        print(f"⏳ 等待分析完成...")
        
        for i in range(60):  # 最多等待60秒
            await asyncio.sleep(1)
            
            # 检查任务状态
            try:
                result = db_manager.client.table("analysis_tasks").select("*").eq("id", task_id).execute()
                if result.data:
                    task_status = result.data[0]
                    status = task_status.get("status", "unknown")
                    progress = task_status.get("progress", "0")
                    
                    print(f"状态: {status} ({progress}%)", end="\r")
                    
                    if status == "completed":
                        print(f"\n✅ 分析完成！")
                        break
                    elif status == "failed":
                        error_msg = task_status.get("error_message", "未知错误")
                        print(f"\n❌ 分析失败: {error_msg}")
                        return
            except Exception as e:
                print(f".", end="")  # 简单的进度指示
        
        # 检查结果文件
        uploads_dir = Path("video-learning-helper-backend/uploads")
        results_file = uploads_dir / f"{task_id}_results.json"
        
        if results_file.exists():
            import json
            with open(results_file, 'r', encoding='utf-8') as f:
                results = json.load(f)
            
            segments = results.get("segments", [])
            print(f"\n📊 分析结果:")
            print(f"片段数量: {len(segments)}")
            
            if segments:
                print(f"\n🎬 片段详情:")
                for i, segment in enumerate(segments[:10]):  # 只显示前10个
                    duration = segment.get('duration', 0)
                    start_time = segment.get('start_time', 0)
                    end_time = segment.get('end_time', 0)
                    scene_type = segment.get('scene_type', '未知')
                    
                    print(f"  片段 {i+1}: {start_time:.1f}s - {end_time:.1f}s ({duration:.1f}s) [{scene_type}]")
                
                if len(segments) > 10:
                    print(f"  ... 还有 {len(segments) - 10} 个片段")
                
                # 检查是否是AI智能分割
                durations = [s.get('duration', 0) for s in segments]
                avg_duration = sum(durations) / len(durations)
                variance = sum((d - avg_duration) ** 2 for d in durations) / len(durations)
                std_dev = variance ** 0.5
                
                print(f"\n📈 分割质量分析:")
                print(f"平均片段长度: {avg_duration:.1f} 秒")
                print(f"标准差: {std_dev:.1f} 秒")
                
                if std_dev > 5.0:
                    print("✅ 确认使用AI智能分割！片段长度变化明显")
                else:
                    print("⚠️  可能仍在使用固定时间分割")
                
                # 检查是否所有片段都是30秒
                thirty_second_segments = [d for d in durations if abs(d - 30.0) < 0.1]
                if len(thirty_second_segments) > len(segments) * 0.8:
                    print("❌ 警告：80%以上片段都是30秒，可能仍在使用简单分割器！")
                else:
                    print("✅ 片段长度多样化，确认使用AI分析器")
        else:
            print(f"\n❌ 结果文件不存在: {results_file}")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await task_processor.stop()

if __name__ == "__main__":
    asyncio.run(test_current_analyzer()) 
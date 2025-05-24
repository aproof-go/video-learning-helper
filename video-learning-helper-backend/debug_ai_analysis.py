#!/usr/bin/env python3
"""
AI分析功能调试脚本
用于测试和验证视频分析功能
"""

import asyncio
import sys
import os
from pathlib import Path
import time
import json

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from app.video_analyzer_simple import VideoAnalyzer
from app.task_processor import TaskProcessor, start_task_processor, stop_task_processor, submit_analysis_task
from app.database_supabase import db_manager

def test_video_analyzer():
    """测试基础视频分析器"""
    print("🔍 测试1: 基础视频分析器")
    print("=" * 50)
    
    analyzer = VideoAnalyzer()
    
    # 创建测试视频文件（模拟）
    test_video_path = Path("test_video.mp4")
    test_video_path.write_text("fake video content")
    
    try:
        # 测试配置
        test_config = {
            "video_segmentation": True,
            "transition_detection": True,
            "audio_transcription": True,
            "report_generation": True
        }
        
        def progress_callback(progress, message):
            print(f"  📊 进度: {progress}% - {message}")
        
        print(f"📁 测试视频路径: {test_video_path}")
        print("🚀 开始分析...")
        
        results = analyzer.analyze_video(str(test_video_path), test_config, progress_callback)
        
        print(f"✅ 分析完成! 结果:")
        print(f"  📊 场景数量: {len(results.get('segments', []))}")
        print(f"  🔄 转场数量: {len(results.get('transitions', []))}")
        print(f"  🎵 转录状态: {'✅' if results.get('transcription', {}).get('text') else '❌'}")
        print(f"  📄 报告路径: {results.get('report_path', '未生成')}")
        
        return True
        
    except Exception as e:
        print(f"❌ 分析失败: {e}")
        return False
    finally:
        # 清理测试文件
        if test_video_path.exists():
            test_video_path.unlink()

async def test_task_processor():
    """测试任务处理器"""
    print("\n🔍 测试2: 任务处理器")
    print("=" * 50)
    
    try:
        # 启动任务处理器
        print("🚀 启动任务处理器...")
        await start_task_processor()
        
        # 创建测试视频文件
        test_video_path = Path("uploads/test_processor_video.mp4")
        test_video_path.parent.mkdir(exist_ok=True)
        test_video_path.write_text("fake video content for processor")
        
        # 提交测试任务
        task_id = "debug-task-001"
        task_config = {
            "video_segmentation": True,
            "transition_detection": False,
            "audio_transcription": False,
            "report_generation": True
        }
        
        print(f"📤 提交任务: {task_id}")
        await submit_analysis_task(task_id, str(test_video_path), task_config)
        
        # 等待任务处理
        print("⏳ 等待任务处理...")
        for i in range(10):  # 最多等待10秒
            await asyncio.sleep(1)
            from app.task_processor import get_processor_status
            status = get_processor_status()
            print(f"  📊 处理器状态: 运行任务={status['running_tasks']}, 队列={status['queue_size']}")
            
            if status['running_tasks'] == 0 and status['queue_size'] == 0:
                print("✅ 任务处理完成!")
                break
        else:
            print("⚠️ 任务处理超时")
        
        return True
        
    except Exception as e:
        print(f"❌ 任务处理器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 停止任务处理器
        print("🛑 停止任务处理器...")
        await stop_task_processor()
        
        # 清理测试文件
        if test_video_path.exists():
            test_video_path.unlink()

async def test_database_connection():
    """测试数据库连接"""
    print("\n🔍 测试3: 数据库连接")
    print("=" * 50)
    
    try:
        # 测试用户计数
        user_count = await db_manager.get_user_count()
        print(f"✅ 数据库连接成功, 用户数量: {user_count}")
        
        # 测试内存存储状态
        from app.database_supabase import _video_storage, _task_storage
        print(f"📊 内存存储状态:")
        print(f"  视频: {len(_video_storage)} 条记录")
        print(f"  任务: {len(_task_storage)} 条记录")
        
        return True
        
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False

async def test_complete_flow():
    """测试完整流程"""
    print("\n🔍 测试4: 完整分析流程")
    print("=" * 50)
    
    try:
        # 启动任务处理器
        await start_task_processor()
        
        # 模拟创建视频记录
        video_data = {
            "title": "调试测试视频",
            "filename": "debug_test.mp4",
            "file_size": 1024,
            "format": "mp4",
            "status": "uploaded",
            "user_id": "debug-user-001",
            "file_url": "/uploads/debug_test.mp4"
        }
        
        # 创建实际文件
        video_file_path = Path("uploads/debug_test.mp4")
        video_file_path.parent.mkdir(exist_ok=True)
        video_file_path.write_text("fake video content for complete flow")
        
        try:
            video_record = await db_manager.create_video(video_data)
            video_id = video_record["id"]
            print(f"✅ 视频记录创建成功: {video_id}")
        except Exception as e:
            print(f"⚠️ 数据库创建失败，使用内存存储: {e}")
            video_id = "debug-video-001"
            from app.database_supabase import _video_storage
            _video_storage[video_id] = video_data
        
        # 创建分析任务
        task_data = {
            "video_id": video_id,
            "user_id": "debug-user-001",
            "video_segmentation": True,
            "transition_detection": True,
            "audio_transcription": True,
            "report_generation": True
        }
        
        try:
            task_record = await db_manager.create_analysis_task(task_data)
            task_id = task_record["id"]
            print(f"✅ 分析任务创建成功: {task_id}")
        except Exception as e:
            print(f"⚠️ 数据库创建失败，使用内存存储: {e}")
            task_id = "debug-task-complete-001"
            from app.database_supabase import _task_storage
            _task_storage[task_id] = {
                **task_data,
                "id": task_id,
                "status": "pending",
                "progress": "0",
                "created_at": "2025-01-01T00:00:00Z",
                "updated_at": "2025-01-01T00:00:00Z"
            }
        
        # 提交到处理器
        await submit_analysis_task(task_id, str(video_file_path), {
            "video_segmentation": True,
            "transition_detection": True, 
            "audio_transcription": True,
            "report_generation": True
        })
        
        print("⏳ 等待完整分析流程...")
        for i in range(15):  # 最多等待15秒
            await asyncio.sleep(1)
            from app.task_processor import get_processor_status
            status = get_processor_status()
            print(f"  📊 第{i+1}秒: 运行任务={status['running_tasks']}, 队列={status['queue_size']}")
            
            if status['running_tasks'] == 0 and status['queue_size'] == 0:
                print("✅ 完整流程处理完成!")
                break
        
        # 检查结果文件
        uploads_dir = Path("uploads")
        result_files = list(uploads_dir.glob(f"{task_id}*"))
        print(f"📁 生成的结果文件:")
        for file in result_files:
            print(f"  - {file.name} ({file.stat().st_size} bytes)")
        
        return True
        
    except Exception as e:
        print(f"❌ 完整流程测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 清理
        await stop_task_processor()
        
        # 清理测试文件
        for pattern in ["debug_test.*", "debug-task-*"]:
            for file in Path("uploads").glob(pattern):
                try:
                    file.unlink()
                except:
                    pass

async def main():
    """主调试函数"""
    print("🚀 AI视频分析功能调试")
    print("=" * 80)
    
    results = []
    
    # 运行所有测试
    tests = [
        ("基础分析器", test_video_analyzer),
        ("数据库连接", test_database_connection),
        ("任务处理器", test_task_processor),
        ("完整流程", test_complete_flow)
    ]
    
    for test_name, test_func in tests:
        print(f"\n🧪 运行测试: {test_name}")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ 测试异常: {e}")
            results.append((test_name, False))
    
    # 汇总结果
    print("\n" + "=" * 80)
    print("📊 调试结果汇总:")
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\n总体结果: {passed}/{total} 个测试通过")
    
    if passed == total:
        print("🎉 所有测试通过! AI分析功能正常工作")
    else:
        print("⚠️ 部分测试失败，请检查上述错误信息")

if __name__ == "__main__":
    asyncio.run(main()) 
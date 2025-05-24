#!/usr/bin/env python3
"""
重新分析现有视频的脚本
"""

import sys
import asyncio
import requests
import json
from pathlib import Path
import time

# 添加backend路径
backend_path = Path(__file__).parent / "video-learning-helper-backend"
sys.path.append(str(backend_path))

from app.task_processor import submit_analysis_task
from app.database_supabase import db_manager

async def reanalyze_video():
    """重新分析视频"""
    print("🔄 视频重新分析工具")
    print("=" * 50)
    
    # 1. 获取登录token
    try:
        login_resp = requests.post('http://localhost:8000/api/v1/auth/login', 
                                  json={'email': 'frontend_test@example.com', 'password': 'test123456'})
        if login_resp.status_code != 200:
            print("❌ 登录失败，请检查后端服务是否正常运行")
            return
        
        token = login_resp.json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        print("✅ 登录成功")
    except Exception as e:
        print(f"❌ 登录失败: {e}")
        return

    # 2. 获取用户的视频列表
    try:
        videos_resp = requests.get('http://localhost:8000/api/v1/videos', headers=headers)
        if videos_resp.status_code != 200:
            print("❌ 获取视频列表失败")
            return
        
        videos = videos_resp.json()
        if not videos:
            print("❌ 没有找到任何视频")
            return
        
        print(f"\n📹 找到 {len(videos)} 个视频:")
        for i, video in enumerate(videos):
            print(f"  {i+1}. {video['filename']}")
            print(f"     ID: {video['id']}")
            print(f"     大小: {video['file_size'] / 1024 / 1024:.1f} MB")
            print(f"     上传时间: {video['created_at'][:19]}")
            print()
        
    except Exception as e:
        print(f"❌ 获取视频列表失败: {e}")
        return

    # 3. 让用户选择视频
    while True:
        try:
            choice = input(f"请选择要重新分析的视频 (1-{len(videos)}, 或输入 'q' 退出): ").strip()
            if choice.lower() == 'q':
                print("👋 退出")
                return
            
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(videos):
                selected_video = videos[choice_idx]
                break
            else:
                print(f"❌ 请输入 1 到 {len(videos)} 之间的数字")
        except ValueError:
            print("❌ 请输入有效的数字")

    video_id = selected_video['id']
    video_filename = selected_video['filename']
    print(f"\n🎯 选择的视频: {video_filename}")

    # 4. 获取现有分析任务
    try:
        tasks_resp = requests.get(f'http://localhost:8000/api/v1/analysis/videos/{video_id}/tasks', 
                                 headers=headers)
        if tasks_resp.status_code == 200:
            existing_tasks = tasks_resp.json()
            if existing_tasks:
                print(f"\n📋 现有分析任务 ({len(existing_tasks)} 个):")
                for i, task in enumerate(existing_tasks):
                    print(f"  {i+1}. {task['id'][:8]}... - {task['status']} - {task['created_at'][:19]}")
        else:
            existing_tasks = []
    except Exception as e:
        print(f"⚠️  获取现有任务失败: {e}")
        existing_tasks = []

    # 5. 配置分析选项
    print(f"\n⚙️  配置分析选项:")
    
    config = {}
    config['video_segmentation'] = input("启用视频分割? (Y/n): ").strip().lower() != 'n'
    config['transition_detection'] = input("启用转场检测? (Y/n): ").strip().lower() != 'n'
    config['audio_transcription'] = input("启用音频转录? (y/N): ").strip().lower() == 'y'
    config['report_generation'] = input("启用报告生成? (y/N): ").strip().lower() == 'y'

    print(f"\n📊 分析配置:")
    for key, value in config.items():
        status = "✅" if value else "❌"
        print(f"  {status} {key}: {value}")

    # 6. 确认创建新任务
    confirm = input(f"\n🚀 确认为视频 '{video_filename}' 创建新的AI分析任务? (y/N): ").strip().lower()
    if confirm != 'y':
        print("❌ 取消操作")
        return

    # 7. 创建新的分析任务
    try:
        task_data = {
            'video_id': video_id,
            'video_segmentation': config['video_segmentation'],
            'transition_detection': config['transition_detection'],
            'audio_transcription': config['audio_transcription'],
            'report_generation': config['report_generation']
        }
        
        task_resp = requests.post('http://localhost:8000/api/v1/analysis/tasks',
                                json=task_data, headers=headers)
        
        if task_resp.status_code != 200:
            error_data = task_resp.json() if task_resp.headers.get('content-type', '').startswith('application/json') else {}
            print(f"❌ 创建分析任务失败: {task_resp.status_code}")
            print(f"   错误信息: {error_data.get('detail', task_resp.text)}")
            return
        
        new_task = task_resp.json()
        task_id = new_task['id']
        print(f"✅ 新分析任务已创建: {task_id}")

    except Exception as e:
        print(f"❌ 创建分析任务失败: {e}")
        return

    # 8. 监控分析进度
    print(f"\n⏳ 开始监控分析进度...")
    print("   (按 Ctrl+C 可以停止监控，任务会继续在后台运行)")
    
    try:
        for i in range(300):  # 最多监控5分钟
            await asyncio.sleep(2)
            
            try:
                status_resp = requests.get(f'http://localhost:8000/api/v1/analysis/tasks/{task_id}',
                                         headers=headers)
                if status_resp.status_code == 200:
                    task_status = status_resp.json()
                    status = task_status['status']
                    progress = task_status['progress']
                    
                    if status == 'completed':
                        print(f"\n🎉 分析完成！")
                        print(f"   任务ID: {task_id}")
                        print(f"   可以访问: http://localhost:3000/analysis/{video_id}")
                        break
                    elif status == 'failed':
                        error_msg = task_status.get('error_message', '未知错误')
                        print(f"\n❌ 分析失败: {error_msg}")
                        break
                    else:
                        print(f"\r   状态: {status} ({progress}%)", end="", flush=True)
                else:
                    print(".", end="", flush=True)
            except KeyboardInterrupt:
                print(f"\n⏸️  监控已停止，但任务继续在后台运行")
                print(f"   任务ID: {task_id}")
                print(f"   可以稍后访问: http://localhost:3000/analysis/{video_id}")
                break
            except Exception:
                print(".", end="", flush=True)
    
    except KeyboardInterrupt:
        print(f"\n⏸️  监控已停止，但任务继续在后台运行")
        print(f"   任务ID: {task_id}")
        print(f"   可以稍后访问: http://localhost:3000/analysis/{video_id}")

if __name__ == "__main__":
    asyncio.run(reanalyze_video()) 
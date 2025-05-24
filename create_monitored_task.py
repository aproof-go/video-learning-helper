#!/usr/bin/env python3
"""
创建新的AI分析任务并监控整个过程
"""

import asyncio
import json
import requests
import time
from pathlib import Path

async def create_and_monitor_task():
    """创建并监控AI分析任务"""
    print("🧠 创建并监控新的AI分析任务")
    print("=" * 60)
    
    # 1. 登录获取token
    try:
        login_resp = requests.post('http://localhost:8000/api/v1/auth/login', 
                                  json={'email': 'frontend_test@example.com', 'password': 'test123456'})
        if login_resp.status_code != 200:
            print("❌ 登录失败")
            return
        
        token = login_resp.json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        print("✅ 登录成功")
    except Exception as e:
        print(f"❌ 登录失败: {e}")
        return

    # 2. 获取目标视频
    video_id = '90c13d7f-6202-4439-809f-f066f6be3628'  # 测试视频ID
    print(f"🎯 目标视频ID: {video_id}")
    
    # 3. 创建新的AI分析任务
    task_data = {
        'video_id': video_id,
        'video_segmentation': True,
        'transition_detection': True, 
        'audio_transcription': True,
        'report_generation': True
    }
    
    print(f"📝 创建任务配置: {task_data}")
    
    try:
        create_resp = requests.post(
            'http://localhost:8000/api/v1/analysis/tasks',
            headers=headers,
            json=task_data
        )
        
        if create_resp.status_code != 200:
            print(f"❌ 创建任务失败: {create_resp.status_code}")
            print(create_resp.text)
            return
            
        task_result = create_resp.json()
        new_task_id = task_result['id']
        print(f"✅ 任务创建成功，ID: {new_task_id}")
        
    except Exception as e:
        print(f"❌ 创建任务失败: {e}")
        return
    
    # 4. 监控任务状态
    print(f"\n🔍 监控任务进度...")
    
    for i in range(180):  # 最多监控3分钟
        try:
            # 获取任务状态
            status_resp = requests.get(
                f'http://localhost:8000/api/v1/analysis/videos/{video_id}/tasks',
                headers=headers
            )
            
            if status_resp.status_code == 200:
                tasks = status_resp.json()
                current_task = None
                
                for task in tasks:
                    if task['id'] == new_task_id:
                        current_task = task
                        break
                
                if current_task:
                    status = current_task['status']
                    progress = current_task.get('progress', '0')
                    
                    print(f"⏳ [{i*5:03d}s] 状态: {status}, 进度: {progress}%")
                    
                    if status == 'completed':
                        print(f"✅ 任务完成！检查结果文件...")
                        
                        # 检查结果文件
                        results_file = Path(f"video-learning-helper-backend/uploads/{new_task_id}_results.json")
                        if results_file.exists():
                            with open(results_file) as f:
                                results = json.load(f)
                            
                            segments = results.get('segments', [])
                            print(f"\n📊 分析结果:")
                            print(f"   总片段数: {len(segments)}")
                            
                            if segments:
                                durations = [s['duration'] for s in segments]
                                scene_types = {s.get('scene_type', '未知') for s in segments}
                                
                                print(f"   片段时长范围: {min(durations):.1f}s - {max(durations):.1f}s")
                                print(f"   平均时长: {sum(durations)/len(durations):.1f}s")
                                print(f"   场景类型: {scene_types}")
                                
                                # 检查是否所有片段都是30秒
                                all_30_seconds = all(abs(d - 30.0) < 0.1 for d in durations)
                                if all_30_seconds:
                                    print("⚠️  警告: 所有片段都是30秒！")
                                    print("📋 前5个片段详情:")
                                    for i, segment in enumerate(segments[:5]):
                                        print(f"     片段{segment['segment_id']}: {segment['start_time']}s-{segment['end_time']}s ({segment['duration']}s) {segment.get('scene_type', '未知')}")
                                else:
                                    print("✅ 片段长度变化，符合AI智能分割")
                                    print("📋 前5个片段详情:")
                                    for i, segment in enumerate(segments[:5]):
                                        print(f"     片段{segment['segment_id']}: {segment['start_time']}s-{segment['end_time']}s ({segment['duration']}s) {segment.get('scene_type', '未知')}")
                        
                        break
                    
                    elif status == 'failed':
                        error_msg = current_task.get('error_message', '未知错误')
                        print(f"❌ 任务失败: {error_msg}")
                        break
                        
                else:
                    print(f"❓ 未找到任务 {new_task_id}")
                    
            await asyncio.sleep(5)  # 每5秒检查一次
            
        except Exception as e:
            print(f"❌ 监控失败: {e}")
            break
    
    else:
        print("⏰ 监控超时，任务可能仍在进行中")

if __name__ == "__main__":
    asyncio.run(create_and_monitor_task()) 
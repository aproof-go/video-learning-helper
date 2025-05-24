#!/usr/bin/env python3
"""
前端调用调试工具 - 模拟前端的数据获取流程
"""

import requests
import json
from datetime import datetime

def debug_frontend_calls():
    """调试前端调用流程"""
    print("🔍 前端调用流程调试")
    print("=" * 50)
    
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

    # 2. 获取视频列表
    try:
        videos_resp = requests.get('http://localhost:8000/api/v1/videos', headers=headers)
        videos = videos_resp.json()
        
        print(f"\n📹 用户视频列表 ({len(videos)} 个):")
        for i, video in enumerate(videos):
            print(f"  {i+1}. {video['filename']} (ID: {video['id']})")
        
        if not videos:
            print("❌ 没有视频")
            return
            
        # 选择第一个视频进行测试
        test_video = videos[0]
        video_id = test_video['id']
        print(f"\n🎯 测试视频: {test_video['filename']} (ID: {video_id})")
        
    except Exception as e:
        print(f"❌ 获取视频列表失败: {e}")
        return

    # 3. 模拟前端的任务获取流程
    try:
        print(f"\n📋 步骤1: 获取视频的分析任务列表...")
        tasks_url = f'http://localhost:8000/api/v1/analysis/videos/{video_id}/tasks'
        print(f"   API调用: {tasks_url}")
        
        tasks_resp = requests.get(tasks_url, headers=headers)
        if tasks_resp.status_code != 200:
            print(f"❌ 获取任务失败: {tasks_resp.status_code}")
            return
            
        tasks = tasks_resp.json()
        print(f"   ✅ 获取到 {len(tasks)} 个任务")
        
        # 显示所有任务
        print(f"\n📊 所有分析任务:")
        for i, task in enumerate(tasks):
            created_time = datetime.fromisoformat(task['created_at'].replace('Z', '+00:00'))
            print(f"  {i+1}. 任务ID: {task['id'][:8]}...")
            print(f"     状态: {task['status']}")
            print(f"     创建时间: {created_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"     视频分割: {task.get('video_segmentation', False)}")
            print(f"     转场检测: {task.get('transition_detection', False)}")
            print(f"     音频转录: {task.get('audio_transcription', False)}")
            print()
        
        # 4. 模拟前端的任务选择逻辑
        print(f"📋 步骤2: 前端任务选择逻辑...")
        completed_tasks = [task for task in tasks if task['status'] == 'completed']
        print(f"   已完成任务数: {len(completed_tasks)}")
        
        if not completed_tasks:
            print("   ❌ 没有已完成的任务")
            return
        
        # 按创建时间排序，选择最新的
        latest_task = sorted(completed_tasks, 
                           key=lambda x: datetime.fromisoformat(x['created_at'].replace('Z', '+00:00')), 
                           reverse=True)[0]
        
        print(f"   🎯 前端会选择: 任务ID {latest_task['id'][:8]}... (最新完成的任务)")
        print(f"   创建时间: {latest_task['created_at']}")
        
        # 5. 模拟前端加载分析结果
        print(f"\n📋 步骤3: 加载分析结果文件...")
        results_url = f"http://localhost:8000/uploads/{latest_task['id']}_results.json"
        print(f"   文件URL: {results_url}")
        
        try:
            results_resp = requests.get(results_url)
            if results_resp.status_code == 200:
                results = results_resp.json()
                print(f"   ✅ 结果文件加载成功")
                
                # 分析结果内容
                print(f"\n📊 分析结果内容:")
                segments = results.get('segments', [])
                transitions = results.get('transitions', [])
                transcription = results.get('transcription', {})
                
                print(f"   视频时长: {results.get('video_info', {}).get('duration', '未知')} 秒")
                print(f"   片段数量: {len(segments)}")
                print(f"   转场数量: {len(transitions)}")
                print(f"   转录段数: {len(transcription.get('segments', []))}")
                
                # 检查是否是AI智能分割
                if segments:
                    durations = [s['duration'] for s in segments]
                    avg_duration = sum(durations) / len(durations)
                    min_duration = min(durations)
                    max_duration = max(durations)
                    
                    print(f"\n🧠 分割质量分析:")
                    print(f"   平均片段长度: {avg_duration:.1f}秒")
                    print(f"   最短片段: {min_duration:.1f}秒")
                    print(f"   最长片段: {max_duration:.1f}秒")
                    
                    # 检查是否是固定30秒分割
                    if all(abs(d - 30.0) < 0.1 for d in durations):
                        print(f"   ⚠️  检测到固定30秒分割（可能是旧版本分析器）")
                    else:
                        print(f"   ✅ 检测到AI智能分割（变长片段）")
                
                # 显示前几个片段
                print(f"\n🎬 前5个片段详情:")
                for i, segment in enumerate(segments[:5]):
                    print(f"   片段{segment['segment_id']}: {segment['start_time']:.1f}s-{segment['end_time']:.1f}s ({segment['duration']:.1f}s) - {segment.get('scene_type', '未知场景')}")
                
            else:
                print(f"   ❌ 结果文件加载失败: HTTP {results_resp.status_code}")
                
        except Exception as e:
            print(f"   ❌ 加载结果文件异常: {e}")
        
    except Exception as e:
        print(f"❌ 任务处理失败: {e}")

if __name__ == "__main__":
    debug_frontend_calls() 
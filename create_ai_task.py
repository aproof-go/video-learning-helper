#!/usr/bin/env python3
"""
创建新的AI分析任务
"""

import asyncio
import sys
import requests
from pathlib import Path
import json

async def create_ai_task_via_api():
    """通过API创建AI分析任务"""
    print("🧠 创建新的AI分析任务")
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

    # 2. 获取目标视频
    video_id = '90c13d7f-6202-4439-809f-f066f6be3628'  # 测试视频ID
    print(f"🎯 目标视频ID: {video_id}")

    # 3. 创建新的AI分析任务
    task_data = {
        'video_id': video_id,
        'video_segmentation': True,    # 启用AI视频分割
        'transition_detection': True,  # 启用转场检测
        'audio_transcription': True,   # 启用音频转录
        'report_generation': True      # 启用报告生成
    }
    
    print(f"\n🚀 分析配置:")
    for key, value in task_data.items():
        if key != 'video_id':
            status = "✅" if value else "❌"
            print(f"  {status} {key}: {value}")

    try:
        print(f"\n📤 提交分析任务...")
        task_resp = requests.post('http://localhost:8000/api/v1/analysis/tasks',
                                json=task_data, headers=headers)
        
        if task_resp.status_code != 200:
            error_data = task_resp.json() if task_resp.headers.get('content-type', '').startswith('application/json') else {}
            print(f"❌ 创建分析任务失败: {task_resp.status_code}")
            print(f"   错误信息: {error_data.get('detail', task_resp.text)}")
            return
        
        new_task = task_resp.json()
        task_id = new_task['id']
        print(f"✅ 新AI分析任务已创建: {task_id}")

        # 4. 监控分析进度
        print(f"\n⏳ 监控分析进度...")
        print("   (等待AI处理，这可能需要几分钟)")
        
        for i in range(180):  # 最多监控3分钟
            await asyncio.sleep(2)
            
            try:
                status_resp = requests.get(f'http://localhost:8000/api/v1/analysis/tasks/{task_id}',
                                         headers=headers)
                if status_resp.status_code == 200:
                    task_status = status_resp.json()
                    status = task_status['status']
                    progress = task_status['progress']
                    
                    if status == 'completed':
                        print(f"\n🎉 AI分析完成！")
                        print(f"   任务ID: {task_id}")
                        
                        # 验证结果质量
                        await verify_ai_results(task_id)
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
                break
            except Exception:
                print(".", end="", flush=True)
    
    except Exception as e:
        print(f"❌ 任务处理失败: {e}")

async def verify_ai_results(task_id: str):
    """验证AI分析结果质量"""
    try:
        results_url = f"http://localhost:8000/uploads/{task_id}_results.json"
        results_resp = requests.get(results_url)
        
        if results_resp.status_code == 200:
            results = results_resp.json()
            segments = results.get('segments', [])
            
            if segments:
                durations = [s['duration'] for s in segments]
                avg_duration = sum(durations) / len(durations)
                min_duration = min(durations)
                max_duration = max(durations)
                
                print(f"\n📊 AI分析结果验证:")
                print(f"   片段数量: {len(segments)}")
                print(f"   平均长度: {avg_duration:.1f}秒")
                print(f"   最短片段: {min_duration:.1f}秒")
                print(f"   最长片段: {max_duration:.1f}秒")
                
                # 检查是否是真正的AI分割
                if all(abs(d - 30.0) < 0.1 for d in durations):
                    print(f"   ⚠️  仍然是固定30秒分割")
                else:
                    print(f"   ✅ 确认为AI智能分割（变长片段）")
                    
                print(f"\n🎬 前5个片段:")
                for segment in segments[:5]:
                    print(f"   片段{segment['segment_id']}: {segment['start_time']:.1f}s-{segment['end_time']:.1f}s ({segment['duration']:.1f}s)")
        else:
            print(f"   ❌ 无法加载结果文件: HTTP {results_resp.status_code}")
            
    except Exception as e:
        print(f"   ❌ 验证结果时出错: {e}")

if __name__ == "__main__":
    asyncio.run(create_ai_task_via_api()) 
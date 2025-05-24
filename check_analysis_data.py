#!/usr/bin/env python3
"""
检查分析数据的真实性
"""
import requests
import json

def main():
    print("🔍 检查分析数据真实性")
    print("=" * 40)
    
    # 登录
    login_resp = requests.post('http://localhost:8000/api/v1/auth/login', 
                              json={'email': 'frontend_test@example.com', 'password': 'test123456'})
    token = login_resp.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    
    # 获取任务列表
    video_id = '1c0d168e-ddf5-47d4-8173-edc3f63a4c9b'
    tasks_resp = requests.get(f'http://localhost:8000/api/v1/analysis/videos/{video_id}/tasks', headers=headers)
    tasks = tasks_resp.json()
    
    print(f'视频ID: {video_id}')
    print(f'任务数量: {len(tasks)}')
    
    for i, task in enumerate(tasks):
        print(f'\n📋 任务{i+1}: {task["id"][:8]}...')
        print(f'   状态: {task["status"]}')
        
        if task['status'] == 'completed':
            # 检查结果文件
            results_url = f'http://localhost:8000/uploads/{task["id"]}_results.json'
            try:
                results_resp = requests.get(results_url)
                if results_resp.status_code == 200:
                    results = results_resp.json()
                    
                    print(f'   ✅ 结果文件存在')
                    print(f'   📊 视频信息:')
                    video_info = results.get('video_info', {})
                    print(f'      时长: {video_info.get("duration", "未知")} 秒')
                    print(f'      分辨率: {video_info.get("width", "?")}x{video_info.get("height", "?")}')
                    print(f'      帧率: {video_info.get("fps", "?")} FPS')
                    
                    print(f'   🎬 分析结果:')
                    segments = results.get('segments', [])
                    transitions = results.get('transitions', [])
                    transcription = results.get('transcription', {})
                    
                    print(f'      片段数: {len(segments)}')
                    print(f'      转场数: {len(transitions)}')
                    print(f'      转录段数: {len(transcription.get("segments", []))}')
                    
                    # 显示前几个片段的详情
                    if segments:
                        print(f'   📹 片段详情:')
                        for j, seg in enumerate(segments[:3]):
                            print(f'      片段{j+1}: {seg["start_time"]:.1f}-{seg["end_time"]:.1f}s ({seg["scene_type"]})')
                    
                    # 显示转场详情
                    if transitions:
                        print(f'   🔄 转场详情:')
                        for j, trans in enumerate(transitions[:3]):
                            print(f'      转场{j+1}: {trans["timestamp"]:.1f}s ({trans["type"]}, 强度:{trans["strength"]:.2f})')
                    
                else:
                    print(f'   ❌ 结果文件不存在 ({results_resp.status_code})')
            except Exception as e:
                print(f'   ❌ 检查结果文件失败: {e}')

if __name__ == "__main__":
    main() 
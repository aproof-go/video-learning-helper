#!/usr/bin/env python3
"""
为前端测试用户创建测试数据
"""
import requests
import json
import time
from pathlib import Path

def main():
    print("📦 创建前端测试数据")
    print("=" * 40)
    
    # 1. 登录
    user_email = 'frontend_test@example.com'
    password = 'test123456'
    
    login_resp = requests.post('http://localhost:8000/api/v1/auth/login', 
                              json={'email': user_email, 'password': password})
    if login_resp.status_code != 200:
        print(f'❌ 登录失败: {login_resp.text}')
        return
    
    token = login_resp.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    print('✅ 登录成功')
    
    # 2. 上传视频
    video_path = Path('video-learning-helper-backend/uploads/test_video.mp4')
    if not video_path.exists():
        print('❌ 测试视频不存在')
        return
    
    with open(video_path, 'rb') as f:
        files = {'file': (video_path.name, f, 'video/mp4')}
        data = {'title': 'Frontend Test Video', 'description': 'Test video for frontend analysis'}
        upload_resp = requests.post('http://localhost:8000/api/v1/videos/upload', 
                                   files=files, data=data, headers=headers)
    
    if upload_resp.status_code != 200:
        print(f'❌ 视频上传失败: {upload_resp.text}')
        return
    
    upload_data = upload_resp.json()
    print(f'📋 上传响应: {upload_data}')
    
    # 处理不同的响应格式
    if 'id' in upload_data:
        video_id = upload_data['id']
    elif 'video_id' in upload_data:
        video_id = upload_data['video_id']
    elif 'video' in upload_data and 'id' in upload_data['video']:
        video_id = upload_data['video']['id']
    else:
        print(f'❌ 无法从响应中获取视频ID: {upload_data}')
        return
    
    print(f'✅ 视频上传成功: {video_id}')
    
    # 3. 创建分析任务
    task_data = {
        'video_id': video_id,
        'video_segmentation': True,
        'transition_detection': True, 
        'audio_transcription': True,
        'report_generation': True
    }
    
    task_resp = requests.post('http://localhost:8000/api/v1/analysis/tasks',
                             json=task_data, headers=headers)
    
    if task_resp.status_code != 200:
        print(f'❌ 创建分析任务失败: {task_resp.text}')
        return
    
    task_id = task_resp.json()['id']
    print(f'✅ 分析任务创建成功: {task_id}')
    
    # 4. 等待任务完成
    print('⏳ 等待任务完成...')
    for i in range(60):  # 最多等待60秒
        status_resp = requests.get(f'http://localhost:8000/api/v1/analysis/tasks/{task_id}', headers=headers)
        if status_resp.status_code == 200:
            task_status = status_resp.json()['status']
            print(f'   状态: {task_status}')
            if task_status == 'completed':
                print('✅ 任务完成!')
                break
            elif task_status == 'failed':
                print('❌ 任务失败')
                return
        time.sleep(1)
    
    # 5. 检查结果文件
    json_url = f'http://localhost:8000/uploads/{task_id}_results.json'
    json_resp = requests.get(json_url)
    if json_resp.status_code == 200:
        print('✅ 分析结果文件可访问')
    else:
        print('❌ 分析结果文件不可访问')
    
    print(f'\n🌐 前端分析页面: http://localhost:3000/analysis/{video_id}')
    print('   请在浏览器中打开上述链接查看真实的分析结果')

if __name__ == "__main__":
    main() 
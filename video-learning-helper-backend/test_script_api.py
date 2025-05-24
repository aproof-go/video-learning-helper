#!/usr/bin/env python3
"""简化API测试 - 专注测试脚本功能"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_script_functionality():
    print("🚀 开始脚本功能测试")
    
    # 1. 登录
    login_data = {
        "email": "script_test@example.com",
        "password": "test123456"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=login_data)
    if response.status_code != 200:
        print(f"❌ 登录失败: {response.status_code}")
        return
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ 登录成功")
    
    # 2. 上传视频
    files = {"file": ("test_script_api.mp4", b"test video content for script", "video/mp4")}
    data = {"title": "Script Test Video"}
    
    response = requests.post(f"{BASE_URL}/api/v1/videos/upload", files=files, data=data, headers=headers)
    if response.status_code != 200:
        print(f"❌ 视频上传失败: {response.status_code}")
        return
    
    video_id = response.json()["video_id"]
    print(f"✅ 视频上传成功: {video_id}")
    
    # 3. 创建分析任务（启用音频转录）
    task_data = {
        "video_id": video_id,
        "video_segmentation": True,
        "transition_detection": True,
        "audio_transcription": True,  # 这是关键！
        "report_generation": True
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/analysis/tasks", json=task_data, headers=headers)
    if response.status_code != 200:
        print(f"❌ 任务创建失败: {response.status_code}")
        print(f"响应: {response.text}")
        return
    
    task_id = response.json()["id"]
    print(f"✅ 任务创建成功: {task_id}")
    
    # 4. 等待任务完成
    print("⏳ 等待任务完成...")
    max_wait = 30
    wait_count = 0
    
    while wait_count < max_wait:
        response = requests.get(f"{BASE_URL}/api/v1/analysis/tasks/{task_id}", headers=headers)
        if response.status_code == 200:
            task = response.json()
            status = task.get("status")
            print(f"    任务状态: {status}, 进度: {task.get('progress', '0')}%")
            
            if status == "completed":
                print("✅ 任务完成")
                
                # 检查脚本字段
                script_url = task.get("script_md_url")
                if script_url:
                    print(f"✅ 找到脚本URL: {script_url}")
                    
                    # 尝试下载脚本
                    download_response = requests.get(f"{BASE_URL}{script_url}")
                    if download_response.status_code == 200:
                        print(f"✅ 脚本下载成功: {len(download_response.content)} bytes")
                        print("📄 脚本内容预览:")
                        content = download_response.text
                        print(content[:200] + "..." if len(content) > 200 else content)
                    else:
                        print(f"❌ 脚本下载失败: HTTP {download_response.status_code}")
                else:
                    print("❌ 任务中没有脚本URL")
                    print(f"任务详情: {json.dumps(task, indent=2, ensure_ascii=False)}")
                
                break
            elif status == "failed":
                print(f"❌ 任务失败: {task.get('error_message', '未知错误')}")
                break
        
        time.sleep(2)
        wait_count += 2
    
    if wait_count >= max_wait:
        print("⏰ 任务超时")

if __name__ == "__main__":
    test_script_functionality() 
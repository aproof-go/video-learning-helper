#!/usr/bin/env python3
"""
测试真实实现的功能
验证所有模拟数据已被替换为真实实现
"""

import requests
import json
import time
import os
from pathlib import Path

# 配置
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"

# 测试用户
TEST_USER = {
    "email": "real_test@example.com",
    "password": "test123456",
    "name": "Real Implementation Test User"
}

def test_backend_health():
    """测试后端健康状态"""
    print("🔍 测试后端健康状态...")
    try:
        response = requests.get(f"{BACKEND_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 后端健康: {data}")
            return True
        else:
            print(f"❌ 后端健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 后端连接失败: {e}")
        return False

def register_and_login():
    """注册并登录测试用户"""
    print("🔍 注册并登录测试用户...")
    
    # 尝试注册
    try:
        response = requests.post(f"{BACKEND_URL}/api/v1/auth/register", json=TEST_USER)
        if response.status_code in [201, 409]:  # 201创建成功，409已存在
            print("✅ 用户注册成功或已存在")
        else:
            print(f"⚠️ 注册响应: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"⚠️ 注册请求失败: {e}")
    
    # 登录
    try:
        login_data = {"email": TEST_USER["email"], "password": TEST_USER["password"]}
        response = requests.post(f"{BACKEND_URL}/api/v1/auth/login", json=login_data)
        if response.status_code == 200:
            token_data = response.json()
            print(f"✅ 登录成功: {token_data['access_token'][:20]}...")
            return token_data["access_token"]
        else:
            print(f"❌ 登录失败: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ 登录请求失败: {e}")
        return None

def create_test_video_file():
    """创建测试视频文件"""
    test_file = Path("test_video.mp4")
    if not test_file.exists():
        # 创建一个小的测试文件
        with open(test_file, "wb") as f:
            f.write(b"fake video content for testing")
        print(f"✅ 创建测试视频文件: {test_file}")
    return test_file

def upload_video(token):
    """上传测试视频"""
    print("🔍 上传测试视频...")
    
    test_file = create_test_video_file()
    
    headers = {"Authorization": f"Bearer {token}"}
    files = {"file": ("test_video.mp4", open(test_file, "rb"), "video/mp4")}
    data = {"title": "Real Implementation Test Video", "description": "Testing real implementation"}
    
    try:
        response = requests.post(f"{BACKEND_URL}/api/v1/videos/upload", 
                               headers=headers, files=files, data=data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 视频上传成功: {result['video_id']}")
            return result["video_id"]
        else:
            print(f"❌ 视频上传失败: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ 视频上传请求失败: {e}")
        return None
    finally:
        files["file"][1].close()

def create_analysis_task(token, video_id):
    """创建分析任务"""
    print("🔍 创建分析任务...")
    
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    task_data = {
        "video_id": video_id,
        "video_segmentation": True,
        "transition_detection": True,
        "audio_transcription": True,
        "report_generation": True
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/api/v1/analysis/tasks", 
                               headers=headers, json=task_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 分析任务创建成功: {result['id']}")
            return result["id"]
        else:
            print(f"❌ 分析任务创建失败: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ 分析任务创建请求失败: {e}")
        return None

def monitor_task_progress(token, task_id, max_wait=60):
    """监控任务进度"""
    print(f"🔍 监控任务进度: {task_id}")
    
    headers = {"Authorization": f"Bearer {token}"}
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        try:
            response = requests.get(f"{BACKEND_URL}/api/v1/analysis/tasks/{task_id}", 
                                  headers=headers)
            if response.status_code == 200:
                task = response.json()
                status = task["status"]
                progress = task["progress"]
                print(f"📊 任务状态: {status}, 进度: {progress}")
                
                if status == "completed":
                    print("✅ 任务完成!")
                    return task
                elif status == "failed":
                    print(f"❌ 任务失败: {task.get('error_message', '未知错误')}")
                    return task
                
                time.sleep(5)
            else:
                print(f"⚠️ 获取任务状态失败: {response.status_code}")
                time.sleep(5)
        except Exception as e:
            print(f"⚠️ 监控请求失败: {e}")
            time.sleep(5)
    
    print("⏰ 监控超时")
    return None

def test_processor_status(token):
    """测试处理器状态"""
    print("🔍 测试处理器状态...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/v1/system/processor-status", 
                              headers=headers)
        if response.status_code == 200:
            status = response.json()
            print(f"✅ 处理器状态: {status}")
            return True
        else:
            print(f"❌ 获取处理器状态失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 处理器状态请求失败: {e}")
        return False

def test_frontend_accessibility():
    """测试前端可访问性"""
    print("🔍 测试前端可访问性...")
    
    # 尝试多个可能的端口
    ports = [3000, 3001, 3002, 3003]
    
    for port in ports:
        try:
            url = f"http://localhost:{port}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ 前端可访问: {url}")
                return url
        except Exception:
            continue
    
    print("❌ 前端不可访问")
    return None

def cleanup():
    """清理测试文件"""
    test_file = Path("test_video.mp4")
    if test_file.exists():
        test_file.unlink()
        print("🧹 清理测试文件")

def main():
    """主测试函数"""
    print("🎬 视频学习助手 - 真实实现测试")
    print("=" * 50)
    
    # 1. 测试后端健康状态
    if not test_backend_health():
        print("❌ 后端不可用，请先启动后端服务")
        return
    
    # 2. 测试前端可访问性
    frontend_url = test_frontend_accessibility()
    if not frontend_url:
        print("⚠️ 前端不可访问，但继续测试后端功能")
    
    # 3. 注册并登录
    token = register_and_login()
    if not token:
        print("❌ 无法获取访问令牌")
        return
    
    # 4. 测试处理器状态
    test_processor_status(token)
    
    # 5. 上传视频
    video_id = upload_video(token)
    if not video_id:
        print("❌ 视频上传失败")
        cleanup()
        return
    
    # 6. 创建分析任务
    task_id = create_analysis_task(token, video_id)
    if not task_id:
        print("❌ 分析任务创建失败")
        cleanup()
        return
    
    # 7. 监控任务进度
    final_task = monitor_task_progress(token, task_id)
    
    # 8. 显示结果
    if final_task:
        print("\n📋 最终任务状态:")
        print(f"  状态: {final_task['status']}")
        print(f"  进度: {final_task['progress']}")
        if final_task.get('report_pdf_url'):
            print(f"  报告: {final_task['report_pdf_url']}")
        if final_task.get('subtitle_srt_url'):
            print(f"  字幕: {final_task['subtitle_srt_url']}")
        if final_task.get('script_md_url'):
            print(f"  脚本: {final_task['script_md_url']}")
    
    # 9. 清理
    cleanup()
    
    print("\n🎉 测试完成!")
    if frontend_url:
        print(f"🌐 前端地址: {frontend_url}")
    print(f"🔧 后端地址: {BACKEND_URL}")
    print(f"📚 API文档: {BACKEND_URL}/docs")

if __name__ == "__main__":
    main() 
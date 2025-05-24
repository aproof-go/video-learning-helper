#!/usr/bin/env python3
"""
测试前端分析结果显示
"""
import requests
import json
import time

def test_frontend_analysis():
    """测试前端分析结果页面"""
    print("🎯 测试前端分析结果显示")
    print("=" * 50)
    
    # 1. 检查最近的分析任务
    print("1️⃣ 获取最近的分析任务...")
    try:
        # 登录获取token
        login_response = requests.post("http://localhost:8000/api/v1/auth/login", 
            json={"email": "frontend_test@example.com", "password": "test123456"})
        
        if login_response.status_code == 200:
            token = login_response.json()["access_token"]
            print(f"   ✅ 登录成功")
        else:
            print(f"   ❌ 登录失败: {login_response.text}")
            return False
        
        # 获取用户视频列表
        headers = {"Authorization": f"Bearer {token}"}
        videos_response = requests.get("http://localhost:8000/api/v1/videos", headers=headers)
        
        if videos_response.status_code == 200:
            videos = videos_response.json()
            if videos:
                latest_video = videos[0]  # 取最新的视频
                video_id = latest_video["id"]
                print(f"   ✅ 找到视频: {latest_video['filename']} (ID: {video_id})")
                
                # 获取分析任务
                tasks_response = requests.get(f"http://localhost:8000/api/v1/analysis/videos/{video_id}/tasks", 
                                           headers=headers)
                
                if tasks_response.status_code == 200:
                    tasks = tasks_response.json()
                    if tasks:
                        completed_tasks = [t for t in tasks if t["status"] == "completed"]
                        if completed_tasks:
                            task = completed_tasks[0]
                            task_id = task["id"]
                            print(f"   ✅ 找到完成的任务: {task_id}")
                            
                            # 检查JSON文件是否可访问
                            json_url = f"http://localhost:8000/uploads/{task_id}_results.json"
                            json_response = requests.get(json_url)
                            
                            if json_response.status_code == 200:
                                results = json_response.json()
                                print(f"   ✅ JSON文件可访问: {len(json.dumps(results))} 字符")
                                
                                # 显示分析结果摘要
                                print("\n📋 分析结果摘要:")
                                print(f"   📹 视频路径: {results.get('video_path', 'N/A')}")
                                print(f"   ⏱️ 分析时间: {results.get('analysis_time', 'N/A')}")
                                print(f"   🎬 场景数量: {len(results.get('segments', []))}")
                                print(f"   🔄 转场数量: {len(results.get('transitions', []))}")
                                
                                transcription = results.get('transcription', {})
                                print(f"   🎤 转录文本: {transcription.get('text', 'N/A')[:50]}...")
                                print(f"   📝 转录段数: {len(transcription.get('segments', []))}")
                                
                                video_info = results.get('video_info', {})
                                print(f"   📊 视频信息: {video_info.get('width', 0)}x{video_info.get('height', 0)}, {video_info.get('duration', 0)}s")
                                
                                # 前端页面URL
                                frontend_url = f"http://localhost:3000/analysis/{video_id}"
                                print(f"\n🌐 前端分析页面: {frontend_url}")
                                print("   请在浏览器中打开上述链接查看分析结果")
                                
                                return True
                            else:
                                print(f"   ❌ JSON文件无法访问: {json_response.status_code}")
                                return False
                        else:
                            print("   ⚠️ 没有找到完成的分析任务")
                            return False
                    else:
                        print("   ⚠️ 没有找到分析任务")
                        return False
                else:
                    print(f"   ❌ 获取分析任务失败: {tasks_response.status_code}")
                    return False
            else:
                print("   ⚠️ 没有找到视频")
                return False
        else:
            print(f"   ❌ 获取视频列表失败: {videos_response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ 测试失败: {e}")
        return False

def main():
    """主函数"""
    print("🔧 前端分析结果显示测试")
    print("=" * 60)
    
    # 检查服务状态
    print("🔍 检查服务状态...")
    try:
        # 检查后端
        backend_response = requests.get("http://localhost:8000/health", timeout=5)
        if backend_response.status_code == 200:
            print("   ✅ 后端服务正常")
        else:
            print("   ❌ 后端服务异常")
            return
        
        # 检查前端
        frontend_response = requests.get("http://localhost:3000", timeout=5)
        if frontend_response.status_code == 200:
            print("   ✅ 前端服务正常")
        else:
            print("   ❌ 前端服务异常")
            return
            
    except Exception as e:
        print(f"   ❌ 服务检查失败: {e}")
        return
    
    print()
    
    # 运行测试
    if test_frontend_analysis():
        print("\n🎉 测试完成! 请在浏览器中查看分析结果页面")
    else:
        print("\n❌ 测试失败")

if __name__ == "__main__":
    main() 
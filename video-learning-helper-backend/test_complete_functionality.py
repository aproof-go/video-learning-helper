#!/usr/bin/env python3
"""
完整功能验证脚本
测试所有核心功能包括逻辑删除、最新视频排序、下载功能等
"""

import requests
import json
import time
import os
from pathlib import Path

# API配置
BASE_URL = "http://localhost:8000"
TEST_EMAIL = "functional_test@example.com"
TEST_PASSWORD = "test123456"

class FunctionalTest:
    def __init__(self):
        self.token = None
        self.video_id = None
        self.task_id = None
        self.test_results = []
        
    def log_test(self, test_name, success, message="", expected="", actual=""):
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            "test": test_name,
            "status": status,
            "message": message,
            "expected": expected,
            "actual": actual
        })
        print(f"{status}: {test_name}")
        if message:
            print(f"    {message}")
        if not success and expected:
            print(f"    Expected: {expected}")
            print(f"    Actual: {actual}")
        print()

    def test_health_check(self):
        """测试健康检查"""
        try:
            response = requests.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    self.log_test("健康检查", True, f"版本: {data.get('version')}, 用户数: {data.get('user_count')}")
                    return True
                else:
                    self.log_test("健康检查", False, f"状态不健康: {data}")
                    return False
            else:
                self.log_test("健康检查", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("健康检查", False, f"请求异常: {e}")
            return False

    def test_user_registration_and_login(self):
        """测试用户注册和登录"""
        # 注册用户
        try:
            register_data = {
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD,
                "name": "功能测试用户"
            }
            response = requests.post(f"{BASE_URL}/api/v1/auth/register", json=register_data)
            
            if response.status_code in [201, 400]:  # 201创建成功或400已存在
                if response.status_code == 400 and "already registered" in response.text:
                    self.log_test("用户注册", True, "用户已存在，跳过注册")
                else:
                    self.log_test("用户注册", True, "注册成功")
            else:
                self.log_test("用户注册", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("用户注册", False, f"注册异常: {e}")
            return False

        # 登录
        try:
            login_data = {
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            }
            response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                if self.token:
                    self.log_test("用户登录", True, "获取到访问令牌")
                    return True
                else:
                    self.log_test("用户登录", False, "未获取到访问令牌")
                    return False
            else:
                self.log_test("用户登录", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("用户登录", False, f"登录异常: {e}")
            return False

    def test_video_upload(self):
        """测试视频上传"""
        try:
            # 创建测试视频文件
            test_file_content = b"fake video content for testing"
            test_file_path = Path("test_video_functional.mp4")
            with open(test_file_path, "wb") as f:
                f.write(test_file_content)
            
            # 上传视频
            files = {"file": ("test_video_functional.mp4", open(test_file_path, "rb"), "video/mp4")}
            data = {
                "title": "功能测试视频",
                "description": "用于功能验证的测试视频"
            }
            headers = {"Authorization": f"Bearer {self.token}"}
            
            response = requests.post(f"{BASE_URL}/api/v1/videos/upload", files=files, data=data, headers=headers)
            files["file"][1].close()  # 关闭文件
            
            if response.status_code == 200:
                result = response.json()
                self.video_id = result.get("video_id")
                if self.video_id:
                    self.log_test("视频上传", True, f"视频ID: {self.video_id}")
                    # 清理测试文件
                    test_file_path.unlink()
                    return True
                else:
                    self.log_test("视频上传", False, "未获取到视频ID")
                    return False
            else:
                self.log_test("视频上传", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("视频上传", False, f"上传异常: {e}")
            return False

    def test_video_list(self):
        """测试视频列表（检查最新排序）"""
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(f"{BASE_URL}/api/v1/videos/", headers=headers)
            
            if response.status_code == 200:
                videos = response.json()
                if isinstance(videos, list) and len(videos) > 0:
                    # 检查是否有刚上传的视频
                    found_video = any(v.get("id") == self.video_id for v in videos)
                    if found_video:
                        # 检查排序（最新的在前面）
                        if len(videos) > 1:
                            first_video_time = videos[0].get("created_at", "")
                            second_video_time = videos[1].get("created_at", "")
                            if first_video_time >= second_video_time:
                                self.log_test("视频列表", True, f"获取到{len(videos)}个视频，排序正确")
                            else:
                                self.log_test("视频列表", False, "视频排序不正确")
                        else:
                            self.log_test("视频列表", True, f"获取到{len(videos)}个视频")
                        return True
                    else:
                        self.log_test("视频列表", False, "未找到刚上传的视频")
                        return False
                else:
                    self.log_test("视频列表", False, "视频列表为空")
                    return False
            else:
                self.log_test("视频列表", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("视频列表", False, f"请求异常: {e}")
            return False

    def test_analysis_task_creation(self):
        """测试分析任务创建"""
        try:
            task_data = {
                "video_id": self.video_id,
                "video_segmentation": True,
                "transition_detection": True,
                "audio_transcription": True,
                "report_generation": True
            }
            headers = {"Authorization": f"Bearer {self.token}"}
            
            response = requests.post(f"{BASE_URL}/api/v1/analysis/tasks", json=task_data, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                self.task_id = result.get("id")
                if self.task_id:
                    self.log_test("分析任务创建", True, f"任务ID: {self.task_id}")
                    return True
                else:
                    self.log_test("分析任务创建", False, "未获取到任务ID")
                    return False
            else:
                self.log_test("分析任务创建", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("分析任务创建", False, f"创建异常: {e}")
            return False

    def test_task_processing(self):
        """测试任务处理（等待完成）"""
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            max_wait_time = 30  # 最大等待30秒
            wait_time = 0
            
            while wait_time < max_wait_time:
                response = requests.get(f"{BASE_URL}/api/v1/analysis/tasks/{self.task_id}", headers=headers)
                
                if response.status_code == 200:
                    task = response.json()
                    status = task.get("status")
                    progress = task.get("progress", "0")
                    
                    print(f"    任务状态: {status}, 进度: {progress}%")
                    
                    if status == "completed":
                        self.log_test("任务处理完成", True, f"任务在{wait_time}秒内完成")
                        return True
                    elif status == "failed":
                        error_msg = task.get("error_message", "未知错误")
                        self.log_test("任务处理完成", False, f"任务失败: {error_msg}")
                        return False
                    
                    time.sleep(2)
                    wait_time += 2
                else:
                    self.log_test("任务处理完成", False, f"查询任务状态失败: HTTP {response.status_code}")
                    return False
            
            self.log_test("任务处理完成", False, f"任务在{max_wait_time}秒内未完成")
            return False
        except Exception as e:
            self.log_test("任务处理完成", False, f"处理异常: {e}")
            return False

    def test_file_downloads(self):
        """测试文件下载"""
        try:
            # 首先获取任务详情
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(f"{BASE_URL}/api/v1/analysis/tasks/{self.task_id}", headers=headers)
            
            if response.status_code != 200:
                self.log_test("文件下载", False, "获取任务详情失败")
                return False
            
            task = response.json()
            report_url = task.get("report_pdf_url")
            subtitle_url = task.get("subtitle_srt_url")
            script_url = task.get("script_md_url")
            
            success_count = 0
            total_count = 0
            
            # 测试报告下载
            if report_url:
                total_count += 1
                download_url = f"{BASE_URL}{report_url}"
                download_response = requests.get(download_url)
                if download_response.status_code == 200:
                    if len(download_response.content) > 0:
                        success_count += 1
                        print(f"    ✅ 报告下载成功: {len(download_response.content)} bytes")
                    else:
                        print(f"    ❌ 报告文件为空")
                else:
                    print(f"    ❌ 报告下载失败: HTTP {download_response.status_code}")
            
            # 测试字幕下载
            if subtitle_url:
                total_count += 1
                download_url = f"{BASE_URL}{subtitle_url}"
                download_response = requests.get(download_url)
                if download_response.status_code == 200:
                    if len(download_response.content) > 0:
                        success_count += 1
                        print(f"    ✅ 字幕下载成功: {len(download_response.content)} bytes")
                    else:
                        print(f"    ❌ 字幕文件为空")
                else:
                    print(f"    ❌ 字幕下载失败: HTTP {download_response.status_code}")
            
            # 测试脚本下载
            if script_url:
                total_count += 1
                download_url = f"{BASE_URL}{script_url}"
                download_response = requests.get(download_url)
                if download_response.status_code == 200:
                    if len(download_response.content) > 0:
                        success_count += 1
                        print(f"    ✅ 脚本下载成功: {len(download_response.content)} bytes")
                    else:
                        print(f"    ❌ 脚本文件为空")
                else:
                    print(f"    ❌ 脚本下载失败: HTTP {download_response.status_code}")
            else:
                print(f"    ❓ 任务中没有脚本URL: script_md_url 字段不存在")
            
            if total_count == 0:
                self.log_test("文件下载", False, "没有可下载的文件")
                return False
            elif success_count == total_count:
                self.log_test("文件下载", True, f"所有{total_count}个文件下载成功")
                return True
            else:
                self.log_test("文件下载", False, f"{success_count}/{total_count}个文件下载成功")
                return False
                
        except Exception as e:
            self.log_test("文件下载", False, f"下载异常: {e}")
            return False

    def test_task_list(self):
        """测试任务列表"""
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(f"{BASE_URL}/api/v1/analysis/videos/{self.video_id}/tasks", headers=headers)
            
            if response.status_code == 200:
                tasks = response.json()
                if isinstance(tasks, list) and len(tasks) > 0:
                    found_task = any(t.get("id") == self.task_id for t in tasks)
                    if found_task:
                        self.log_test("任务列表", True, f"获取到{len(tasks)}个任务")
                        return True
                    else:
                        self.log_test("任务列表", False, "未找到创建的任务")
                        return False
                else:
                    self.log_test("任务列表", False, "任务列表为空")
                    return False
            else:
                self.log_test("任务列表", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("任务列表", False, f"请求异常: {e}")
            return False

    def test_processor_status(self):
        """测试处理器状态"""
        try:
            response = requests.get(f"{BASE_URL}/api/v1/system/processor-status")
            
            if response.status_code == 200:
                status = response.json()
                if "is_running" in status:
                    self.log_test("处理器状态", True, f"处理器运行状态: {status.get('is_running')}")
                    return True
                else:
                    self.log_test("处理器状态", False, "处理器状态格式不正确")
                    return False
            else:
                self.log_test("处理器状态", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("处理器状态", False, f"请求异常: {e}")
            return False

    def test_logical_delete(self):
        """测试逻辑删除功能"""
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            
            # 删除视频
            response = requests.delete(f"{BASE_URL}/api/v1/videos/{self.video_id}", headers=headers)
            
            if response.status_code == 200:
                # 验证视频列表中不再显示该视频
                list_response = requests.get(f"{BASE_URL}/api/v1/videos/", headers=headers)
                if list_response.status_code == 200:
                    videos = list_response.json()
                    found_video = any(v.get("id") == self.video_id for v in videos)
                    if not found_video:
                        self.log_test("逻辑删除", True, "视频已从列表中移除")
                        return True
                    else:
                        self.log_test("逻辑删除", False, "视频仍在列表中显示")
                        return False
                else:
                    self.log_test("逻辑删除", False, "验证删除后无法获取视频列表")
                    return False
            else:
                self.log_test("逻辑删除", False, f"删除失败: HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("逻辑删除", False, f"删除异常: {e}")
            return False

    def run_all_tests(self):
        """运行所有测试"""
        print("=" * 60)
        print("🚀 开始功能验证测试")
        print("=" * 60)
        print()
        
        # 按顺序执行测试
        tests = [
            self.test_health_check,
            self.test_user_registration_and_login,
            self.test_video_upload,
            self.test_video_list,
            self.test_analysis_task_creation,
            self.test_task_processing,
            self.test_file_downloads,
            self.test_task_list,
            self.test_processor_status,
            self.test_logical_delete
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            if test():
                passed += 1
            time.sleep(1)  # 测试间隔
        
        print("=" * 60)
        print("📊 测试结果汇总")
        print("=" * 60)
        
        for result in self.test_results:
            print(f"{result['status']}: {result['test']}")
        
        print()
        print(f"总计: {passed}/{total} 个测试通过")
        
        if passed == total:
            print("🎉 所有功能测试通过！")
        else:
            print(f"⚠️  {total - passed} 个测试失败，需要修复")
        
        return passed == total

if __name__ == "__main__":
    test = FunctionalTest()
    test.run_all_tests() 
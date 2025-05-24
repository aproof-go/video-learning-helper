#!/usr/bin/env python3
"""
Supabase数据库集成测试脚本
测试用户注册、登录和数据持久化功能
"""

import requests
import json
import time
from datetime import datetime

# API基础URL
BASE_URL = "http://localhost:8000"

def test_health_check():
    """测试健康检查"""
    print("🔍 测试健康检查...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
    
    assert response.status_code == 200
    assert data["status"] == "healthy"
    assert data["version"] == "2.0.0"
    assert data["database"] == "supabase"
    print("✅ 健康检查通过\n")
    return data

def test_user_registration():
    """测试用户注册"""
    print("🔍 测试用户注册...")
    
    # 测试数据
    test_users = [
        {
            "email": "supabase_admin@example.com",
            "password": "admin123456",
            "name": "Supabase管理员"
        },
        {
            "email": "supabase_editor@example.com", 
            "password": "editor123456",
            "name": "Supabase剪辑师"
        },
        {
            "email": "supabase_teacher@example.com",
            "password": "teacher123456",
            "name": "Supabase电影老师"
        }
    ]
    
    registered_users = []
    
    for user_data in test_users:
        print(f"注册用户: {user_data['email']}")
        response = requests.post(f"{BASE_URL}/api/v1/auth/register", json=user_data)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print(f"注册成功: {json.dumps(data, indent=2, ensure_ascii=False)}")
            registered_users.append({**user_data, "id": data["id"]})
        elif response.status_code == 400:
            print(f"用户已存在: {response.json()}")
            # 如果用户已存在，仍然添加到列表中用于后续测试
            registered_users.append(user_data)
        else:
            print(f"注册失败: {response.json()}")
        print()
    
    print(f"✅ 用户注册测试完成，共处理 {len(registered_users)} 个用户\n")
    return registered_users

def test_user_login(users):
    """测试用户登录"""
    print("🔍 测试用户登录...")
    
    login_results = []
    
    for user in users:
        print(f"登录用户: {user['email']}")
        login_data = {
            "email": user["email"],
            "password": user["password"]
        }
        
        response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=login_data)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"登录成功，获得token: {data['access_token'][:50]}...")
            login_results.append({
                **user,
                "token": data["access_token"]
            })
        else:
            print(f"登录失败: {response.json()}")
        print()
    
    print(f"✅ 用户登录测试完成，{len(login_results)} 个用户成功登录\n")
    return login_results

def test_authenticated_requests(logged_in_users):
    """测试需要认证的请求"""
    print("🔍 测试认证请求...")
    
    for user in logged_in_users:
        print(f"测试用户 {user['email']} 的认证请求")
        headers = {"Authorization": f"Bearer {user['token']}"}
        
        # 测试获取用户信息
        response = requests.get(f"{BASE_URL}/api/v1/auth/me", headers=headers)
        print(f"获取用户信息状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"用户信息: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"获取用户信息失败: {response.json()}")
        
        # 测试获取用户统计
        response = requests.get(f"{BASE_URL}/api/v1/users/stats", headers=headers)
        print(f"获取用户统计状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"用户统计: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"获取用户统计失败: {response.json()}")
        print()
    
    print("✅ 认证请求测试完成\n")

def test_data_persistence():
    """测试数据持久化"""
    print("🔍 测试数据持久化...")
    
    # 获取当前用户数量
    health_data = requests.get(f"{BASE_URL}/health").json()
    user_count = health_data["user_count"]
    print(f"当前数据库中用户数量: {user_count}")
    
    # 创建一个新用户来测试持久化
    timestamp = int(time.time())
    test_user = {
        "email": f"persistence_test_{timestamp}@example.com",
        "password": "test123456",
        "name": f"持久化测试用户_{timestamp}"
    }
    
    print(f"创建测试用户: {test_user['email']}")
    response = requests.post(f"{BASE_URL}/api/v1/auth/register", json=test_user)
    
    if response.status_code == 201:
        print("✅ 用户创建成功")
        
        # 再次检查用户数量
        health_data = requests.get(f"{BASE_URL}/health").json()
        new_user_count = health_data["user_count"]
        print(f"创建后用户数量: {new_user_count}")
        
        if new_user_count > user_count:
            print("✅ 数据持久化验证成功")
        else:
            print("❌ 数据持久化验证失败")
    else:
        print(f"❌ 用户创建失败: {response.json()}")
    
    print()

def test_error_handling():
    """测试错误处理"""
    print("🔍 测试错误处理...")
    
    # 测试重复注册
    duplicate_user = {
        "email": "supabase_admin@example.com",
        "password": "admin123456",
        "name": "重复用户"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/auth/register", json=duplicate_user)
    print(f"重复注册状态码: {response.status_code}")
    if response.status_code == 400:
        print("✅ 重复注册错误处理正确")
    else:
        print("❌ 重复注册错误处理异常")
    
    # 测试错误密码登录
    wrong_login = {
        "email": "supabase_admin@example.com",
        "password": "wrongpassword"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=wrong_login)
    print(f"错误密码登录状态码: {response.status_code}")
    if response.status_code == 401:
        print("✅ 错误密码处理正确")
    else:
        print("❌ 错误密码处理异常")
    
    # 测试无效token
    headers = {"Authorization": "Bearer invalid_token"}
    response = requests.get(f"{BASE_URL}/api/v1/auth/me", headers=headers)
    print(f"无效token状态码: {response.status_code}")
    if response.status_code == 401:
        print("✅ 无效token处理正确")
    else:
        print("❌ 无效token处理异常")
    
    print()

def main():
    """主测试函数"""
    print("🚀 开始Supabase数据库集成测试")
    print("=" * 50)
    
    try:
        # 1. 健康检查
        health_data = test_health_check()
        
        # 2. 用户注册
        registered_users = test_user_registration()
        
        # 3. 用户登录
        logged_in_users = test_user_login(registered_users)
        
        # 4. 认证请求
        if logged_in_users:
            test_authenticated_requests(logged_in_users)
        
        # 5. 数据持久化
        test_data_persistence()
        
        # 6. 错误处理
        test_error_handling()
        
        print("🎉 Supabase数据库集成测试完成！")
        print("=" * 50)
        
        # 最终统计
        final_health = requests.get(f"{BASE_URL}/health").json()
        print(f"最终用户数量: {final_health['user_count']}")
        print(f"数据库类型: {final_health['database']}")
        print(f"API版本: {final_health['version']}")
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 
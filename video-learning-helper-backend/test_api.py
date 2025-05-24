#!/usr/bin/env python3
"""
API测试脚本
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """测试健康检查"""
    print("=== 测试健康检查 ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    print()

def test_register():
    """测试用户注册"""
    print("=== 测试用户注册 ===")
    user_data = {
        "email": "test@example.com",
        "password": "testpassword123",
        "name": "测试用户"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/auth/register", json=user_data)
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    print()
    return response.status_code == 201

def test_login():
    """测试用户登录"""
    print("=== 测试用户登录 ===")
    login_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=login_data)
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        print(f"获取到token: {token[:50]}...")
        print()
        return token
    print()
    return None

def test_get_user_info(token):
    """测试获取用户信息"""
    print("=== 测试获取用户信息 ===")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/api/v1/auth/me", headers=headers)
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    print()

def test_duplicate_register():
    """测试重复注册"""
    print("=== 测试重复注册 ===")
    user_data = {
        "email": "test@example.com",
        "password": "testpassword123",
        "name": "测试用户2"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/auth/register", json=user_data)
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    print()

def test_wrong_login():
    """测试错误登录"""
    print("=== 测试错误登录 ===")
    login_data = {
        "email": "test@example.com",
        "password": "wrongpassword"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=login_data)
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    print()

def main():
    """主测试函数"""
    print("开始测试API接口...")
    print()
    
    # 测试健康检查
    test_health()
    
    # 测试用户注册
    if test_register():
        print("✅ 用户注册成功")
    else:
        print("❌ 用户注册失败")
        return
    
    # 测试用户登录
    token = test_login()
    if token:
        print("✅ 用户登录成功")
    else:
        print("❌ 用户登录失败")
        return
    
    # 测试获取用户信息
    test_get_user_info(token)
    print("✅ 获取用户信息成功")
    
    # 测试重复注册
    test_duplicate_register()
    print("✅ 重复注册测试完成")
    
    # 测试错误登录
    test_wrong_login()
    print("✅ 错误登录测试完成")
    
    print("所有测试完成！")

if __name__ == "__main__":
    main() 
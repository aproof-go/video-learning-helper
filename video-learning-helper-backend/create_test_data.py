#!/usr/bin/env python3
"""
创建测试数据脚本
"""
import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"

# 测试用户数据
test_users = [
    {
        "email": "admin@example.com",
        "password": "admin123456",
        "name": "管理员"
    },
    {
        "email": "editor1@example.com", 
        "password": "editor123456",
        "name": "剪辑师张三"
    },
    {
        "email": "editor2@example.com",
        "password": "editor123456", 
        "name": "剪辑师李四"
    },
    {
        "email": "teacher@example.com",
        "password": "teacher123456",
        "name": "电影老师王五"
    },
    {
        "email": "critic@example.com",
        "password": "critic123456",
        "name": "影评人赵六"
    },
    {
        "email": "student@example.com",
        "password": "student123456",
        "name": "学生小明"
    }
]

def check_health():
    """检查服务健康状态"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ 服务正常运行")
            return True
        else:
            print("❌ 服务异常")
            return False
    except Exception as e:
        print(f"❌ 无法连接到服务: {e}")
        return False

def register_user(user_data):
    """注册单个用户"""
    try:
        response = requests.post(f"{BASE_URL}/api/v1/auth/register", json=user_data)
        if response.status_code == 201:
            user_info = response.json()
            print(f"✅ 注册成功: {user_data['name']} ({user_data['email']})")
            return user_info
        elif response.status_code == 400:
            print(f"⚠️  用户已存在: {user_data['email']}")
            return None
        else:
            print(f"❌ 注册失败: {user_data['email']} - {response.json()}")
            return None
    except Exception as e:
        print(f"❌ 注册异常: {user_data['email']} - {e}")
        return None

def login_user(email, password):
    """用户登录"""
    try:
        login_data = {"email": email, "password": password}
        response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=login_data)
        if response.status_code == 200:
            token_info = response.json()
            print(f"✅ 登录成功: {email}")
            return token_info["access_token"]
        else:
            print(f"❌ 登录失败: {email} - {response.json()}")
            return None
    except Exception as e:
        print(f"❌ 登录异常: {email} - {e}")
        return None

def get_user_info(token):
    """获取用户信息"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/v1/auth/me", headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ 获取用户信息失败: {response.json()}")
            return None
    except Exception as e:
        print(f"❌ 获取用户信息异常: {e}")
        return None

def test_user_workflow(user_data):
    """测试完整的用户工作流"""
    print(f"\n=== 测试用户: {user_data['name']} ===")
    
    # 1. 注册
    user_info = register_user(user_data)
    
    # 2. 登录
    token = login_user(user_data["email"], user_data["password"])
    
    if token:
        # 3. 获取用户信息
        current_user = get_user_info(token)
        if current_user:
            print(f"📋 用户信息: ID={current_user['id'][:8]}..., 创建时间={current_user['created_at']}")
            return {
                "user_info": user_info or current_user,
                "token": token
            }
    
    return None

def main():
    """主函数"""
    print("🎬 Video Learning Helper - 测试数据创建工具")
    print("=" * 50)
    
    # 检查服务状态
    if not check_health():
        print("请先启动后端服务!")
        return
    
    print(f"\n开始创建 {len(test_users)} 个测试用户...")
    
    successful_users = []
    failed_users = []
    
    for i, user_data in enumerate(test_users, 1):
        print(f"\n[{i}/{len(test_users)}]", end="")
        result = test_user_workflow(user_data)
        
        if result:
            successful_users.append({
                "email": user_data["email"],
                "name": user_data["name"],
                "password": user_data["password"],
                "user_id": result["user_info"]["id"],
                "token": result["token"][:20] + "..."
            })
        else:
            failed_users.append({
                "email": user_data["email"],
                "name": user_data["name"]
            })
        
        # 避免请求过快
        time.sleep(0.5)
    
    # 输出统计结果
    print(f"\n" + "=" * 50)
    print("📊 测试数据创建完成!")
    print(f"✅ 成功: {len(successful_users)} 个用户")
    print(f"❌ 失败: {len(failed_users)} 个用户")
    
    if successful_users:
        print(f"\n✅ 成功创建的用户:")
        for user in successful_users:
            print(f"  • {user['name']} ({user['email']}) - ID: {user['user_id'][:8]}...")
    
    if failed_users:
        print(f"\n❌ 创建失败的用户:")
        for user in failed_users:
            print(f"  • {user['name']} ({user['email']})")
    
    # 验证登录功能
    print(f"\n🔐 验证登录功能...")
    login_tests = 0
    login_success = 0
    
    for user_data in test_users:
        login_tests += 1
        token = login_user(user_data["email"], user_data["password"])
        if token:
            login_success += 1
    
    print(f"登录测试: {login_success}/{login_tests} 成功")
    
    # 保存测试账号信息
    save_test_accounts()
    
    print(f"\n🎉 所有测试完成!")
    print(f"💡 可以使用以下测试账号:")
    print(f"   管理员: admin@example.com / admin123456")
    print(f"   剪辑师: editor1@example.com / editor123456")
    print(f"   老师: teacher@example.com / teacher123456")

def save_test_accounts():
    """保存测试账号信息到文件"""
    account_info = {
        "created_at": datetime.now().isoformat(),
        "api_base": BASE_URL,
        "test_accounts": test_users
    }
    
    with open("test_accounts.json", "w", encoding="utf-8") as f:
        json.dump(account_info, f, ensure_ascii=False, indent=2)
    
    print("📝 测试账号信息已保存到 test_accounts.json")

if __name__ == "__main__":
    main() 
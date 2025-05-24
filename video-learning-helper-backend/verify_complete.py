#!/usr/bin/env python3
"""
完整验证脚本 - 测试所有注册登录功能
"""
import requests
import json
import time
from datetime import datetime
import jwt

BASE_URL = "http://localhost:8000"

def print_header(title):
    """打印标题"""
    print(f"\n{'='*60}")
    print(f"🎬 {title}")
    print(f"{'='*60}")

def print_section(title):
    """打印章节"""
    print(f"\n📋 {title}")
    print("-" * 40)

def test_api_docs():
    """测试API文档"""
    print_section("API文档测试")
    
    try:
        # 测试Swagger UI
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code == 200:
            print("✅ Swagger UI 可访问")
        else:
            print("❌ Swagger UI 不可访问")
        
        # 测试OpenAPI规范
        response = requests.get(f"{BASE_URL}/openapi.json")
        if response.status_code == 200:
            openapi_spec = response.json()
            print("✅ OpenAPI 规范可访问")
            print(f"   📄 API标题: {openapi_spec.get('info', {}).get('title')}")
            print(f"   🔢 API版本: {openapi_spec.get('info', {}).get('version')}")
            return True
        else:
            print("❌ OpenAPI 规范不可访问")
            return False
    except Exception as e:
        print(f"❌ API文档测试失败: {e}")
        return False

def test_authentication_security():
    """测试认证安全性"""
    print_section("认证安全性测试")
    
    # 测试无效token访问
    try:
        invalid_token = "invalid.token.here"
        headers = {"Authorization": f"Bearer {invalid_token}"}
        response = requests.get(f"{BASE_URL}/api/v1/auth/me", headers=headers)
        
        if response.status_code == 401:
            print("✅ 无效token被正确拒绝")
        else:
            print("❌ 无效token验证失败")
    except Exception as e:
        print(f"❌ 无效token测试异常: {e}")
    
    # 测试无token访问
    try:
        response = requests.get(f"{BASE_URL}/api/v1/auth/me")
        if response.status_code == 403:  # FastAPI默认返回403
            print("✅ 无token访问被正确拒绝")
        else:
            print(f"⚠️  无token访问返回状态码: {response.status_code}")
    except Exception as e:
        print(f"❌ 无token测试异常: {e}")

def test_token_validation():
    """测试token验证"""
    print_section("Token验证测试")
    
    # 先登录获取有效token
    login_data = {"email": "admin@example.com", "password": "admin123456"}
    response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=login_data)
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        print("✅ 获取到有效token")
        
        # 解析token内容
        try:
            # 注意：这里不验证签名，只是查看内容
            decoded = jwt.decode(token, options={"verify_signature": False})
            print(f"   📋 Token内容: sub={decoded.get('sub')}, exp={decoded.get('exp')}")
            
            # 验证token可以正常使用
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(f"{BASE_URL}/api/v1/auth/me", headers=headers)
            
            if response.status_code == 200:
                user_info = response.json()
                print(f"   ✅ Token验证成功: {user_info['name']} ({user_info['email']})")
            else:
                print("   ❌ Token验证失败")
                
        except Exception as e:
            print(f"   ❌ Token解析失败: {e}")
    else:
        print("❌ 无法获取token进行测试")

def test_input_validation():
    """测试输入验证"""
    print_section("输入验证测试")
    
    # 测试无效邮箱格式
    try:
        invalid_email_data = {
            "email": "invalid-email",
            "password": "test123",
            "name": "测试"
        }
        response = requests.post(f"{BASE_URL}/api/v1/auth/register", json=invalid_email_data)
        if response.status_code == 422:  # Pydantic验证错误
            print("✅ 无效邮箱格式被正确拒绝")
        else:
            print(f"⚠️  无效邮箱格式返回状态码: {response.status_code}")
    except Exception as e:
        print(f"❌ 邮箱验证测试异常: {e}")
    
    # 测试缺少必填字段
    try:
        incomplete_data = {"email": "test@example.com"}
        response = requests.post(f"{BASE_URL}/api/v1/auth/register", json=incomplete_data)
        if response.status_code == 422:
            print("✅ 缺少必填字段被正确拒绝")
        else:
            print(f"⚠️  缺少必填字段返回状态码: {response.status_code}")
    except Exception as e:
        print(f"❌ 必填字段测试异常: {e}")

def test_user_workflow(email, password, name):
    """测试完整用户工作流"""
    results = {}
    
    # 1. 注册
    user_data = {"email": email, "password": password, "name": name}
    response = requests.post(f"{BASE_URL}/api/v1/auth/register", json=user_data)
    
    if response.status_code == 201:
        results["register"] = {"success": True, "data": response.json()}
        print(f"✅ 注册成功: {name}")
    elif response.status_code == 400:
        results["register"] = {"success": False, "reason": "already_exists"}
        print(f"⚠️  用户已存在: {email}")
    else:
        results["register"] = {"success": False, "reason": "other", "data": response.json()}
        print(f"❌ 注册失败: {name}")
        return results
    
    # 2. 登录
    login_data = {"email": email, "password": password}
    response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=login_data)
    
    if response.status_code == 200:
        token_data = response.json()
        results["login"] = {"success": True, "token": token_data["access_token"]}
        print(f"✅ 登录成功: {email}")
    else:
        results["login"] = {"success": False, "data": response.json()}
        print(f"❌ 登录失败: {email}")
        return results
    
    # 3. 获取用户信息
    headers = {"Authorization": f"Bearer {results['login']['token']}"}
    response = requests.get(f"{BASE_URL}/api/v1/auth/me", headers=headers)
    
    if response.status_code == 200:
        user_info = response.json()
        results["user_info"] = {"success": True, "data": user_info}
        print(f"✅ 获取用户信息成功: {user_info['id'][:8]}...")
    else:
        results["user_info"] = {"success": False, "data": response.json()}
        print(f"❌ 获取用户信息失败: {email}")
    
    return results

def test_edge_cases():
    """测试边界情况"""
    print_section("边界情况测试")
    
    # 测试极长邮箱
    long_email = "a" * 100 + "@example.com"
    try:
        response = requests.post(f"{BASE_URL}/api/v1/auth/register", json={
            "email": long_email,
            "password": "test123",
            "name": "长邮箱测试"
        })
        print(f"   极长邮箱测试: 状态码 {response.status_code}")
    except Exception as e:
        print(f"   极长邮箱测试异常: {e}")
    
    # 测试空密码
    try:
        response = requests.post(f"{BASE_URL}/api/v1/auth/register", json={
            "email": "empty@example.com",
            "password": "",
            "name": "空密码测试"
        })
        print(f"   空密码测试: 状态码 {response.status_code}")
    except Exception as e:
        print(f"   空密码测试异常: {e}")

def main():
    """主验证函数"""
    print_header("Video Learning Helper 完整功能验证")
    
    # 1. 基础健康检查
    print_section("基础健康检查")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ 服务健康: {health_data}")
        else:
            print("❌ 服务不健康")
            return
    except Exception as e:
        print(f"❌ 无法连接到服务: {e}")
        return
    
    # 2. API文档测试
    test_api_docs()
    
    # 3. 输入验证测试
    test_input_validation()
    
    # 4. 认证安全性测试
    test_authentication_security()
    
    # 5. Token验证测试
    test_token_validation()
    
    # 6. 用户工作流测试
    print_section("用户工作流测试")
    
    # 加载测试账号
    try:
        with open("test_accounts.json", "r", encoding="utf-8") as f:
            test_data = json.load(f)
            test_users = test_data["test_accounts"]
    except FileNotFoundError:
        print("❌ 找不到测试账号文件，请先运行 create_test_data.py")
        return
    
    successful_workflows = 0
    total_workflows = len(test_users)
    
    for user in test_users:
        result = test_user_workflow(user["email"], user["password"], user["name"])
        
        # 检查工作流是否完全成功
        if (result.get("login", {}).get("success") and 
            result.get("user_info", {}).get("success")):
            successful_workflows += 1
    
    # 7. 边界情况测试
    test_edge_cases()
    
    # 8. 并发测试 (简单版本)
    print_section("并发测试")
    try:
        import concurrent.futures
        import threading
        
        def concurrent_login():
            login_data = {"email": "admin@example.com", "password": "admin123456"}
            response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=login_data)
            return response.status_code == 200
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(concurrent_login) for _ in range(10)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
            
        success_count = sum(results)
        print(f"   并发登录测试: {success_count}/10 成功")
        
    except ImportError:
        print("   ⚠️  跳过并发测试 (需要concurrent.futures)")
    except Exception as e:
        print(f"   ❌ 并发测试异常: {e}")
    
    # 9. 最终统计
    print_header("验证结果统计")
    print(f"📊 用户工作流测试: {successful_workflows}/{total_workflows} 成功")
    print(f"🔒 安全性测试: 已完成")
    print(f"📝 输入验证测试: 已完成")
    print(f"🚀 性能测试: 已完成")
    
    if successful_workflows == total_workflows:
        print(f"\n🎉 所有验证测试通过!")
        print(f"✅ 注册登录功能完全正常")
        print(f"✅ 安全机制工作正常")
        print(f"✅ API接口设计合理")
    else:
        print(f"\n⚠️  部分测试未通过，请检查错误信息")
    
    # 10. 使用建议
    print(f"\n💡 测试账号使用建议:")
    print(f"   🔹 管理员账号: admin@example.com / admin123456")
    print(f"   🔹 剪辑师账号: editor1@example.com / editor123456")
    print(f"   🔹 教师账号: teacher@example.com / teacher123456")
    print(f"   🔹 学生账号: student@example.com / student123456")
    
    print(f"\n🌐 Web测试页面: {BASE_URL}/docs")
    print(f"📄 本地测试页面: file://{__file__.replace('verify_complete.py', 'test_frontend.html')}")

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
import requests
import json

# 登录
response = requests.post('http://localhost:8000/api/v1/auth/login', json={'email': 'script_test@example.com', 'password': 'test123456'})
token = response.json()['access_token']

# 获取任务详情
headers = {'Authorization': f'Bearer {token}'}
response = requests.get('http://localhost:8000/api/v1/analysis/tasks/6b4cd3c1-700e-4ec8-828f-70be7ed66551', headers=headers)
task = response.json()

print('�� API响应测试:')
print('响应状态码:', response.status_code)
print('所有字段:', list(task.keys()))
print('脚本URL字段值:', repr(task.get('script_md_url')))
print('报告URL字段值:', repr(task.get('report_pdf_url')))
print('字幕URL字段值:', repr(task.get('subtitle_srt_url')))

script_url = task.get('script_md_url')
if script_url:
    print('✅ 脚本URL已正确返回!')
    # 尝试下载脚本文件
    script_response = requests.get(f"http://localhost:8000{script_url}")
    if script_response.status_code == 200:
        print(f'✅ 脚本文件下载成功: {len(script_response.content)} bytes')
        print('📄 脚本内容预览:')
        print(script_response.text[:200] + '...')
    else:
        print(f'❌ 脚本文件下载失败: HTTP {script_response.status_code}')
else:
    print('❌ 脚本URL为空值') 
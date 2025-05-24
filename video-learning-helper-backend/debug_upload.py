#!/usr/bin/env python3
"""Debug upload API response"""

import requests
import json

# 登录
login_data = {'email': 'script_test@example.com', 'password': 'test123456'}
response = requests.post('http://localhost:8000/api/v1/auth/login', json=login_data)
token = response.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

# 测试上传
files = {'file': ('test.mp4', b'test video content', 'video/mp4')}
data = {'title': 'Script Test Video'}
response = requests.post('http://localhost:8000/api/v1/videos/upload', files=files, data=data, headers=headers)
print('Upload response status:', response.status_code)
print('Upload response:', json.dumps(response.json(), indent=2, ensure_ascii=False)) 
#!/usr/bin/env python3
import json
import sys

with open('uploads/2ac0c816-b62e-4933-b080-f11def66134d_results.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

transcription = data.get('transcription', {})
print('转录结果包含的字段:', list(transcription.keys()))

if 'script_file' in transcription:
    print('✅ 脚本文件字段存在:', transcription['script_file'])
else:
    print('❌ 脚本文件字段不存在')

# 显示完整的转录结果
print('\n完整转录结果:')
print(json.dumps(transcription, ensure_ascii=False, indent=2)) 
#!/usr/bin/env python3
import json

with open('video-learning-helper-backend/uploads/75e7c02d-144f-4be3-beb1-e8b643c60e78_results.json') as f:
    data = json.load(f)
    
print('🔍 结果文件详细分析:')
print('=' * 50)
print('视频路径:', data.get('video_path', 'N/A'))
print('分析时间:', data.get('analysis_time', 'N/A'))
print('片段生成器:', data.get('generator', 'N/A'))

segments = data.get('segments', [])
print(f'\n📊 片段分析 ({len(segments)} 个):')
print('片段类型分布:', {s['scene_type'] for s in segments})
print('片段总数:', len(segments))
print('前10个片段时长:', [s['duration'] for s in segments][:10])

if segments:
    scene_types = {}
    for s in segments:
        scene_type = s.get('scene_type', '未知')
        scene_types[scene_type] = scene_types.get(scene_type, 0) + 1
    
    print('\n场景类型统计:')
    for scene_type, count in scene_types.items():
        print(f'  {scene_type}: {count} 个')

print('\n🎞️ 转场分析:')
transitions = data.get('transitions', [])
print('转场总数:', len(transitions))
if transitions:
    print('前3个转场:', [(t['timestamp'], t['strength'], t['type']) for t in transitions[:3]])

print('\n🎙️ 转录分析:')
transcription = data.get('transcription', {})
if transcription:
    print('转录文本长度:', len(transcription.get('text', '')))
    print('转录片段数:', len(transcription.get('segments', [])))
else:
    print('无转录数据') 
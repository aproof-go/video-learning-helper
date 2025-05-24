#!/usr/bin/env python3
"""
查找真正的AI智能分析结果
"""

import json
import os

def find_ai_results():
    uploads_dir = 'video-learning-helper-backend/uploads/'
    ai_results = []

    for filename in os.listdir(uploads_dir):
        if filename.endswith('_results.json'):
            try:
                with open(os.path.join(uploads_dir, filename)) as f:
                    data = json.load(f)
                    segments = data.get('segments', [])
                    if segments:
                        durations = [s['duration'] for s in segments]
                        avg_dur = sum(durations) / len(durations)
                        min_dur = min(durations)
                        max_dur = max(durations)
                        is_fixed_30 = all(abs(d - 30.0) < 0.1 for d in durations)
                        
                        task_id = filename.replace('_results.json', '')
                        
                        result_info = {
                            'task_id': task_id,
                            'segments': len(segments),
                            'avg_duration': avg_dur,
                            'min_duration': min_dur,
                            'max_duration': max_dur,
                            'transitions': len(data.get('transitions', [])),
                            'filename': filename,
                            'is_ai': not is_fixed_30
                        }
                        
                        ai_results.append(result_info)
            except Exception as e:
                print(f"处理文件 {filename} 时出错: {e}")

    # 按是否为AI结果排序
    ai_results.sort(key=lambda x: (x['is_ai'], x['avg_duration']), reverse=True)

    print('📊 所有分析结果对比:')
    print('=' * 80)
    
    for result in ai_results:
        status = "🧠 AI智能分割" if result['is_ai'] else "⚠️  固定分割"
        print(f'{status} - 任务ID: {result["task_id"][:8]}...')
        print(f'  片段数: {result["segments"]:>3} | 平均: {result["avg_duration"]:>5.1f}s | 最短: {result["min_duration"]:>5.1f}s | 最长: {result["max_duration"]:>5.1f}s | 转场: {result["transitions"]:>3}')
        print()
    
    # 找出最好的AI结果
    ai_only = [r for r in ai_results if r['is_ai']]
    if ai_only:
        best_ai = ai_only[0]
        print(f'🎯 最佳AI分析结果: {best_ai["task_id"]}')
        print(f'   文件路径: video-learning-helper-backend/uploads/{best_ai["filename"]}')
        return best_ai["task_id"]
    else:
        print('❌ 没有找到AI智能分析结果')
        return None

if __name__ == "__main__":
    find_ai_results() 
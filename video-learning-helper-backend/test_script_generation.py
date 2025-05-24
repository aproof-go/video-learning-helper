#!/usr/bin/env python3
"""测试脚本生成功能"""

from app.video_analyzer_simple import VideoAnalyzer
from pathlib import Path
import json

def test_script_generation():
    # 创建测试视频文件
    test_video = Path('uploads/test_new_script.mp4')
    test_video.write_text('test video content')

    # 创建分析器
    analyzer = VideoAnalyzer()

    # 运行完整分析
    task_config = {
        'video_segmentation': True,
        'transition_detection': True,
        'audio_transcription': True,
        'report_generation': True
    }

    result = analyzer.analyze_video(str(test_video), task_config, task_id='test_new_script_456')
    print('分析结果:')
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))

    # 检查生成的文件
    transcription = result.get('transcription', {})
    script_file = transcription.get('script_file', '')
    
    print(f"\n转录结果包含的字段: {list(transcription.keys())}")
    
    if script_file and Path(script_file).exists():
        print(f'✅ 脚本文件已生成: {script_file}')
        print(f'文件大小: {Path(script_file).stat().st_size} bytes')
        
        # 显示文件内容的前几行
        with open(script_file, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f'文件内容预览:\n{content[:300]}...')
    else:
        print('❌ 脚本文件未生成')
        print(f'script_file 值: {script_file}')

if __name__ == "__main__":
    test_script_generation() 
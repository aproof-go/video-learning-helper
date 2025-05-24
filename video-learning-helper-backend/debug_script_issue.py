#!/usr/bin/env python3
"""调试脚本生成问题"""

from app.video_analyzer_simple import VideoAnalyzer
from pathlib import Path
import json

def debug_script_generation():
    print("🔧 开始调试脚本生成问题")
    
    # 创建测试视频文件
    test_video = Path('uploads/debug_test.mp4')
    test_video.write_text('test video content')
    print(f"📝 创建测试视频文件: {test_video}")

    # 创建分析器
    analyzer = VideoAnalyzer()
    
    # 运行音频转录
    print("🎤 开始音频转录...")
    transcription = analyzer._simulate_audio_transcription(test_video, task_id='debug_test_123')
    
    print("📋 转录结果:")
    print(json.dumps(transcription, ensure_ascii=False, indent=2, default=str))
    
    # 检查是否包含script_file字段
    if "script_file" in transcription:
        script_file_path = Path(transcription["script_file"])
        if script_file_path.exists():
            print(f"✅ 脚本文件已生成: {script_file_path}")
            print(f"📊 文件大小: {script_file_path.stat().st_size} bytes")
            
            # 检查内容
            with open(script_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"📄 脚本内容 (前200字符):")
                print(content[:200])
        else:
            print(f"❌ 脚本文件路径存在但文件不存在: {script_file_path}")
    else:
        print("❌ 转录结果中没有script_file字段")
    
    # 运行完整分析来对比
    print("\n🔄 运行完整分析进行对比...")
    task_config = {
        'video_segmentation': True,
        'transition_detection': True,
        'audio_transcription': True,
        'report_generation': True
    }
    
    results = analyzer.analyze_video(str(test_video), task_config, task_id='debug_test_456')
    
    print("📋 完整分析结果中的转录:")
    transcription_full = results.get('transcription', {})
    print(json.dumps(transcription_full, ensure_ascii=False, indent=2, default=str))
    
    if "script_file" in transcription_full:
        print("✅ 完整分析中包含script_file字段")
    else:
        print("❌ 完整分析中不包含script_file字段")
    
    # 检查uploads目录中的文件
    print("\n📁 检查uploads目录中的相关文件:")
    uploads_dir = Path('uploads')
    for pattern in ['*debug_test*', '*script*']:
        files = list(uploads_dir.glob(pattern))
        if files:
            print(f"  {pattern}: {[f.name for f in files]}")
        else:
            print(f"  {pattern}: 无匹配文件")

if __name__ == "__main__":
    debug_script_generation() 
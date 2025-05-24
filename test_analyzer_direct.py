#!/usr/bin/env python3
import sys
sys.path.insert(0, 'video-learning-helper-backend')

from app.video_analyzer import VideoAnalyzer
from pathlib import Path
import json

print('🧪 直接测试增强的VideoAnalyzer...')

# 创建分析器实例
analyzer = VideoAnalyzer()

# 使用指定的测试视频文件
video_path = Path('video-learning-helper-backend/uploads/03ebf0e0-3e0b-464c-9783-a054061578a0.mp4')

if not video_path.exists():
    print(f'❌ 测试视频文件不存在: {video_path}')
    exit(1)
print(f'🎬 测试视频: {video_path.name}')

# 测试配置
task_config = {
    "video_segmentation": True,
    "transition_detection": True,
    "audio_transcription": True,  # 如果有音频
    "report_generation": True
}

test_task_id = "test_enhanced_20241225"

def progress_callback(progress, message):
    print(f"   进度: {progress}% - {message}")

try:
    print('🚀 开始增强分析...')
    results = analyzer.analyze_video(
        str(video_path), 
        task_config, 
        progress_callback,
        test_task_id
    )
    
    print('✅ 分析完成！')
    
    # 检查结果
    segments = results.get("segments", [])
    transitions = results.get("transitions", [])
    transcription = results.get("transcription", {})
    
    print(f'\n📊 分析结果统计:')
    print(f'   📁 视频分段: {len(segments)} 个')
    print(f'   🎞️  转场检测: {len(transitions)} 个')
    print(f'   🎤 音频转录: {"✅" if transcription.get("text") else "❌"}')
    print(f'   🔗 路径匹配: {"✅" if test_task_id in results.get("video_path", "") else "❌"}')
    
    # 检查增强功能
    print(f'\n🔍 增强功能检查:')
    
    detailed_segments = 0
    segments_with_thumbnails = 0
    segments_with_gifs = 0
    segments_with_text = 0
    
    for segment in segments:
        # 检查详细分析字段
        if all(key in segment for key in ['composition_analysis', 'camera_movement', 'theme_analysis', 'critical_review']):
            detailed_segments += 1
        
        # 检查媒体文件
        if segment.get('thumbnail_url'):
            segments_with_thumbnails += 1
        if segment.get('gif_url'):
            segments_with_gifs += 1
        if segment.get('transcript_text'):
            segments_with_text += 1
    
    print(f'   🎨 详细分析覆盖: {detailed_segments}/{len(segments)} 个片段')
    print(f'   🖼️  缩略图生成: {segments_with_thumbnails}/{len(segments)} 个')
    print(f'   🎥 GIF动画生成: {segments_with_gifs}/{len(segments)} 个')
    print(f'   📝 转录文本分配: {segments_with_text}/{len(segments)} 个片段')
    
    # 检查生成的文件
    uploads_dir = Path('video-learning-helper-backend/uploads')
    
    results_file = uploads_dir / f"{test_task_id}_results.json"
    script_file = uploads_dir / f"{test_task_id}_script.md"
    report_file = uploads_dir / f"{test_task_id}_report.pdf"
    
    print(f'\n📁 生成文件检查:')
    print(f'   📄 结果文件: {"✅" if results_file.exists() else "❌"} ({results_file})')
    print(f'   📋 脚本文件: {"✅" if script_file.exists() else "❌"} ({script_file})')
    print(f'   📖 PDF报告: {"✅" if report_file.exists() else "❌"} ({report_file})')
    
    # 保存结果文件
    if not results_file.exists():
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2, default=str)
        print(f'   💾 结果文件已保存: {results_file}')
    
    # 检查脚本内容
    if script_file.exists():
        with open(script_file, 'r', encoding='utf-8') as f:
            script_content = f.read()
        
        has_detailed_analysis = "## 分段详细分析" in script_content
        has_overall_summary = "## 总体评价" in script_content
        
        print(f'   📖 脚本内容检查:')
        print(f'     - 包含详细分析: {"✅" if has_detailed_analysis else "❌"}')
        print(f'     - 包含总体评价: {"✅" if has_overall_summary else "❌"}')
        print(f'     - 文件大小: {len(script_content)} 字符')
    
    # 显示示例详细分析
    if detailed_segments > 0:
        print(f'\n🎬 示例详细分析:')
        sample_segment = next(s for s in segments if 'composition_analysis' in s)
        print(f'   片段 {sample_segment["segment_id"]} ({sample_segment["start_time"]:.1f}s-{sample_segment["end_time"]:.1f}s)')
        print(f'   🎨 构图: {sample_segment.get("composition_analysis", "无")[:60]}...')
        print(f'   🎥 运镜: {sample_segment.get("camera_movement", "无")[:60]}...')
        print(f'   🎯 主题: {sample_segment.get("theme_analysis", "无")[:60]}...')
        print(f'   💬 简评: {sample_segment.get("critical_review", "无")[:60]}...')
    
    # 质量评分
    total_score = 0
    max_score = 100
    
    # 基础功能 (30分)
    if len(segments) > 0:
        total_score += 30
    
    # 详细分析 (25分)
    if detailed_segments > 0:
        total_score += int((detailed_segments / len(segments)) * 25)
    
    # 媒体生成 (20分)
    if segments_with_gifs > 0:
        total_score += int((segments_with_gifs / len(segments)) * 20)
    
    # 脚本生成 (15分)
    if script_file.exists():
        total_score += 15
    
    # 路径匹配 (10分)
    if test_task_id in results.get("video_path", ""):
        total_score += 10
    
    print(f'\n📈 总体质量评分: {total_score}/{max_score}')
    
    if total_score >= 90:
        print('🎉 优秀！所有功能运行完美')
    elif total_score >= 75:
        print('👍 良好！大部分功能正常工作')
    elif total_score >= 60:
        print('⚠️ 一般，部分功能需要优化')
    else:
        print('❌ 需要改进，多项功能存在问题')
    
    print(f'\n🔗 可通过以下URL访问结果文件:')
    print(f'   📄 结果JSON: http://localhost:8000/uploads/{test_task_id}_results.json')
    print(f'   📋 脚本文件: http://localhost:8000/uploads/{test_task_id}_script.md')
    print(f'   📖 PDF报告: http://localhost:8000/uploads/{test_task_id}_report.pdf')

except Exception as e:
    print(f'❌ 分析失败: {e}')
    import traceback
    traceback.print_exc() 
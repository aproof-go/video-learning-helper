#!/usr/bin/env python3
import sys
sys.path.insert(0, 'video-learning-helper-backend')

from app.video_analyzer import VideoAnalyzer
from pathlib import Path
import json

print('🔧 测试增强的AI分析器...')

# 创建分析器实例
analyzer = VideoAnalyzer()

# 测试视频文件
video_file = Path('video-learning-helper-backend/uploads/fc1d7978-5abc-49a4-9efe-1d173637087c.mp4')

if not video_file.exists():
    print(f'❌ 视频文件不存在: {video_file}')
    print('请确保有一个可用的测试视频文件')
    exit(1)

# 配置测试任务
task_config = {
    "video_segmentation": True,
    "transition_detection": True,
    "audio_transcription": False,  # 暂时跳过音频转录以加快测试
    "report_generation": False     # 暂时跳过报告生成以加快测试
}

test_task_id = "test_enhanced_analyzer_123"

def progress_callback(progress, message):
    print(f"进度: {progress}% - {message}")

try:
    print(f'🎬 分析视频文件: {video_file}')
    results = analyzer.analyze_video(
        str(video_file), 
        task_config, 
        progress_callback, 
        test_task_id
    )
    
    print('\n✅ 分析完成!')
    
    # 检查分段结果
    segments = results.get('segments', [])
    print(f'\n📊 分段分析结果:')
    print(f'   总分段数: {len(segments)}')
    
    # 检查前5个分段的详细信息
    for i, segment in enumerate(segments[:5]):
        print(f'\n   分段 {segment["segment_id"]}:')
        print(f'     时长: {segment["duration"]:.2f}s')
        print(f'     场景类型: {segment["scene_type"]}')
        print(f'     缩略图: {segment.get("thumbnail_url", "❌ 无")}')
        print(f'     GIF: {segment.get("gif_url", "❌ 无")}')
        
        # 检查文件是否存在
        if segment.get('thumbnail_url'):
            thumbnail_file = Path(f'video-learning-helper-backend{segment["thumbnail_url"]}')
            print(f'     缩略图文件存在: {"✅" if thumbnail_file.exists() else "❌"} {thumbnail_file.name}')
        
        if segment.get('gif_url'):
            gif_file = Path(f'video-learning-helper-backend{segment["gif_url"]}')
            print(f'     GIF文件存在: {"✅" if gif_file.exists() else "❌"} {gif_file.name}')
    
    if len(segments) > 5:
        print(f'   ... 还有 {len(segments) - 5} 个分段')
    
    # 检查转场结果
    transitions = results.get('transitions', [])
    print(f'\n🎞️  转场检测结果:')
    print(f'   总转场数: {len(transitions)}')
    
    for i, transition in enumerate(transitions[:10]):
        print(f'   转场 {transition["transition_id"]}: {transition["timestamp"]:.2f}s, 强度: {transition["strength"]:.3f}, 类型: {transition["type"]}')
    
    if len(transitions) > 10:
        print(f'   ... 还有 {len(transitions) - 10} 个转场')
    
    # 保存测试结果
    results_file = Path(f'video-learning-helper-backend/uploads/{test_task_id}_results.json')
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    
    print(f'\n💾 测试结果已保存: {results_file}')
    
    # 统计缩略图和GIF文件
    uploads_dir = Path('video-learning-helper-backend/uploads')
    thumbnail_files = list(uploads_dir.glob(f'{test_task_id}_segment_*_thumbnail.jpg'))
    gif_files = list(uploads_dir.glob(f'{test_task_id}_segment_*.gif'))
    
    print(f'\n📁 生成的文件:')
    print(f'   缩略图文件: {len(thumbnail_files)} 个')
    print(f'   GIF文件: {len(gif_files)} 个')
    
    # 计算质量分数
    total_segments = len(segments)
    segments_with_thumbnails = sum(1 for s in segments if s.get('thumbnail_url'))
    segments_with_gifs = sum(1 for s in segments if s.get('gif_url'))
    
    quality_score = 0
    if total_segments > 0:
        # 基础分数：有分段
        quality_score += 40
        
        # 转场检测分数
        expected_transitions = max(total_segments // 3, 5)  # 预期转场数
        transition_score = min(len(transitions) / expected_transitions, 1.0) * 30
        quality_score += transition_score
        
        # 缩略图分数
        thumbnail_score = (segments_with_thumbnails / total_segments) * 15
        quality_score += thumbnail_score
        
        # GIF分数
        gif_score = (segments_with_gifs / total_segments) * 15
        quality_score += gif_score
    
    print(f'\n📈 数据质量评估:')
    print(f'   总体质量分数: {quality_score:.1f}%')
    print(f'   分段完整性: {len(segments) > 0}')
    print(f'   转场检测率: {len(transitions)}/{expected_transitions} (期望)')
    print(f'   缩略图覆盖率: {segments_with_thumbnails}/{total_segments} ({segments_with_thumbnails/total_segments*100:.1f}%)')
    print(f'   GIF覆盖率: {segments_with_gifs}/{total_segments} ({segments_with_gifs/total_segments*100:.1f}%)')
    
    if quality_score >= 90:
        print('🎉 优秀！数据质量很高')
    elif quality_score >= 75:
        print('👍 良好！数据质量可接受')
    else:
        print('⚠️  需要改进数据质量')

except Exception as e:
    print(f'❌ 测试失败: {e}')
    import traceback
    traceback.print_exc() 
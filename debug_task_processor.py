#!/usr/bin/env python3
"""
调试任务处理器和视频分析器集成
"""
import sys
import os
sys.path.append('video-learning-helper-backend')
import asyncio
from pathlib import Path

def test_task_processor_integration():
    print("🔧 调试任务处理器集成")
    print("=" * 50)
    
    from app.video_analyzer_simple import VideoAnalyzer
    
    # 使用实际上传的视频文件
    video_path = "video-learning-helper-backend/uploads/ebcdf5dc-fe9a-495c-b1d9-920e9765e8b3.mp4"
    task_id = "fdaaad07-cfb3-4f51-8114-f39bbc3b5d7b"
    
    if not Path(video_path).exists():
        print(f"❌ 视频文件不存在: {video_path}")
        return
    
    print(f"📹 视频文件: {video_path}")
    print(f"🆔 任务ID: {task_id}")
    
    # 创建分析器
    analyzer = VideoAnalyzer()
    
    # 任务配置（模拟任务处理器的配置）
    task_config = {
        "video_segmentation": True,
        "transition_detection": False,
        "audio_transcription": False,
        "report_generation": False
    }
    
    def progress_callback(progress, message):
        print(f"进度: {progress}% - {message}")
    
    try:
        print("🔍 模拟任务处理器调用...")
        print(f"   调用参数: video_path={video_path}, task_config={task_config}, task_id={task_id}")
        
        results = analyzer.analyze_video(video_path, task_config, progress_callback, task_id)
        
        print("\n📊 分析结果:")
        segments = results.get('segments', [])
        print(f"   片段数: {len(segments)}")
        
        # 检查前几个片段
        for i, segment in enumerate(segments[:3]):
            print(f"\n   片段 {segment['segment_id']}:")
            print(f"     时间: {segment['start_time']:.1f}s - {segment['end_time']:.1f}s")
            print(f"     场景类型: {segment['scene_type']}")
            print(f"     缩略图: {segment.get('thumbnail_url', '❌ 无')}")
            print(f"     GIF: {segment.get('gif_url', '❌ 无')}")
        
        # 检查生成的文件
        print(f"\n📁 检查生成的文件:")
        uploads_dir = Path("video-learning-helper-backend/uploads")
        thumbnail_files = list(uploads_dir.glob(f"{task_id}_segment_*_thumbnail.jpg"))
        gif_files = list(uploads_dir.glob(f"{task_id}_segment_*.gif"))
        
        print(f"   缩略图文件: {len(thumbnail_files)} 个")
        for f in thumbnail_files:
            print(f"     - {f.name}")
        
        print(f"   GIF文件: {len(gif_files)} 个")
        for f in gif_files:
            print(f"     - {f.name}")
        
        print(f"\n✅ 测试完成")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_task_processor_integration() 
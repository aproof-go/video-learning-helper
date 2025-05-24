#!/usr/bin/env python3
"""
测试缩略图和GIF生成功能
"""
import sys
import os
sys.path.append('video-learning-helper-backend')

from app.video_analyzer_simple import VideoAnalyzer
from pathlib import Path

def test_thumbnail_gif():
    print("🎬 测试缩略图和GIF生成功能")
    print("=" * 50)
    
    # 使用我们上传的视频文件
    video_path = Path('video-learning-helper-backend/uploads/ebcdf5dc-fe9a-495c-b1d9-920e9765e8b3.mp4')
    if not video_path.exists():
        print(f"❌ 视频文件不存在: {video_path}")
        return
    
    print(f"📹 视频文件: {video_path}")
    
    # 创建分析器
    analyzer = VideoAnalyzer()
    
    # 测试配置
    task_config = {
        "video_segmentation": True,
        "transition_detection": False,
        "audio_transcription": False,
        "report_generation": False
    }
    
    task_id = "test_thumbnail_gif_123"
    
    def progress_callback(progress, message):
        print(f"进度: {progress}% - {message}")
    
    try:
        print("🔍 开始分析...")
        results = analyzer.analyze_video(str(video_path), task_config, progress_callback, task_id)
        
        print("\n📊 分析结果:")
        segments = results.get('segments', [])
        print(f"   片段数: {len(segments)}")
        
        # 检查每个片段是否有缩略图和GIF
        for segment in segments:
            print(f"\n   片段 {segment['segment_id']}:")
            print(f"     时间: {segment['start_time']:.1f}s - {segment['end_time']:.1f}s")
            print(f"     场景类型: {segment['scene_type']}")
            print(f"     缩略图: {segment.get('thumbnail_url', '❌ 无')}")
            print(f"     GIF: {segment.get('gif_url', '❌ 无')}")
            
            # 检查文件是否真的存在
            if segment.get('thumbnail_url'):
                thumbnail_file = Path(f"video-learning-helper-backend{segment['thumbnail_url']}")
                print(f"     缩略图文件存在: {'✅' if thumbnail_file.exists() else '❌'} {thumbnail_file}")
            
            if segment.get('gif_url'):
                gif_file = Path(f"video-learning-helper-backend{segment['gif_url']}")
                print(f"     GIF文件存在: {'✅' if gif_file.exists() else '❌'} {gif_file}")
        
        print(f"\n✅ 测试完成")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_thumbnail_gif() 
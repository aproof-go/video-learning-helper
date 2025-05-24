#!/usr/bin/env python3
"""
测试智能视频分割功能
"""

import sys
import os
from pathlib import Path

# 添加backend路径
backend_path = Path(__file__).parent / "video-learning-helper-backend" / "app"
sys.path.append(str(backend_path))

from video_analyzer_simple import VideoAnalyzer

def test_smart_segmentation():
    """测试智能视频分割"""
    print("🧪 测试智能视频分割功能...")
    
    # 测试视频路径
    video_path = "/Users/apulu/Desktop/learning/写给自卑的自己的一封信 - 001 - 写给自卑的自己的一封信.mp4"
    
    if not Path(video_path).exists():
        print(f"❌ 测试视频不存在: {video_path}")
        return
    
    # 创建分析器
    analyzer = VideoAnalyzer()
    
    # 测试任务ID
    task_id = "smart_test_001"
    
    print(f"📹 分析视频: {Path(video_path).name}")
    
    try:
        # 只测试视频分割功能
        task_config = {
            "video_segmentation": True,
            "transition_detection": False,
            "audio_transcription": False,
            "report_generation": False
        }
        
        results = analyzer.analyze_video(
            video_path=video_path,
            task_config=task_config,
            task_id=task_id
        )
        
        # 分析结果
        segments = results.get("segments", [])
        video_info = results.get("video_info", {})
        
        print("\n📊 分析结果:")
        print(f"视频时长: {video_info.get('duration', 0):.1f} 秒")
        print(f"帧率: {video_info.get('fps', 0):.1f} fps")
        print(f"分辨率: {video_info.get('width', 0)}x{video_info.get('height', 0)}")
        print(f"片段数量: {len(segments)}")
        
        print("\n🎬 片段详情:")
        for segment in segments:
            print(f"片段 {segment['segment_id']}: "
                  f"{segment['start_time']:.1f}s - {segment['end_time']:.1f}s "
                  f"({segment['duration']:.1f}s) - {segment['scene_type']}")
            
            if segment.get('thumbnail_url'):
                print(f"  📸 缩略图: {segment['thumbnail_url']}")
            if segment.get('gif_url'):
                print(f"  🎞️  GIF: {segment['gif_url']}")
        
        # 计算平均片段长度
        if segments:
            avg_duration = sum(s['duration'] for s in segments) / len(segments)
            print(f"\n📈 平均片段长度: {avg_duration:.1f} 秒")
            
            # 检查是否是固定30秒分割
            is_fixed_30s = all(abs(s['duration'] - 30.0) < 1.0 for s in segments[:-1])  # 最后一个片段可能不足30秒
            if is_fixed_30s:
                print("⚠️  警告: 看起来仍然是固定30秒分割！")
            else:
                print("✅ 检测到变长片段，智能分割工作正常")
        
        print(f"\n💾 分析结果已保存")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_smart_segmentation() 
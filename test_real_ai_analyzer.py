#!/usr/bin/env python3
"""
测试真正的AI视频分析器
"""

import sys
import os
from pathlib import Path

# 添加backend路径
backend_path = Path(__file__).parent / "video-learning-helper-backend" / "app"
sys.path.append(str(backend_path))

from video_analyzer import VideoAnalyzer

def test_real_ai_analyzer():
    """测试真正的AI视频分析器"""
    print("🤖 测试真正的AI视频分析器...")
    
    # 测试视频路径
    video_path = "/Users/apulu/Desktop/learning/写给自卑的自己的一封信 - 001 - 写给自卑的自己的一封信.mp4"
    
    if not Path(video_path).exists():
        print(f"❌ 测试视频不存在: {video_path}")
        return
    
    # 创建分析器
    analyzer = VideoAnalyzer()
    
    # 测试任务ID
    task_id = "real_ai_test_001"
    
    print(f"📹 分析视频: {Path(video_path).name}")
    
    try:
        # 只测试视频分割功能
        task_config = {
            "video_segmentation": True,
            "transition_detection": True,
            "audio_transcription": False,  # 暂时跳过音频分析
            "report_generation": False
        }
        
        def progress_callback(progress, message):
            print(f"进度: {progress}% - {message}")
        
        results = analyzer.analyze_video(
            video_path=video_path,
            task_config=task_config,
            progress_callback=progress_callback,
            task_id=task_id
        )
        
        # 分析结果
        segments = results.get("segments", [])
        transitions = results.get("transitions", [])
        video_info = results.get("video_info", {})
        
        print("\n📊 分析结果:")
        print(f"视频时长: {video_info.get('duration', 0):.1f} 秒")
        print(f"帧率: {video_info.get('fps', 0):.1f} fps")
        print(f"分辨率: {video_info.get('width', 0)}x{video_info.get('height', 0)}")
        print(f"片段数量: {len(segments)}")
        print(f"转场数量: {len(transitions)}")
        
        print("\n🎬 AI智能分割片段详情:")
        for segment in segments:
            print(f"片段 {segment['segment_id']}: "
                  f"{segment['start_time']:.1f}s - {segment['end_time']:.1f}s "
                  f"({segment['duration']:.1f}s) - {segment.get('scene_type', '未知场景')}")
        
        print("\n🔄 转场检测结果:")
        for i, transition in enumerate(transitions[:10]):  # 只显示前10个
            print(f"转场 {i+1}: {transition['timestamp']:.1f}s "
                  f"(强度: {transition['strength']:.3f}, 类型: {transition['type']})")
        if len(transitions) > 10:
            print(f"... 还有 {len(transitions) - 10} 个转场")
        
        # 分析结果质量
        if segments:
            durations = [s['duration'] for s in segments]
            avg_duration = sum(durations) / len(durations)
            min_duration = min(durations)
            max_duration = max(durations)
            
            print(f"\n📈 分割质量分析:")
            print(f"平均片段长度: {avg_duration:.1f} 秒")
            print(f"最短片段: {min_duration:.1f} 秒")
            print(f"最长片段: {max_duration:.1f} 秒")
            
            # 检查是否真正智能分割
            variance = sum((d - avg_duration) ** 2 for d in durations) / len(durations)
            std_dev = variance ** 0.5
            
            if std_dev > 5.0:  # 如果标准差大于5秒，说明是变长分割
                print("✅ 检测到真正的AI智能分割！片段长度有明显变化")
            else:
                print("⚠️  警告: 片段长度变化较小，可能不是真正的智能分割")
        
        print(f"\n💾 分析结果已保存")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_real_ai_analyzer() 
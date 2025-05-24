#!/usr/bin/env python3
"""
视频分析功能专项测试
"""
import sys
import os
sys.path.append('video-learning-helper-backend')

from pathlib import Path
from app.video_analyzer_simple import VideoAnalyzer
import json

def test_video_analysis():
    """测试视频分析功能"""
    print("🎬 视频分析功能测试")
    print("=" * 50)
    
    # 初始化分析器
    analyzer = VideoAnalyzer()
    
    # 测试视频文件
    test_video = Path("video-learning-helper-backend/uploads/test_video.mp4")
    
    if not test_video.exists():
        print(f"❌ 测试视频不存在: {test_video}")
        return False
    
    print(f"📹 测试视频: {test_video}")
    print(f"   文件大小: {test_video.stat().st_size} bytes")
    
    # 分析配置
    task_config = {
        "video_segmentation": True,
        "transition_detection": True,
        "audio_transcription": True,
        "report_generation": True
    }
    
    task_id = "analysis_test_001"
    
    def progress_callback(progress, message):
        print(f"   📊 进度: {progress}% - {message}")
    
    try:
        print("\n🔍 开始视频分析...")
        results = analyzer.analyze_video(
            str(test_video), 
            task_config, 
            progress_callback, 
            task_id
        )
        
        print("\n✅ 分析完成!")
        
        # 显示结果摘要
        print("\n📋 分析结果摘要:")
        print(f"   视频信息: {results.get('video_info', {}).get('duration', 'N/A')}秒")
        print(f"   场景数量: {len(results.get('segments', []))}")
        print(f"   转场数量: {len(results.get('transitions', []))}")
        
        transcription = results.get('transcription', {})
        print(f"   转录文本: {transcription.get('text', 'N/A')[:50]}...")
        
        # 检查生成的文件
        print("\n📁 生成的文件:")
        uploads_dir = Path("video-learning-helper-backend/uploads")
        
        files_to_check = [
            f"{task_id}_subtitles.srt",
            f"{task_id}_script.md", 
            f"{task_id}_report.pdf",
            f"{task_id}_audio.wav"
        ]
        
        for filename in files_to_check:
            file_path = uploads_dir / filename
            if file_path.exists():
                size = file_path.stat().st_size
                print(f"   ✅ {filename}: {size} bytes")
            else:
                print(f"   ❌ {filename}: 文件不存在")
        
        # 保存详细结果
        results_file = uploads_dir / f"{task_id}_detailed_results.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"   💾 详细结果已保存: {results_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ 分析失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_individual_components():
    """测试各个组件"""
    print("\n🔧 组件测试")
    print("=" * 30)
    
    analyzer = VideoAnalyzer()
    test_video = Path("video-learning-helper-backend/uploads/test_video.mp4")
    
    if not test_video.exists():
        print("❌ 测试视频不存在")
        return
    
    # 1. 测试视频信息获取
    print("1️⃣ 测试视频信息获取...")
    try:
        video_info = analyzer._get_video_info(test_video)
        print(f"   ✅ 视频时长: {video_info.get('duration', 'N/A')}秒")
        print(f"   ✅ 分辨率: {video_info.get('width', 'N/A')}x{video_info.get('height', 'N/A')}")
        print(f"   ✅ 帧率: {video_info.get('fps', 'N/A')} FPS")
    except Exception as e:
        print(f"   ❌ 失败: {e}")
    
    # 2. 测试音频提取
    print("\n2️⃣ 测试音频提取...")
    try:
        audio_path = analyzer._extract_audio(test_video, "component_test")
        if audio_path.exists():
            print(f"   ✅ 音频提取成功: {audio_path}")
            print(f"   ✅ 文件大小: {audio_path.stat().st_size} bytes")
        else:
            print(f"   ❌ 音频文件不存在: {audio_path}")
    except Exception as e:
        print(f"   ❌ 失败: {e}")
    
    # 3. 测试视频分割
    print("\n3️⃣ 测试视频分割...")
    try:
        segments = analyzer._analyze_video_segmentation(test_video)
        print(f"   ✅ 分割成功，共 {len(segments)} 个场景")
        for i, segment in enumerate(segments[:3]):  # 只显示前3个
            print(f"      场景{i+1}: {segment['start_time']:.1f}s - {segment['end_time']:.1f}s")
    except Exception as e:
        print(f"   ❌ 失败: {e}")
    
    # 4. 测试转场检测
    print("\n4️⃣ 测试转场检测...")
    try:
        transitions = analyzer._detect_transitions(test_video)
        print(f"   ✅ 转场检测成功，共 {len(transitions)} 个转场")
        for i, transition in enumerate(transitions[:3]):  # 只显示前3个
            print(f"      转场{i+1}: {transition['time']:.1f}s - {transition['type']}")
    except Exception as e:
        print(f"   ❌ 失败: {e}")

def main():
    """主函数"""
    print("🎯 视频分析系统测试")
    print("=" * 60)
    
    # 检查环境
    print("🔍 环境检查:")
    
    # 检查OpenCV
    try:
        import cv2
        print(f"   ✅ OpenCV: {cv2.__version__}")
    except ImportError:
        print("   ❌ OpenCV: 未安装")
        return
    
    # 检查FFmpeg
    import subprocess
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("   ✅ FFmpeg: 可用")
        else:
            print("   ⚠️ FFmpeg: 不可用")
    except FileNotFoundError:
        print("   ❌ FFmpeg: 未安装")
    
    # 检查测试视频
    test_video = Path("video-learning-helper-backend/uploads/test_video.mp4")
    if test_video.exists():
        print(f"   ✅ 测试视频: {test_video} ({test_video.stat().st_size} bytes)")
    else:
        print(f"   ❌ 测试视频: {test_video} 不存在")
        return
    
    print()
    
    # 运行测试
    success = True
    
    # 组件测试
    test_individual_components()
    
    # 完整分析测试
    if not test_video_analysis():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 所有测试通过!")
    else:
        print("❌ 部分测试失败")
    
    print("\n📚 查看生成的文件:")
    print("   video-learning-helper-backend/uploads/")

if __name__ == "__main__":
    main() 
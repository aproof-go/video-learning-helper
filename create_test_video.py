#!/usr/bin/env python3
"""
创建真实的测试视频文件
"""
import cv2
import numpy as np
from pathlib import Path
import subprocess
import sys

def create_test_video_with_opencv(output_path: Path, duration: int = 10):
    """使用OpenCV创建测试视频"""
    try:
        # 视频参数
        width, height = 640, 480
        fps = 30
        total_frames = duration * fps
        
        # 创建视频写入器
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
        
        if not out.isOpened():
            print(f"❌ 无法创建视频文件: {output_path}")
            return False
        
        print(f"🎬 创建测试视频: {output_path}")
        print(f"   分辨率: {width}x{height}")
        print(f"   帧率: {fps} FPS")
        print(f"   时长: {duration} 秒")
        
        # 生成视频帧
        for frame_num in range(total_frames):
            # 创建彩色背景
            frame = np.zeros((height, width, 3), dtype=np.uint8)
            
            # 渐变背景色
            color_intensity = int(255 * (frame_num / total_frames))
            frame[:, :] = [color_intensity % 255, (color_intensity * 2) % 255, (color_intensity * 3) % 255]
            
            # 添加移动的圆形
            center_x = int(width * (0.5 + 0.3 * np.sin(frame_num * 0.1)))
            center_y = int(height * (0.5 + 0.3 * np.cos(frame_num * 0.1)))
            cv2.circle(frame, (center_x, center_y), 50, (255, 255, 255), -1)
            
            # 添加文字
            text = f"Frame {frame_num + 1}/{total_frames}"
            cv2.putText(frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
            
            # 添加时间戳
            timestamp = f"Time: {frame_num / fps:.2f}s"
            cv2.putText(frame, timestamp, (10, height - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
            
            # 写入帧
            out.write(frame)
            
            # 显示进度
            if frame_num % (fps * 2) == 0:  # 每2秒显示一次进度
                progress = (frame_num / total_frames) * 100
                print(f"   进度: {progress:.1f}%")
        
        # 释放资源
        out.release()
        
        # 验证文件
        if output_path.exists() and output_path.stat().st_size > 1000:
            print(f"✅ 视频创建成功: {output_path}")
            print(f"   文件大小: {output_path.stat().st_size} bytes")
            return True
        else:
            print(f"❌ 视频创建失败或文件太小")
            return False
            
    except Exception as e:
        print(f"❌ 创建视频时出错: {e}")
        return False

def create_test_video_with_ffmpeg(output_path: Path, duration: int = 10):
    """使用FFmpeg创建测试视频（如果可用）"""
    try:
        # 检查FFmpeg是否可用
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        if result.returncode != 0:
            print("⚠️ FFmpeg不可用，跳过FFmpeg方式")
            return False
        
        print(f"🎬 使用FFmpeg创建测试视频: {output_path}")
        
        # FFmpeg命令：创建包含音频的彩色测试视频
        cmd = [
            'ffmpeg', '-y',  # 覆盖已存在的文件
            '-f', 'lavfi',
            '-i', f'testsrc=duration={duration}:size=640x480:rate=30',
            '-f', 'lavfi', 
            '-i', f'sine=frequency=1000:duration={duration}',  # 添加1000Hz正弦波音频
            '-c:v', 'libx264',
            '-c:a', 'aac',  # 音频编码器
            '-pix_fmt', 'yuv420p',
            '-shortest',  # 以最短流为准
            str(output_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0 and output_path.exists():
            print(f"✅ FFmpeg视频创建成功: {output_path}")
            print(f"   文件大小: {output_path.stat().st_size} bytes")
            return True
        else:
            print(f"❌ FFmpeg创建失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ FFmpeg创建视频时出错: {e}")
        return False

def main():
    """主函数"""
    uploads_dir = Path("video-learning-helper-backend/uploads")
    uploads_dir.mkdir(exist_ok=True)
    
    # 要创建的测试视频文件
    test_videos = [
        ("test_video.mp4", 10),
        ("task_processor_test.mp4", 15),
        ("sample_video.mp4", 20)
    ]
    
    print("🎥 创建测试视频文件")
    print("=" * 50)
    
    success_count = 0
    
    for filename, duration in test_videos:
        output_path = uploads_dir / filename
        
        print(f"\n📹 创建: {filename}")
        
        # 先尝试FFmpeg（质量更好）
        if create_test_video_with_ffmpeg(output_path, duration):
            success_count += 1
            continue
        
        # 如果FFmpeg失败，使用OpenCV
        if create_test_video_with_opencv(output_path, duration):
            success_count += 1
        else:
            print(f"❌ 无法创建 {filename}")
    
    print(f"\n🎉 完成! 成功创建 {success_count}/{len(test_videos)} 个视频文件")
    
    # 验证创建的文件
    print("\n📋 文件验证:")
    for filename, _ in test_videos:
        file_path = uploads_dir / filename
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"   ✅ {filename}: {size} bytes")
            
            # 使用OpenCV验证视频可读性
            try:
                cap = cv2.VideoCapture(str(file_path))
                if cap.isOpened():
                    fps = cap.get(cv2.CAP_PROP_FPS)
                    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
                    duration = frame_count / fps if fps > 0 else 0
                    print(f"      📊 {fps:.1f} FPS, {frame_count:.0f} 帧, {duration:.1f}s")
                    cap.release()
                else:
                    print(f"      ⚠️ OpenCV无法读取")
            except Exception as e:
                print(f"      ❌ 验证失败: {e}")
        else:
            print(f"   ❌ {filename}: 文件不存在")

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
import sys
sys.path.insert(0, 'video-learning-helper-backend')

from moviepy.editor import VideoFileClip

video_path = 'video-learning-helper-backend/uploads/ebcdf5dc-fe9a-495c-b1d9-920e9765e8b3.mp4'

print(f"🎬 检查视频文件: {video_path}")

try:
    with VideoFileClip(video_path) as clip:
        print(f'视频时长: {clip.duration}s')
        print(f'视频FPS: {clip.fps}')
        print(f'视频尺寸: {clip.size}')
        print(f'有音频: {clip.audio is not None}')
        
        if clip.audio:
            print(f'音频时长: {clip.audio.duration}s')
            print(f'音频FPS: {clip.audio.fps}')
            print('✅ 视频包含音频轨道')
        else:
            print('❌ 视频没有音频轨道')
            
except Exception as e:
    print(f'❌ 检查失败: {e}')
    import traceback
    traceback.print_exc() 
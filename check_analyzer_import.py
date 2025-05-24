#!/usr/bin/env python3
import sys
sys.path.insert(0, 'video-learning-helper-backend')

from app.video_analyzer import VideoAnalyzer

analyzer = VideoAnalyzer()
print('VideoAnalyzer类来源:', VideoAnalyzer.__module__)
print('VideoAnalyzer文件路径:', VideoAnalyzer.__module__.replace('.', '/') + '.py')

# 检查分析方法
print('分析方法:', hasattr(analyzer, 'analyze_video'))
print('分割方法:', hasattr(analyzer, '_segment_video'))

# 测试一个小的分割
import tempfile
import cv2
import numpy as np

# 创建一个测试视频
test_video = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(test_video.name, fourcc, 1.0, (100, 100))

# 写入10帧
for i in range(10):
    frame = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    out.write(frame)
out.release()

print(f'测试视频创建: {test_video.name}')

# 测试分割
try:
    segments = analyzer._segment_video(test_video.name)
    print(f'分割结果: {len(segments)} 个片段')
    if segments:
        print('第一个片段场景类型:', segments[0].get('scene_type', '未知'))
        print('第一个片段时长:', segments[0].get('duration', 0))
except Exception as e:
    print(f'分割测试失败: {e}')

# 清理
import os
os.unlink(test_video.name) 
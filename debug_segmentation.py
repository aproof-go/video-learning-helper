#!/usr/bin/env python3
"""
调试AI分析器的分割逻辑
"""

import cv2
import numpy as np
from pathlib import Path
from sklearn.cluster import KMeans
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_video_segmentation():
    """调试视频分割算法"""
    video_path = Path("video-learning-helper-backend/uploads/46f6b955-7058-4361-8f83-39ef82fd9000.mp4")
    
    if not video_path.exists():
        print(f"❌ 视频文件不存在: {video_path}")
        return
    
    print("🔍 开始调试视频分割算法")
    print("=" * 60)
    
    try:
        cap = cv2.VideoCapture(str(video_path))
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps
        
        print(f"视频信息:")
        print(f"  帧率: {fps} FPS")
        print(f"  总帧数: {frame_count}")
        print(f"  时长: {duration:.2f} 秒")
        
        # 用于存储帧的特征
        frame_features = []
        timestamps = []
        
        # 每秒采样一帧进行分析
        sample_interval = max(1, int(fps))
        
        frame_idx = 0
        processed_frames = 0
        
        print(f"\n🎬 开始提取帧特征 (采样间隔: {sample_interval})")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_idx % sample_interval == 0:
                # 提取帧特征 (颜色直方图)
                feature = extract_frame_features(frame)
                frame_features.append(feature)
                timestamps.append(frame_idx / fps)
                
                processed_frames += 1
                if processed_frames % 30 == 0:
                    print(f"  已处理: {processed_frames} 帧, 时间戳: {timestamps[-1]:.2f}s")
            
            frame_idx += 1
        
        cap.release()
        
        print(f"\n📊 特征提取完成:")
        print(f"  总采样帧数: {len(frame_features)}")
        print(f"  特征维度: {len(frame_features[0]) if frame_features else 0}")
        print(f"  时间范围: 0 - {timestamps[-1]:.2f}s")
        
        if len(frame_features) < 2:
            print("❌ 采样帧数太少，无法进行分割")
            return
        
        # 使用K-means聚类进行场景分割
        n_clusters = min(10, len(frame_features) // 5)
        print(f"\n🧠 K-means聚类分析:")
        print(f"  聚类数量: {n_clusters}")
        
        if n_clusters > 1:
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            labels = kmeans.fit_predict(frame_features)
            
            print(f"  聚类标签: {labels[:20]}... (前20个)")
            print(f"  标签分布: {np.bincount(labels)}")
            
            # 找到场景边界
            scene_changes = [0]
            for i in range(1, len(labels)):
                if labels[i] != labels[i-1]:
                    scene_changes.append(i)
            scene_changes.append(len(labels) - 1)
            
            print(f"\n🎯 场景边界分析:")
            print(f"  场景变化点: {scene_changes}")
            print(f"  场景数量: {len(scene_changes) - 1}")
            
            # 生成分割结果
            segments = []
            for i in range(len(scene_changes) - 1):
                start_idx = scene_changes[i]
                end_idx = scene_changes[i + 1]
                
                start_time = timestamps[start_idx]
                end_time = timestamps[end_idx]
                duration = end_time - start_time
                
                segment = {
                    "segment_id": i + 1,
                    "start_time": start_time,
                    "end_time": end_time,
                    "duration": duration,
                    "scene_type": f"场景 {i + 1}",
                    "frame_count": (end_idx - start_idx) * sample_interval
                }
                segments.append(segment)
                
                print(f"  片段{i+1}: {start_time:.2f}s - {end_time:.2f}s (时长: {duration:.2f}s)")
            
            print(f"\n📋 分割结果总结:")
            print(f"  总片段数: {len(segments)}")
            durations = [s['duration'] for s in segments]
            print(f"  平均时长: {np.mean(durations):.2f}s")
            print(f"  最短片段: {np.min(durations):.2f}s")
            print(f"  最长片段: {np.max(durations):.2f}s")
            print(f"  时长标准差: {np.std(durations):.2f}s")
            
            # 检查是否所有片段都是30秒
            if all(abs(d - 30.0) < 0.1 for d in durations):
                print("⚠️  警告: 所有片段都是30秒，这不正常！")
                print("可能的原因:")
                print("  1. 采样间隔导致时间戳间隔固定为30秒")
                print("  2. K-means聚类算法没有找到有效的场景边界") 
                print("  3. 视频内容过于单一，缺乏场景变化")
                
                # 检查时间戳间隔
                if len(timestamps) > 1:
                    time_diffs = [timestamps[i+1] - timestamps[i] for i in range(len(timestamps)-1)]
                    print(f"\n  时间戳间隔分析:")
                    print(f"    间隔范围: {min(time_diffs):.2f}s - {max(time_diffs):.2f}s")
                    print(f"    平均间隔: {np.mean(time_diffs):.2f}s")
                    print(f"    是否固定间隔: {len(set([round(d, 1) for d in time_diffs])) == 1}")
            
        else:
            print("❌ 无法进行聚类分析")
            
    except Exception as e:
        logger.error(f"调试失败: {e}")
        import traceback
        traceback.print_exc()

def extract_frame_features(frame) -> np.ndarray:
    """提取帧特征 - 与AI分析器相同的逻辑"""
    # 转换到HSV颜色空间
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # 计算颜色直方图
    hist_h = cv2.calcHist([hsv], [0], None, [50], [0, 180])
    hist_s = cv2.calcHist([hsv], [1], None, [50], [0, 256])
    hist_v = cv2.calcHist([hsv], [2], None, [50], [0, 256])
    
    # 归一化并连接特征
    hist_h = hist_h.flatten() / hist_h.sum()
    hist_s = hist_s.flatten() / hist_s.sum()
    hist_v = hist_v.flatten() / hist_v.sum()
    
    feature = np.concatenate([hist_h, hist_s, hist_v])
    return feature

if __name__ == "__main__":
    debug_video_segmentation() 
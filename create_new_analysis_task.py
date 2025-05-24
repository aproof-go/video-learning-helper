#!/usr/bin/env python3
import sys
sys.path.insert(0, 'video-learning-helper-backend')

import requests
import json
import time
from pathlib import Path

# API配置
base_url = "http://localhost:8000"
frontend_url = "http://localhost:3000"

print("🚀 创建新的分析任务，测试所有修复...")

# 1. 检查现有视频
videos_response = requests.get(f"{base_url}/api/v1/videos", 
                              headers={"X-User-Email": "337939930@qq.com"})

if videos_response.status_code != 200:
    print(f"❌ 无法获取视频列表: {videos_response.status_code}")
    exit(1)

videos = videos_response.json()
print(f"📹 找到 {len(videos)} 个视频")

# 选择第一个视频进行测试
if not videos:
    print("❌ 没有找到视频文件")
    exit(1)

video = videos[0]
video_id = video["id"]
video_name = video.get("filename", "未知视频")

print(f"🎬 选择视频: {video_name} (ID: {video_id})")

# 2. 创建新的分析任务
task_data = {
    "video_id": video_id,
    "task_config": {
        "video_segmentation": True,
        "transition_detection": True,
        "audio_transcription": True,
        "report_generation": True
    }
}

task_response = requests.post(f"{base_url}/api/v1/analysis/tasks", 
                             json=task_data,
                             headers={"X-User-Email": "337939930@qq.com"})

if task_response.status_code != 200:
    print(f"❌ 创建任务失败: {task_response.status_code}")
    print(task_response.text)
    exit(1)

task = task_response.json()
task_id = task["id"]

print(f"✅ 任务创建成功!")
print(f"   任务ID: {task_id}")
print(f"   前端查看: {frontend_url}/analysis/{video_id}")

# 3. 监控任务进度
print("\n🔍 监控分析进度...")
start_time = time.time()
last_progress = ""

while True:
    try:
        # 获取任务状态
        status_response = requests.get(f"{base_url}/api/v1/analysis/videos/{video_id}/tasks",
                                     headers={"X-User-Email": "337939930@qq.com"})
        
        if status_response.status_code == 200:
            tasks = status_response.json()
            current_task = None
            
            for t in tasks:
                if t["id"] == task_id:
                    current_task = t
                    break
            
            if current_task:
                status = current_task["status"]
                progress = current_task.get("progress", "0")
                
                if progress != last_progress:
                    elapsed = time.time() - start_time
                    print(f"   [{elapsed:.1f}s] 状态: {status}, 进度: {progress}%")
                    last_progress = progress
                
                if status == "completed":
                    print("🎉 分析完成!")
                    break
                elif status == "failed":
                    error_msg = current_task.get("error_message", "未知错误")
                    print(f"❌ 分析失败: {error_msg}")
                    exit(1)
            
    except Exception as e:
        print(f"⚠️ 监控错误: {e}")
    
    time.sleep(2)

# 4. 检查分析结果
print("\n📊 检查分析结果...")

# 等待一下确保文件保存完成
time.sleep(2)

results_url = f"{base_url}/uploads/{task_id}_results.json"
results_response = requests.get(results_url)

if results_response.status_code == 200:
    results = results_response.json()
    
    print(f"✅ 分析结果文件存在")
    
    # 检查各项指标
    segments = results.get("segments", [])
    transitions = results.get("transitions", [])
    transcription = results.get("transcription", {})
    
    print(f"   📁 视频分段: {len(segments)} 个")
    print(f"   🎞️  转场检测: {len(transitions)} 个")
    print(f"   🎤 音频转录: {'✅' if transcription.get('text') else '❌'}")
    
    # 检查缩略图和GIF
    segments_with_thumbnails = sum(1 for s in segments if s.get('thumbnail_url'))
    segments_with_gifs = sum(1 for s in segments if s.get('gif_url'))
    
    print(f"   🖼️  缩略图: {segments_with_thumbnails}/{len(segments)} 个")
    print(f"   🎥 GIF动画: {segments_with_gifs}/{len(segments)} 个")
    
    # 检查场景类型格式
    ai_format_segments = sum(1 for s in segments if s.get('scene_type', '').startswith('场景'))
    print(f"   🤖 AI格式场景: {ai_format_segments}/{len(segments)} 个")
    
    # 计算质量分数
    quality_score = 0
    if len(segments) > 0:
        quality_score += 40  # 基础分段分数
        
        # 转场检测分数
        expected_transitions = max(len(segments) // 3, 5)
        transition_score = min(len(transitions) / expected_transitions, 1.0) * 25
        quality_score += transition_score
        
        # 缩略图分数
        thumbnail_score = (segments_with_thumbnails / len(segments)) * 10
        quality_score += thumbnail_score
        
        # GIF分数
        gif_score = (segments_with_gifs / len(segments)) * 10
        quality_score += gif_score
        
        # 音频转录分数
        if transcription.get('text'):
            quality_score += 10
        
        # AI格式分数
        if ai_format_segments == len(segments):
            quality_score += 5
    
    print(f"\n📈 数据质量评估:")
    print(f"   总体质量分数: {quality_score:.1f}%")
    
    if quality_score >= 90:
        print("🎉 优秀！数据质量很高")
    elif quality_score >= 75:
        print("👍 良好！数据质量可接受") 
    elif quality_score >= 60:
        print("⚠️ 一般，需要一些改进")
    else:
        print("❌ 较差，需要大幅改进")
    
    # 检查PDF报告
    pdf_url = f"{base_url}/uploads/{task_id}_report.pdf"
    pdf_response = requests.head(pdf_url)
    
    if pdf_response.status_code == 200:
        print(f"📄 PDF报告: ✅ 可访问 ({pdf_url})")
    else:
        print(f"📄 PDF报告: ❌ 不可访问")
    
    print(f"\n🌐 前端查看地址: {frontend_url}/analysis/{video_id}")
    
else:
    print(f"❌ 无法获取分析结果: {results_response.status_code}")

print(f"\n⏱️ 总分析时间: {time.time() - start_time:.1f} 秒") 
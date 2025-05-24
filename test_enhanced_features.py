#!/usr/bin/env python3
import sys
sys.path.insert(0, 'video-learning-helper-backend')

import requests
import json
import time
from pathlib import Path

# 测试配置
base_url = "http://localhost:8000"
frontend_url = "http://localhost:3000"
user_email = "337939930@qq.com"

print("🧪 测试所有增强功能...")

# 1. 获取视频列表
print("\n📹 获取可用视频...")
videos_response = requests.get(f"{base_url}/api/v1/videos", 
                              headers={"X-User-Email": user_email})

if videos_response.status_code != 200:
    print(f"❌ 获取视频失败: {videos_response.status_code}")
    exit(1)

videos = videos_response.json()
if not videos:
    print("❌ 没有可用视频")
    exit(1)

# 选择第一个视频
video = videos[0]
video_id = video["id"]
print(f"✅ 选择视频: {video.get('filename', '未知')} (ID: {video_id})")

# 2. 创建新的分析任务
print("\n🚀 创建增强分析任务...")
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
                             headers={"X-User-Email": user_email})

if task_response.status_code != 200:
    print(f"❌ 创建任务失败: {task_response.status_code}")
    print(task_response.text)
    exit(1)

task = task_response.json()
task_id = task["id"]
print(f"✅ 任务创建成功! ID: {task_id}")

# 3. 监控任务进度
print("\n⏳ 监控任务进度...")
start_time = time.time()
last_progress = ""

while True:
    try:
        status_response = requests.get(f"{base_url}/api/v1/analysis/videos/{video_id}/tasks",
                                     headers={"X-User-Email": user_email})
        
        if status_response.status_code == 200:
            tasks = status_response.json()
            current_task = next((t for t in tasks if t["id"] == task_id), None)
            
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
    
    time.sleep(3)

# 4. 检查增强分析结果
print("\n📊 检查增强分析结果...")
time.sleep(2)

results_url = f"{base_url}/uploads/{task_id}_results.json"
results_response = requests.get(results_url)

if results_response.status_code != 200:
    print(f"❌ 无法获取分析结果: {results_response.status_code}")
    exit(1)

results = results_response.json()

# 检查基础数据
segments = results.get("segments", [])
transitions = results.get("transitions", [])
transcription = results.get("transcription", {})

print(f"📁 视频分段: {len(segments)} 个")
print(f"🎞️  转场检测: {len(transitions)} 个")
print(f"🎤 音频转录: {'✅' if transcription.get('text') else '❌'}")

# 检查新增功能
print("\n🔍 检查增强功能...")

# 1. 详细分析字段
detailed_segments = 0
for segment in segments:
    if all(key in segment for key in ['composition_analysis', 'camera_movement', 'theme_analysis', 'critical_review']):
        detailed_segments += 1

print(f"🎨 详细分析覆盖: {detailed_segments}/{len(segments)} 个片段")

# 2. 缩略图和GIF
thumbnails = sum(1 for s in segments if s.get('thumbnail_url'))
gifs = sum(1 for s in segments if s.get('gif_url'))

print(f"🖼️  缩略图生成: {thumbnails}/{len(segments)} 个")
print(f"🎥 GIF动画生成: {gifs}/{len(segments)} 个")

# 3. 转录文本分配
segments_with_text = sum(1 for s in segments if s.get('transcript_text'))
print(f"📝 转录文本分配: {segments_with_text}/{len(segments)} 个片段")

# 4. 路径匹配检查
video_path = results.get("video_path", "")
task_id_in_path = task_id in video_path
print(f"🔗 路径匹配: {'✅' if task_id_in_path else '❌'} (路径: {video_path})")

# 5. 脚本文件检查
script_url = f"{base_url}/uploads/{task_id}_script.md"
script_response = requests.head(script_url)
script_exists = script_response.status_code == 200

print(f"📋 脚本文件: {'✅' if script_exists else '❌'} ({script_url})")

if script_exists:
    # 下载并检查脚本内容
    script_content_response = requests.get(script_url)
    if script_content_response.status_code == 200:
        script_content = script_content_response.text
        has_detailed_analysis = "## 分段详细分析" in script_content
        has_overall_summary = "## 总体评价" in script_content
        print(f"   📖 包含详细分析: {'✅' if has_detailed_analysis else '❌'}")
        print(f"   📈 包含总体评价: {'✅' if has_overall_summary else '❌'}")
        print(f"   📏 脚本长度: {len(script_content)} 字符")

# 6. PDF报告检查
pdf_url = f"{base_url}/uploads/{task_id}_report.pdf"
pdf_response = requests.head(pdf_url)
pdf_exists = pdf_response.status_code == 200

print(f"📄 PDF报告: {'✅' if pdf_exists else '❌'} ({pdf_url})")

# 7. 示例详细分析展示
if segments and detailed_segments > 0:
    print("\n🎬 示例详细分析:")
    sample_segment = next(s for s in segments if 'composition_analysis' in s)
    print(f"   片段 {sample_segment['segment_id']} ({sample_segment['duration']:.1f}秒)")
    print(f"   构图: {sample_segment.get('composition_analysis', '无')[:50]}...")
    print(f"   运镜: {sample_segment.get('camera_movement', '无')[:50]}...")
    print(f"   主题: {sample_segment.get('theme_analysis', '无')[:50]}...")
    print(f"   简评: {sample_segment.get('critical_review', '无')[:50]}...")

# 8. 质量评分
quality_score = 0
total_checks = 8

# 基础功能 (25分)
if len(segments) > 0:
    quality_score += 25

# 详细分析覆盖率 (20分)
if detailed_segments > 0:
    coverage_ratio = detailed_segments / len(segments)
    quality_score += int(coverage_ratio * 20)

# 缩略图和GIF (15分)
if thumbnails > 0 and gifs > 0:
    media_ratio = min(thumbnails, gifs) / len(segments)
    quality_score += int(media_ratio * 15)

# 转录文本分配 (10分)
if segments_with_text > 0:
    text_ratio = segments_with_text / len(segments)
    quality_score += int(text_ratio * 10)

# 路径匹配 (10分)
if task_id_in_path:
    quality_score += 10

# 脚本生成 (10分)
if script_exists:
    quality_score += 10

# 转场检测 (5分)
if len(transitions) > 0:
    quality_score += 5

# PDF报告 (5分)
if pdf_exists:
    quality_score += 5

print(f"\n📈 整体质量评分: {quality_score}/100")

if quality_score >= 90:
    print("🎉 优秀！所有功能都运行良好")
elif quality_score >= 75:
    print("👍 良好！大部分功能正常")
elif quality_score >= 60:
    print("⚠️ 一般，部分功能需要改进")
else:
    print("❌ 需要大幅改进")

print(f"\n🌐 前端查看: {frontend_url}/analysis/{video_id}")
print(f"⏱️ 总耗时: {time.time() - start_time:.1f} 秒") 
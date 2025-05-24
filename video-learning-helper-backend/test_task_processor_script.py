#!/usr/bin/env python3
"""测试任务处理器的脚本生成流程"""

from app.video_analyzer_simple import VideoAnalyzer
from pathlib import Path
import json

def test_task_processor_script():
    print("🔧 测试任务处理器的脚本生成流程")
    
    # 创建测试视频文件
    test_video = Path('uploads/task_processor_test.mp4')
    test_video.write_text('task processor test video content')
    print(f"📝 创建测试视频文件: {test_video}")

    # 创建分析器（模拟任务处理器的方式）
    analyzer = VideoAnalyzer()
    
    # 模拟任务配置（与测试中相同）
    task_config = {
        'video_segmentation': True,
        'transition_detection': True,
        'audio_transcription': True,
        'report_generation': True
    }
    
    task_id = 'task_processor_test_789'
    
    print("🔄 开始分析（模拟任务处理器）...")
    results = analyzer.analyze_video(str(test_video), task_config, task_id=task_id)
    
    print("📋 分析结果:")
    print(json.dumps(results, ensure_ascii=False, indent=2, default=str))
    
    # 检查转录结果
    transcription = results.get('transcription', {})
    print(f"\n📊 转录结果包含的字段: {list(transcription.keys())}")
    
    if "script_file" in transcription:
        script_file_path = Path(transcription["script_file"])
        if script_file_path.exists():
            print(f"✅ 脚本文件已生成: {script_file_path}")
            print(f"📊 文件大小: {script_file_path.stat().st_size} bytes")
        else:
            print(f"❌ 脚本文件路径存在但文件不存在: {script_file_path}")
    else:
        print("❌ 转录结果中没有script_file字段")
    
    # 检查实际生成的文件
    uploads_dir = Path('uploads')
    script_files = list(uploads_dir.glob(f'{task_id}*script*'))
    if script_files:
        print(f"✅ 找到脚本文件: {[f.name for f in script_files]}")
    else:
        print("❌ 在uploads目录中未找到脚本文件")
    
    # 模拟任务处理器的文件处理逻辑
    print("\n🔄 模拟任务处理器文件处理逻辑...")
    update_data = {}
    
    # 处理脚本文件
    if "script_file" in transcription:
        script_path = Path(transcription["script_file"])
        if script_path.exists():
            expected_path = uploads_dir / f"{task_id}_script.md"
            if script_path.resolve() == expected_path.resolve():
                update_data["script_md_url"] = f"/uploads/{expected_path.name}"
                print(f"✅ 脚本文件已在正确位置: {expected_path}")
            else:
                import shutil
                shutil.copy2(script_path, expected_path)
                update_data["script_md_url"] = f"/uploads/{expected_path.name}"
                print(f"✅ 脚本文件已复制: {script_path} -> {expected_path}")
    
    # 检查是否有直接生成的脚本文件
    existing_script = uploads_dir / f"{task_id}_script.md"
    if existing_script.exists() and "script_md_url" not in update_data:
        update_data["script_md_url"] = f"/uploads/{existing_script.name}"
        print(f"✅ 发现现有脚本文件: {existing_script}")
    
    print(f"\n📊 任务处理器将更新的数据: {update_data}")
    
    if "script_md_url" in update_data:
        print("✅ 脚本URL将被保存到数据库")
    else:
        print("❌ 脚本URL将不会被保存到数据库")

if __name__ == "__main__":
    test_task_processor_script() 
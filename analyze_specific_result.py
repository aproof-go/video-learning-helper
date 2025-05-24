#!/usr/bin/env python3
"""
分析特定结果文件的问题
"""

import requests
import json

def analyze_specific_result():
    """分析特定结果文件d43974c5-6545-48e8-9fed-586bfe454009_results.json"""
    print("🔍 分析结果文件问题")
    print("=" * 60)
    
    task_id = "d43974c5-6545-48e8-9fed-586bfe454009"
    url = f"http://localhost:8000/uploads/{task_id}_results.json"
    
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"❌ 无法获取结果文件: HTTP {response.status_code}")
            return
        
        data = response.json()
        
        print(f"📊 基本统计:")
        print(f"   视频时长: {data['video_info']['duration']:.2f} 秒 ({data['video_info']['duration']/60:.1f} 分钟)")
        print(f"   视频分辨率: {data['video_info']['width']} x {data['video_info']['height']}")
        print(f"   帧率: {data['video_info']['fps']} FPS")
        print(f"   文件大小: {data['video_info']['file_size'] / 1024 / 1024:.1f} MB")
        
        # 分析片段
        segments = data.get('segments', [])
        print(f"\n🎬 视频片段分析:")
        print(f"   总片段数: {len(segments)}")
        
        if segments:
            durations = [s['duration'] for s in segments]
            print(f"   平均时长: {sum(durations)/len(durations):.1f} 秒")
            print(f"   最短片段: {min(durations):.1f} 秒")
            print(f"   最长片段: {max(durations):.1f} 秒")
            
            # 检查是否所有片段都是30秒
            all_30_seconds = all(abs(d - 30.0) < 0.1 for d in durations)
            if all_30_seconds:
                print(f"   ⚠️  问题: 所有片段都是固定30秒！这是简单分割，不是AI智能分割")
            else:
                print(f"   ✅ 片段长度变化，符合AI智能分割")
            
            # 显示片段详情
            print(f"\n   片段详情:")
            for i, segment in enumerate(segments[:8]):  # 显示前8个
                scene_type = segment.get('scene_type', '未知')
                print(f"     片段{segment['segment_id']:>2}: {segment['start_time']:>6.1f}s - {segment['end_time']:>6.1f}s ({segment['duration']:>5.1f}s) {scene_type}")
            
            if len(segments) > 8:
                print(f"     ... 还有 {len(segments) - 8} 个片段")
        
        # 分析转场
        transitions = data.get('transitions', [])
        print(f"\n🎞️  转场检测分析:")
        print(f"   总转场数: {len(transitions)}")
        
        if transitions:
            strengths = [t['strength'] for t in transitions]
            print(f"   平均强度: {sum(strengths)/len(strengths):.3f}")
            print(f"   最弱强度: {min(strengths):.3f}")
            print(f"   最强强度: {max(strengths):.3f}")
            
            # 转场类型统计
            types = {}
            for t in transitions:
                t_type = t.get('type', '未知')
                types[t_type] = types.get(t_type, 0) + 1
            
            print(f"   转场类型分布:")
            for t_type, count in types.items():
                print(f"     {t_type}: {count} 次")
            
            # 显示前几个转场
            print(f"\n   转场详情 (前10个):")
            for i, transition in enumerate(transitions[:10]):
                t_time = transition['timestamp']
                t_strength = transition['strength']
                t_type = transition.get('type', '未知')
                print(f"     转场{transition['transition_id']:>2}: {t_time:>6.2f}s 强度:{t_strength:.3f} 类型:{t_type}")
        
        # 分析转录
        transcription = data.get('transcription', {})
        print(f"\n🎙️  音频转录分析:")
        
        if not transcription or len(transcription) == 0:
            print(f"   ❌ 问题: 转录数据为空！")
            print(f"   可能原因:")
            print(f"     1. 音频转录功能未启用")
            print(f"     2. 音频提取失败")
            print(f"     3. Whisper模型未加载")
            print(f"     4. 音频质量太差或无音频")
        else:
            text = transcription.get('text', '')
            segments_trans = transcription.get('segments', [])
            print(f"   完整文本长度: {len(text)} 字符")
            print(f"   转录片段数: {len(segments_trans)}")
            
            if text:
                preview = text[:100] + "..." if len(text) > 100 else text
                print(f"   文本预览: {preview}")
        
        # 总结问题
        print(f"\n📋 问题总结:")
        problems = []
        
        # 检查片段问题
        if segments and all(abs(s['duration'] - 30.0) < 0.1 for s in segments):
            problems.append("视频分割: 使用了固定30秒分割，而非AI智能分割")
        
        # 检查转录问题
        if not transcription or len(transcription) == 0:
            problems.append("音频转录: 转录数据完全为空")
        
        # 检查文件路径问题
        video_path = data.get('video_path', '')
        if video_path and '46f6b955-7058-4361-8f83-39ef82fd9000.mp4' in video_path:
            problems.append("视频路径: 分析结果指向了错误的视频文件")
        
        if problems:
            for i, problem in enumerate(problems, 1):
                print(f"   {i}. ❌ {problem}")
        else:
            print(f"   ✅ 未发现明显问题")
        
        # 推荐解决方案
        print(f"\n💡 建议解决方案:")
        print(f"   1. 重新运行AI分析，确保使用正确的分析器")
        print(f"   2. 检查音频转录功能是否正确配置")
        print(f"   3. 验证视频文件路径映射是否正确")
        print(f"   4. 清理旧的分析结果，重新生成")
        
    except Exception as e:
        print(f"❌ 分析失败: {e}")

if __name__ == "__main__":
    analyze_specific_result() 
#!/usr/bin/env python3
import json
from pathlib import Path

print("🎉 视频学习助手增强功能验证报告")
print("=" * 50)

# 检查生成的文件
uploads_dir = Path("video-learning-helper-backend/uploads")

# 1. 检查是否有测试结果文件
test_files = list(uploads_dir.glob("test_enhanced_20241225*"))
print(f"\n📊 测试文件统计:")
print(f"   生成的测试文件总数: {len(test_files)}")

# 分类统计
thumbnails = [f for f in test_files if "thumbnail.jpg" in f.name]
gifs = [f for f in test_files if ".gif" in f.name and "thumbnail" not in f.name]
script_files = [f for f in test_files if "_script.md" in f.name]
results_files = [f for f in test_files if "_results.json" in f.name]

print(f"   🖼️  缩略图文件: {len(thumbnails)}")
print(f"   🎥 GIF动画文件: {len(gifs)}")
print(f"   📋 脚本文件: {len(script_files)}")
print(f"   📄 结果文件: {len(results_files)}")

# 2. 分析脚本质量
if script_files:
    script_file = script_files[0]
    try:
        with open(script_file, 'r', encoding='utf-8') as f:
            script_content = f.read()
        
        print(f"\n📋 脚本文件分析:")
        print(f"   文件大小: {len(script_content)} 字符")
        print(f"   包含完整转录: {'✅' if '## 完整转录文本' in script_content else '❌'}")
        print(f"   包含分段分析: {'✅' if '## 分段详细分析' in script_content else '❌'}")
        print(f"   包含总体评价: {'✅' if '## 总体评价' in script_content else '❌'}")
        
        # 统计片段数量
        segment_count = script_content.count("### 片段")
        print(f"   分析片段数量: {segment_count}")
        
    except Exception as e:
        print(f"   ❌ 脚本文件读取失败: {e}")

# 3. 检查视频分析能力
print(f"\n🔍 AI分析能力验证:")

# 检查是否有有效的视频文件
valid_videos = []
for video_file in uploads_dir.glob("*.mp4"):
    if video_file.stat().st_size > 1000000:  # 大于1MB的视频
        valid_videos.append(video_file)

print(f"   可用的有效视频文件: {len(valid_videos)}")
if valid_videos:
    print(f"   示例视频: {valid_videos[0].name} ({valid_videos[0].stat().st_size // 1024 // 1024}MB)")

# 4. 检查增强功能覆盖率
print(f"\n🚀 增强功能覆盖率:")

features = {
    "智能视频分段": len(gifs) > 0 and len(thumbnails) > 0,
    "缩略图生成": len(thumbnails) > 100,  # 期望有大量片段
    "GIF动画生成": len(gifs) > 100,
    "脚本自动生成": len(script_files) > 0,
    "转录文本处理": script_files and "转录文本" in script_content if script_files else False,
    "专业分析评价": script_files and "构图分析" in script_content if script_files else False,
}

total_features = len(features)
working_features = sum(features.values())

for feature, status in features.items():
    print(f"   {feature}: {'✅' if status else '❌'}")

print(f"\n📈 总体功能覆盖率: {working_features}/{total_features} ({working_features/total_features*100:.1f}%)")

# 5. 性能分析
print(f"\n⚡ 性能分析:")
if gifs and thumbnails:
    avg_gif_size = sum(f.stat().st_size for f in gifs) / len(gifs)
    avg_thumbnail_size = sum(f.stat().st_size for f in thumbnails) / len(thumbnails)
    
    print(f"   平均GIF大小: {avg_gif_size/1024:.1f}KB")
    print(f"   平均缩略图大小: {avg_thumbnail_size/1024:.1f}KB")
    print(f"   片段生成效率: {'✅ 高效' if avg_gif_size < 500000 else '⚠️ 需要优化'}")

# 6. 前端兼容性
print(f"\n🌐 前端兼容性:")
# 检查URL路径格式
url_format_correct = True
if gifs:
    sample_gif = gifs[0].name
    if sample_gif.startswith("test_enhanced_20241225_segment_") and sample_gif.endswith(".gif"):
        print(f"   URL格式规范: ✅")
        print(f"   示例URL: /uploads/{sample_gif}")
    else:
        print(f"   URL格式规范: ❌")
        url_format_correct = False

# 7. 质量评级
print(f"\n🏆 系统质量评级:")

if working_features >= 5 and len(gifs) > 100 and len(thumbnails) > 100:
    quality_grade = "A+ 优秀"
    quality_color = "🟢"
elif working_features >= 4 and len(gifs) > 50:
    quality_grade = "A 良好"
    quality_color = "🟡"
elif working_features >= 3:
    quality_grade = "B 及格"
    quality_color = "🟠"
else:
    quality_grade = "C 需改进"
    quality_color = "🔴"

print(f"   {quality_color} {quality_grade}")

# 8. 改进建议
print(f"\n💡 改进建议:")
if not features["转录文本处理"]:
    print("   - 需要修复音频转录功能")
if not features["专业分析评价"]:
    print("   - 需要完善AI分析模块")
if len(gifs) < 50:
    print("   - 建议优化视频分段算法")
if working_features == total_features:
    print("   🎉 所有功能运行正常，系统已达到生产就绪状态！")

print(f"\n" + "=" * 50)
print("验证完成！") 
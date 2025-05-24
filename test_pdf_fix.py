#!/usr/bin/env python3
import sys
sys.path.insert(0, 'video-learning-helper-backend')

from app.video_analyzer import VideoAnalyzer
from pathlib import Path
import json

print('🔧 测试PDF中文字体修复...')

# 读取现有的分析结果
results_path = Path('video-learning-helper-backend/uploads/487b9247-03b6-4e71-af4e-5b13d005af9f_results.json')

if results_path.exists():
    print(f'📄 读取分析结果: {results_path}')
    with open(results_path, 'r', encoding='utf-8') as f:
        results = json.load(f)
    
    # 创建分析器实例
    analyzer = VideoAnalyzer()
    
    # 获取原始视频路径
    video_path = Path(results['video_path'])
    
    try:
        # 重新生成PDF报告
        print('🎨 生成新的PDF报告...')
        report_path = analyzer._generate_report(results, video_path)
        print(f'✅ PDF报告已生成: {report_path}')
        
        # 检查文件是否存在
        if report_path.exists():
            file_size = report_path.stat().st_size
            print(f'📊 报告文件大小: {file_size} bytes')
            print('✅ PDF生成成功！请检查中文是否正常显示')
        else:
            print('❌ PDF文件未生成')
            
    except Exception as e:
        print(f'❌ PDF生成失败: {e}')
        import traceback
        traceback.print_exc()
        
else:
    print(f'❌ 找不到分析结果文件: {results_path}') 
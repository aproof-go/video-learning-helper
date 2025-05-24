#!/usr/bin/env python3
import sys
sys.path.insert(0, 'video-learning-helper-backend')
from app.video_analyzer import VideoAnalyzer

print('🧠 测试AI分析器和Whisper模型...')
try:
    analyzer = VideoAnalyzer()
    print('✅ AI分析器创建成功')
    
    if hasattr(analyzer, 'whisper_model') and analyzer.whisper_model:
        print('✅ Whisper模型加载成功')
        print(f'模型类型: {type(analyzer.whisper_model)}')
    else:
        print('❌ Whisper模型未加载')
        print(f'whisper_model属性: {getattr(analyzer, "whisper_model", "不存在")}')
        
except Exception as e:
    print(f'❌ 测试失败: {e}')
    import traceback
    traceback.print_exc() 
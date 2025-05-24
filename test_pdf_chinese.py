#!/usr/bin/env python3
import sys
sys.path.insert(0, 'video-learning-helper-backend')

from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle
from pathlib import Path
import platform

print('🧪 测试PDF中文字体渲染...')

# 注册中文字体（与视频分析器相同的逻辑）
try:
    if platform.system() == "Darwin":  # macOS
        font_path = "/System/Library/Fonts/STHeiti Medium.ttc"
        if not Path(font_path).exists():
            font_path = "/System/Library/Fonts/STHeiti Light.ttc"
        if not Path(font_path).exists():
            font_path = "/System/Library/Fonts/Helvetica.ttc"
    
    if Path(font_path).exists():
        pdfmetrics.registerFont(TTFont('ChineseFont', font_path))
        chinese_font = 'ChineseFont'
        print(f'✅ 使用字体: {font_path}')
    else:
        chinese_font = 'Helvetica'
        print('⚠️ 使用默认字体: Helvetica')
        
except Exception as e:
    chinese_font = 'Helvetica'
    print(f'❌ 字体注册失败: {e}')

# 创建测试PDF
output_path = "test_chinese_pdf.pdf"
doc = SimpleDocTemplate(output_path, pagesize=A4)
styles = getSampleStyleSheet()

# 创建中文样式
chinese_style = ParagraphStyle(
    'ChineseStyle',
    parent=styles['Normal'],
    fontName=chinese_font,
    fontSize=12
)

story = []
story.append(Paragraph("视频分析报告测试", chinese_style))
story.append(Paragraph("场景分割结果：共识别 38 个场景", chinese_style))
story.append(Paragraph("转场检测结果：共检测到 26 个转场", chinese_style))
story.append(Paragraph("音频转录：你要更自信一點，別那麼擔心", chinese_style))

try:
    doc.build(story)
    print(f'✅ 测试PDF已生成: {output_path}')
    
    # 检查文件大小
    file_size = Path(output_path).stat().st_size
    print(f'📊 文件大小: {file_size} bytes')
    print('✅ 请打开PDF文件检查中文显示是否正常')
    
except Exception as e:
    print(f'❌ PDF生成失败: {e}')
    import traceback
    traceback.print_exc() 
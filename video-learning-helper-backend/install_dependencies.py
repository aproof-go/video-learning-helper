#!/usr/bin/env python3
"""
依赖安装脚本
自动检测和安装AI视频分析所需的依赖
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description=""):
    """运行命令并显示进度"""
    print(f"\n🔄 {description}")
    print(f"执行命令: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} 成功")
            return True
        else:
            print(f"❌ {description} 失败")
            print(f"错误信息: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ 执行命令失败: {e}")
        return False

def check_python_version():
    """检查Python版本"""
    version = sys.version_info
    print(f"Python版本: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ 需要Python 3.8或更高版本")
        return False
    
    print("✅ Python版本符合要求")
    return True

def install_pytorch():
    """安装PyTorch"""
    print("\n📦 安装PyTorch...")
    
    # 检测系统和CUDA支持
    import platform
    system = platform.system().lower()
    
    if system == "darwin":  # macOS
        command = "pip install torch torchvision torchaudio"
    elif system == "linux":
        # 简化版本，使用CPU版本
        command = "pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu"
    else:  # Windows
        command = "pip install torch torchvision torchaudio"
    
    return run_command(command, "安装PyTorch")

def install_opencv():
    """安装OpenCV"""
    print("\n📦 安装OpenCV...")
    
    # 先尝试安装opencv-python
    if run_command("pip install opencv-python==4.8.1.78", "安装opencv-python"):
        return True
    
    # 如果失败，尝试安装headless版本
    return run_command("pip install opencv-python-headless==4.8.1.78", "安装opencv-python-headless")

def install_whisper():
    """安装Whisper"""
    print("\n📦 安装OpenAI Whisper...")
    
    # 安装Whisper及其依赖
    commands = [
        ("pip install openai-whisper", "安装Whisper"),
        ("pip install tiktoken", "安装tiktoken"),
    ]
    
    for command, description in commands:
        if not run_command(command, description):
            return False
    
    return True

def install_other_dependencies():
    """安装其他依赖"""
    print("\n📦 安装其他依赖...")
    
    dependencies = [
        "moviepy==1.0.3",
        "librosa==0.10.1",
        "soundfile==0.12.1",
        "scikit-learn==1.3.2",
        "matplotlib==3.8.2",
        "reportlab==4.0.7",
        "fpdf2==2.7.6",
        "numpy==1.24.3",
        "scipy==1.11.4",
        "Pillow==10.1.0",
        "tqdm==4.66.1",
        "imageio==2.33.0",
        "imageio-ffmpeg==0.4.9"
    ]
    
    success = True
    for dep in dependencies:
        if not run_command(f"pip install {dep}", f"安装{dep.split('==')[0]}"):
            success = False
    
    return success

def download_whisper_model():
    """下载Whisper模型"""
    print("\n📥 下载Whisper模型...")
    
    try:
        import whisper
        print("正在下载base模型...")
        model = whisper.load_model("base")
        print("✅ Whisper模型下载成功")
        return True
    except Exception as e:
        print(f"❌ Whisper模型下载失败: {e}")
        return False

def verify_installation():
    """验证安装"""
    print("\n🔍 验证安装...")
    
    test_imports = [
        ("cv2", "OpenCV"),
        ("whisper", "Whisper"),
        ("torch", "PyTorch"),
        ("moviepy.editor", "MoviePy"),
        ("librosa", "Librosa"),
        ("sklearn", "Scikit-learn"),
        ("reportlab", "ReportLab"),
        ("numpy", "NumPy"),
        ("scipy", "SciPy")
    ]
    
    failed_imports = []
    
    for module, name in test_imports:
        try:
            __import__(module)
            print(f"✅ {name} 导入成功")
        except ImportError as e:
            print(f"❌ {name} 导入失败: {e}")
            failed_imports.append(name)
    
    if failed_imports:
        print(f"\n❌ 以下模块导入失败: {', '.join(failed_imports)}")
        return False
    
    print("\n✅ 所有依赖验证成功！")
    return True

def main():
    """主函数"""
    print("🚀 AI视频分析依赖安装器")
    print("=" * 50)
    
    # 检查Python版本
    if not check_python_version():
        sys.exit(1)
    
    # 升级pip
    run_command("pip install --upgrade pip", "升级pip")
    
    # 安装各种依赖
    steps = [
        (install_pytorch, "PyTorch"),
        (install_opencv, "OpenCV"),
        (install_whisper, "Whisper"),
        (install_other_dependencies, "其他依赖"),
        (download_whisper_model, "Whisper模型"),
        (verify_installation, "验证安装")
    ]
    
    failed_steps = []
    
    for step_func, step_name in steps:
        if not step_func():
            failed_steps.append(step_name)
    
    print("\n" + "=" * 50)
    
    if failed_steps:
        print("❌ 安装过程中出现错误:")
        for step in failed_steps:
            print(f"  - {step}")
        print("\n请检查错误信息并手动安装失败的依赖")
        sys.exit(1)
    else:
        print("🎉 所有依赖安装成功！")
        print("\n现在可以启动后端服务器:")
        print("cd video-learning-helper-backend")
        print("source venv/bin/activate  # 如果使用虚拟环境")
        print("python -m app.main_supabase")

if __name__ == "__main__":
    main() 
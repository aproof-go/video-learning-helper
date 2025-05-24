"""
应用配置文件
支持热更新和开发模式
"""

import os
from pathlib import Path
from typing import Optional

class Settings:
    """应用设置"""
    
    # 基本配置
    APP_NAME: str = "视频学习助手"
    VERSION: str = "2.0.0"
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    
    # 服务器配置
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    RELOAD: bool = os.getenv("RELOAD", "true").lower() == "true"
    
    # 数据库配置
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    
    # JWT配置
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # 文件上传配置
    UPLOAD_DIR: Path = Path("uploads")
    MAX_FILE_SIZE: int = 500 * 1024 * 1024  # 500MB
    ALLOWED_VIDEO_EXTENSIONS: set = {".mp4", ".avi", ".mov", ".mkv", ".wmv", ".flv"}
    
    # CORS配置
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:3001", 
        "http://localhost:3002",
        "http://localhost:3003",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002",
        "http://127.0.0.1:3003"
    ]
    
    # 任务处理配置
    MAX_CONCURRENT_TASKS: int = int(os.getenv("MAX_CONCURRENT_TASKS", "2"))
    TASK_TIMEOUT: int = int(os.getenv("TASK_TIMEOUT", "3600"))  # 1小时
    
    # 视频分析配置
    ENABLE_REAL_ANALYSIS: bool = os.getenv("ENABLE_REAL_ANALYSIS", "true").lower() == "true"
    FFMPEG_PATH: Optional[str] = os.getenv("FFMPEG_PATH")
    
    # 热更新配置
    WATCH_DIRS: list = ["app", "static", "templates"]
    WATCH_EXTENSIONS: list = [".py", ".html", ".css", ".js", ".tsx", ".ts"]
    
    def __init__(self):
        """初始化设置"""
        # 确保上传目录存在
        self.UPLOAD_DIR.mkdir(exist_ok=True)
        
        # 开发模式下的额外配置
        if self.DEBUG:
            self.RELOAD = True
            print(f"🔧 开发模式已启用")
            print(f"📁 上传目录: {self.UPLOAD_DIR.absolute()}")
            print(f"🔄 热更新: {'启用' if self.RELOAD else '禁用'}")
    
    @property
    def database_url(self) -> str:
        """获取数据库URL"""
        return self.SUPABASE_URL
    
    @property
    def is_production(self) -> bool:
        """是否为生产环境"""
        return not self.DEBUG

# 全局设置实例
settings = Settings()

# 环境变量检查
def check_environment():
    """检查必要的环境变量"""
    required_vars = []
    
    if not settings.SUPABASE_URL:
        required_vars.append("SUPABASE_URL")
    
    if not settings.SUPABASE_KEY:
        required_vars.append("SUPABASE_KEY")
    
    if required_vars:
        print(f"⚠️ 缺少环境变量: {', '.join(required_vars)}")
        print("请在 .env 文件中设置这些变量")
        return False
    
    return True

# 开发模式配置
def setup_development():
    """设置开发模式"""
    if settings.DEBUG:
        # 启用详细日志
        import logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # 打印配置信息
        print(f"🚀 {settings.APP_NAME} v{settings.VERSION}")
        print(f"🌐 服务器: http://{settings.HOST}:{settings.PORT}")
        print(f"📚 API文档: http://{settings.HOST}:{settings.PORT}/docs")
        print(f"🔄 热更新: {'启用' if settings.RELOAD else '禁用'}")
        print(f"🗄️ 数据库: {'Supabase' if settings.SUPABASE_URL else '内存'}")

# 热更新监控
def setup_hot_reload():
    """设置热更新监控"""
    if settings.RELOAD and settings.DEBUG:
        try:
            import watchdog
            print("🔥 热更新监控已启用")
            return True
        except ImportError:
            print("⚠️ 热更新需要安装 watchdog: pip install watchdog")
            return False
    return False 
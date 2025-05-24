"""
环境配置管理
支持测试、生产环境的数据库和存储分离
"""

import os
from pathlib import Path
from typing import Optional, Literal
from pydantic import BaseSettings, Field
from dotenv import load_dotenv

# 加载环境变量
load_dotenv("config.env")

Environment = Literal["development", "production"]

class Settings(BaseSettings):
    """应用设置"""
    
    # 环境配置
    node_env: Environment = Field(default="development", env="NODE_ENV")
    debug: bool = Field(default=True, env="DEBUG")
    
    # 服务器配置
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    reload: bool = Field(default=True, env="RELOAD")
    
    # JWT配置
    secret_key: str = Field(env="SECRET_KEY")
    algorithm: str = Field(default="HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # 文件上传配置
    upload_dir: Path = Field(default=Path("uploads"))
    max_file_size: int = Field(default=500 * 1024 * 1024)  # 500MB
    allowed_video_extensions: set = {".mp4", ".avi", ".mov", ".mkv", ".wmv", ".flv"}
    
    # 存储配置
    storage_provider: Literal["local", "supabase", "aws_s3"] = Field(default="local", env="STORAGE_PROVIDER")
    use_local_storage: bool = Field(default=True, env="USE_LOCAL_STORAGE")
    
    # 测试环境数据库配置（现有配置）
    supabase_url_dev: str = Field(env="SUPABASE_URL_DEV")
    supabase_key_dev: str = Field(env="SUPABASE_KEY_DEV")
    supabase_storage_bucket_dev: str = Field(default="video-learning-test", env="SUPABASE_STORAGE_BUCKET_DEV")
    
    # 生产环境数据库配置（ap-production 项目）
    supabase_url_prod: Optional[str] = Field(default=None, env=["SUPABASE_URL_PROD", "SUPABASE_URL_PRODUCTION"])
    supabase_key_prod: Optional[str] = Field(default=None, env=["SUPABASE_KEY_PROD", "SUPABASE_KEY_PRODUCTION"])
    supabase_storage_bucket_prod: str = Field(default="video-learning-prod", env=["SUPABASE_STORAGE_BUCKET_PROD", "SUPABASE_STORAGE_BUCKET_PRODUCTION"])
    
    # AWS S3 配置（备选方案）
    aws_access_key_id: Optional[str] = Field(default=None, env="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: Optional[str] = Field(default=None, env="AWS_SECRET_ACCESS_KEY")
    aws_region: str = Field(default="us-east-1", env="AWS_REGION")
    aws_s3_bucket_dev: str = Field(default="video-learning-test", env="AWS_S3_BUCKET_DEV")
    aws_s3_bucket_prod: str = Field(default="video-learning-prod", env="AWS_S3_BUCKET_PROD")
    
    # CORS配置
    cors_origins: list = [
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
    max_concurrent_tasks: int = Field(default=2, env="MAX_CONCURRENT_TASKS")
    task_timeout: int = Field(default=3600, env="TASK_TIMEOUT")
    
    # 视频分析配置
    enable_real_analysis: bool = Field(default=True, env="ENABLE_REAL_ANALYSIS")
    ffmpeg_path: Optional[str] = Field(default=None, env="FFMPEG_PATH")
    
    @property
    def supabase_url(self) -> str:
        """根据环境获取Supabase URL"""
        if self.node_env == "production":
            if not self.supabase_url_prod:
                raise ValueError("生产环境必须配置 SUPABASE_URL_PROD")
            return self.supabase_url_prod
        else:
            # 测试环境：使用现有配置
            return self.supabase_url_dev
    
    @property
    def supabase_key(self) -> str:
        """根据环境获取Supabase Key"""
        if self.node_env == "production":
            if not self.supabase_key_prod:
                raise ValueError("生产环境必须配置 SUPABASE_KEY_PROD")
            return self.supabase_key_prod
        else:
            # 测试环境：使用现有配置
            return self.supabase_key_dev
    
    @property
    def storage_bucket(self) -> str:
        """根据环境获取存储桶名称"""
        if self.storage_provider == "supabase":
            if self.node_env == "production":
                return self.supabase_storage_bucket_prod
            else:
                return self.supabase_storage_bucket_dev
        elif self.storage_provider == "aws_s3":
            if self.node_env == "production":
                return self.aws_s3_bucket_prod
            else:
                return self.aws_s3_bucket_dev
        else:
            return "local"
    
    @property
    def is_production(self) -> bool:
        """是否为生产环境"""
        return self.node_env == "production"
    
    @property
    def is_development(self) -> bool:
        """是否为测试环境（包括本地开发）"""
        return self.node_env == "development"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 确保上传目录存在
        self.upload_dir.mkdir(exist_ok=True)
        
        # 输出环境信息
        env_name = "生产环境" if self.is_production else "测试环境"
        print(f"🚀 启动环境: {env_name} ({self.node_env.upper()})")
        print(f"🗄️ 数据库: {self.supabase_url}")
        print(f"📦 存储方式: {self.storage_provider}")
        print(f"🪣 存储桶: {self.storage_bucket}")
        print(f"📁 上传目录: {self.upload_dir.absolute()}")
        
        if self.debug:
            print(f"🔧 调试模式已启用")

    class Config:
        env_file = "config.env"
        case_sensitive = False

# 全局设置实例
settings = Settings()

def get_settings() -> Settings:
    """获取配置实例"""
    return settings 
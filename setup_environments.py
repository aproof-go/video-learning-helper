#!/usr/bin/env python3
"""
环境设置脚本
帮助快速配置测试、生产环境
"""

import os
import json
from pathlib import Path
from typing import Dict, Any

def create_backend_config(env: str, config: Dict[str, Any]) -> None:
    """创建后端配置文件"""
    backend_dir = Path("video-learning-helper-backend")
    config_file = backend_dir / f"config.{env}.env"
    
    env_title = "测试环境" if env == 'development' else "生产环境"
    env_content = f"""# {env_title}配置
NODE_ENV={env}
DEBUG={'true' if env == 'development' else 'false'}
RELOAD={'true' if env == 'development' else 'false'}

# 服务器配置
HOST=0.0.0.0
PORT=8000

# 数据库配置
SUPABASE_URL_{env.upper()}={config['supabase_url']}
SUPABASE_KEY_{env.upper()}={config['supabase_key']}

# 存储配置
STORAGE_PROVIDER=supabase
USE_LOCAL_STORAGE={'true' if env == 'development' else 'false'}
SUPABASE_STORAGE_BUCKET_{env.upper()}={config['storage_bucket']}

# JWT配置
SECRET_KEY={config['jwt_secret']}
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 任务处理配置
MAX_CONCURRENT_TASKS=2
TASK_TIMEOUT=3600

# 视频分析配置
ENABLE_REAL_ANALYSIS=true
FFMPEG_PATH=/usr/local/bin/ffmpeg

# 文件上传配置
MAX_FILE_SIZE=536870912  # 512MB

# 热更新配置
WATCH_DIRS=app,static,templates
WATCH_EXTENSIONS=.py,.html,.css,.js,.tsx,.ts
"""
    
    config_file.write_text(env_content)
    print(f"✅ 创建后端配置: {config_file}")

def create_frontend_env(env: str, config: Dict[str, Any]) -> None:
    """创建前端环境变量文件"""
    frontend_dir = Path("video-learning-helper-frontend")
    
    if env == 'development':
        env_file = frontend_dir / ".env.local"
        env_content = f"""# 测试环境配置
NODE_ENV=development

# API配置
NEXT_PUBLIC_DEV_API_URL=http://localhost:8000

# Supabase配置（现有测试配置）
NEXT_PUBLIC_SUPABASE_URL_DEV={config['supabase_url']}
NEXT_PUBLIC_SUPABASE_ANON_KEY_DEV={config['supabase_key']}

# JWT 密钥
JWT_SECRET_KEY={config['jwt_secret']}
"""
        env_file.write_text(env_content)
        print(f"✅ 创建前端配置: {env_file}")
    else:
        # 为 Vercel 创建环境变量配置说明
        vercel_config = {
            f"NODE_ENV": env,
            f"NEXT_PUBLIC_SUPABASE_URL_PROD": config['supabase_url'],
            f"NEXT_PUBLIC_SUPABASE_ANON_KEY_PROD": config['supabase_key']
        }
        
        config_file = frontend_dir / f"vercel.{env}.env.json"
        with open(config_file, 'w') as f:
            json.dump(vercel_config, f, indent=2)
        
        print(f"✅ 创建 Vercel 环境配置: {config_file}")
        print(f"📋 请将以下环境变量添加到 Vercel Dashboard:")
        for key, value in vercel_config.items():
            print(f"   {key}={value}")

def create_database_migration_sql() -> None:
    """创建数据库迁移 SQL 文件"""
    sql_content = """-- 视频学习助手数据库结构
-- 适用于生产环境（ap-production 项目）

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    email VARCHAR NOT NULL UNIQUE,
    name VARCHAR,
    username VARCHAR(50) UNIQUE,
    password_hash VARCHAR NOT NULL,
    avatar_url TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- 视频表
CREATE TABLE IF NOT EXISTS videos (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    title VARCHAR NOT NULL,
    filename VARCHAR NOT NULL,
    file_size BIGINT NOT NULL,
    duration INTEGER,
    resolution_width INTEGER,
    resolution_height INTEGER,
    format VARCHAR(10),
    status VARCHAR(20) DEFAULT 'uploaded',
    file_url TEXT,
    thumbnail_url TEXT,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- 分析任务表
CREATE TABLE IF NOT EXISTS analysis_tasks (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    video_id UUID REFERENCES videos(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    video_segmentation BOOLEAN DEFAULT false,
    transition_detection BOOLEAN DEFAULT false,
    audio_transcription BOOLEAN DEFAULT false,
    report_generation BOOLEAN DEFAULT false,
    status VARCHAR(20) DEFAULT 'pending',
    progress VARCHAR(50) DEFAULT '0%',
    error_message TEXT,
    report_pdf_url TEXT,
    subtitle_srt_url TEXT,
    subtitle_vtt_url TEXT,
    script_md_url TEXT,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_videos_user_id ON videos(user_id);
CREATE INDEX IF NOT EXISTS idx_videos_created_at ON videos(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_analysis_tasks_video_id ON analysis_tasks(video_id);
CREATE INDEX IF NOT EXISTS idx_analysis_tasks_user_id ON analysis_tasks(user_id);
CREATE INDEX IF NOT EXISTS idx_analysis_tasks_status ON analysis_tasks(status);

-- 创建 RLS 策略 (可选)
-- ALTER TABLE users ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE videos ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE analysis_tasks ENABLE ROW LEVEL SECURITY;

-- 用户只能访问自己的数据
-- CREATE POLICY "Users can view own data" ON users FOR SELECT USING (auth.uid() = id);
-- CREATE POLICY "Videos policy" ON videos FOR ALL USING (auth.uid() = user_id);
-- CREATE POLICY "Tasks policy" ON analysis_tasks FOR ALL USING (auth.uid() = user_id);
"""
    
    sql_file = Path("production_database_migration.sql")
    sql_file.write_text(sql_content)
    print(f"✅ 创建生产环境数据库迁移文件: {sql_file}")

def main():
    """主函数"""
    print("🔧 视频学习助手环境设置脚本")
    print("=" * 50)
    
    # 环境配置
    environments = {
        'development': {
            'supabase_url': 'https://tjxqzmrmybrcmkflaimq.supabase.co',
            'supabase_key': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRqeHF6bXJteWJyY21rZmxhaW1xIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDgwMTQ2NDIsImV4cCI6MjA2MzU5MDY0Mn0.uOYYkrZP2VFLwNkoU96Qo94A5oh9wJbTIlGnChH2pCg',
            'storage_bucket': 'video-learning-test',
            'jwt_secret': 'test-jwt-secret-key-change-this-2024'
        },
        'production': {
            'supabase_url': 'https://your-ap-production-project.supabase.co',
            'supabase_key': 'your-ap-production-anon-key',
            'storage_bucket': 'video-learning-prod',
            'jwt_secret': 'super-secure-production-jwt-key-2024'
        }
    }
    
    # 创建目录
    Path("video-learning-helper-backend").mkdir(exist_ok=True)
    Path("video-learning-helper-frontend").mkdir(exist_ok=True)
    
    # 为每个环境创建配置
    for env, config in environments.items():
        env_name = "测试环境" if env == 'development' else "生产环境"
        print(f"\n📁 设置 {env_name}:")
        create_backend_config(env, config)
        create_frontend_env(env, config)
    
    # 创建数据库迁移文件
    print(f"\n📄 创建数据库迁移文件:")
    create_database_migration_sql()
    
    print(f"\n✅ 环境设置完成!")
    print(f"\n📋 两环境配置说明:")
    print(f"🧪 测试环境 (development): 继续使用现有 Supabase 项目")
    print(f"🚀 生产环境 (production): 需要创建 ap-production 项目")
    
    print(f"\n📋 后续步骤:")
    print(f"1. 创建 ap-production Supabase 项目")
    print(f"2. 在 ap-production 项目中执行 production_database_migration.sql")
    print(f"3. 在 ap-production 项目中创建 video-learning-prod 存储桶")
    print(f"4. 更新生产环境配置文件中的实际 URL 和密钥")
    print(f"5. 在 Vercel 中配置生产环境变量")
    
    print(f"\n🔍 验证环境:")
    print(f"测试环境: python -m uvicorn app.main_supabase:app --reload")
    print(f"前端开发: npm run dev")

if __name__ == "__main__":
    main() 
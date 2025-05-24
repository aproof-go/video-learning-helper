-- 视频学习助手数据库结构
-- 适用于测试和生产环境

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

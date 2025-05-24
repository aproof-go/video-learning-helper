# 🔧 环境配置指南

## 📋 环境变量配置

### 1. **API配置**

#### 开发环境 (.env.local)
```bash
# 本地开发时的API配置
NEXT_PUBLIC_DEV_API_URL=http://localhost:8000
NODE_ENV=development

# 开发数据库 (测试库)
NEXT_PUBLIC_SUPABASE_URL=https://tjxqzmrmybrcmkflaimq.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### 生产环境 (Vercel环境变量)
```bash
# 生产环境自动使用当前域名，无需配置NEXT_PUBLIC_API_URL

# 生产数据库 (独立库)
NEXT_PUBLIC_SUPABASE_URL=https://your-prod-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-prod-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-prod-service-role-key
```

## 🏗 **创建生产环境数据库**

### 步骤1: 创建新的Supabase项目
1. 访问 [Supabase Dashboard](https://supabase.com/dashboard)
2. 点击 "New Project"
3. 项目名称: `video-learning-helper-production`
4. 选择区域 (建议: US East 或 Asia Pacific)

### 步骤2: 迁移数据库结构
```sql
-- 用户表
CREATE TABLE users (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  email VARCHAR NOT NULL UNIQUE,
  name VARCHAR,
  username VARCHAR(50) UNIQUE,
  password_hash VARCHAR NOT NULL,
  avatar_url TEXT,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- 其他表结构...
```

## 📁 **本地开发配置**

### 创建 `.env.local` 文件
```bash
# 复制到 video-learning-helper-frontend/.env.local
NEXT_PUBLIC_DEV_API_URL=http://localhost:8000
NODE_ENV=development

# 使用测试数据库
NEXT_PUBLIC_SUPABASE_URL=https://tjxqzmrmybrcmkflaimq.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRqeHF6bXJteWJyY21rZmxhaW1xIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDgwMTQ2NDIsImV4cCI6MjA2MzU5MDY0Mn0.uOYYkrZP2VFLwNkoU96Qo94A5oh9wJbTIlGnChH2pCg
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRqeHF6bXJteWJyY21rZmxhaW1xIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0ODAxNDY0MiwiZXhwIjoyMDYzNTkwNjQyfQ.1f141AbRK3Oz9zDnfCh30PdO9Oy-T_UcBN9wSTGfp6c

JWT_SECRET_KEY=dev-jwt-secret-key-change-in-production
```

## 🚀 **Vercel生产环境配置**

### 环境变量设置
在Vercel Dashboard → Project Settings → Environment Variables 中添加：

```bash
NEXT_PUBLIC_SUPABASE_URL=https://prod-project-id.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=prod-anon-key
SUPABASE_SERVICE_ROLE_KEY=prod-service-role-key
JWT_SECRET_KEY=super-secure-production-jwt-key
OPENAI_API_KEY=sk-your-openai-api-key
``` 
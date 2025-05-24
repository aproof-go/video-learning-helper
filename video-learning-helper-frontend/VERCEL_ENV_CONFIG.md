# Vercel 环境变量配置说明

## 必需的环境变量

在Vercel项目设置中添加以下环境变量：

### 1. Supabase配置
```
NEXT_PUBLIC_SUPABASE_URL=https://tjxqzmrmybrcmkflaimq.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRqeHF6bXJteWJyY21rZmxhaW1xIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTY0ODI3MDQsImV4cCI6MjAzMjA1ODcwNH0.OPa2DfkTSSNjOzFGPLHDpz1bpWqNdcxgKFaOtj_8zsg
```

### 2. 服务器端Supabase配置
**需要获取Supabase项目的Service Role Key**
```
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

### 3. JWT配置
```
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
```

### 4. OpenAI配置（用于AI分析）
```
OPENAI_API_KEY=your-openai-api-key
```

## 获取Service Role Key步骤：

1. 访问 https://supabase.com/dashboard
2. 选择项目：tjxqzmrmybrcmkflaimq
3. 前往 Settings → API
4. 复制 "service_role" key（不是anon key）
5. 在Vercel项目设置中添加 SUPABASE_SERVICE_ROLE_KEY

## 获取OpenAI API Key步骤：

1. 访问 https://platform.openai.com/api-keys
2. 创建新的API密钥
3. 在Vercel项目设置中添加 OPENAI_API_KEY

## 本地开发环境变量

创建 `.env.local` 文件（已在 .gitignore 中）：

```bash
# 复制所有上述环境变量到此文件
NEXT_PUBLIC_SUPABASE_URL=https://tjxqzmrmybrcmkflaimq.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=...
SUPABASE_SERVICE_ROLE_KEY=...
JWT_SECRET_KEY=...
OPENAI_API_KEY=...
``` 
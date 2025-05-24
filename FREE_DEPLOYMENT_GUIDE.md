# 🆓 完全免费部署指南

## 🎯 100%免费的部署方案

由于Railway已开始收费，这里提供完全免费的替代方案：

### 方案A：Vercel + Supabase Edge Functions（推荐）

**成本：完全免费**
**优点：无需后端服务器，全部serverless**

#### 1. 将后端逻辑移植到Supabase Edge Functions

```typescript
// supabase/functions/video-upload/index.ts
import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

serve(async (req) => {
  const supabase = createClient(
    Deno.env.get('SUPABASE_URL') ?? '',
    Deno.env.get('SUPABASE_ANON_KEY') ?? ''
  )
  
  // 处理视频上传逻辑
  if (req.method === 'POST') {
    // 视频上传处理
    const formData = await req.formData()
    const file = formData.get('video') as File
    
    // 存储到Supabase Storage
    const { data, error } = await supabase.storage
      .from('videos')
      .upload(`videos/${Date.now()}_${file.name}`, file)
    
    return new Response(JSON.stringify({ data, error }), {
      headers: { 'Content-Type': 'application/json' }
    })
  }
  
  return new Response('Hello from Edge Function!')
})
```

#### 2. 部署步骤

1. **前端部署到Vercel**（免费）
2. **后端逻辑使用Supabase Edge Functions**（免费）
3. **数据库使用Supabase**（免费500MB）
4. **文件存储使用Supabase Storage**（免费1GB）

---

### 方案B：Vercel + PlanetScale（推荐）

**成本：完全免费**
**优点：MySQL数据库，性能更好**

#### 后端部署到Vercel API Routes

```typescript
// pages/api/videos/upload.ts
import { NextApiRequest, NextApiResponse } from 'next'
import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient()

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method === 'POST') {
    // 处理视频上传
    try {
      const video = await prisma.video.create({
        data: req.body
      })
      res.json(video)
    } catch (error) {
      res.status(500).json({ error: 'Upload failed' })
    }
  }
}
```

---

### 方案C：Netlify + Supabase（最稳定）

**成本：完全免费**
**优点：CI/CD最稳定，构建速度快**

#### 1. 前端部署到Netlify
- 免费额度：100GB带宽/月
- 自动SSL证书
- 全球CDN

#### 2. 后端使用Netlify Functions
```javascript
// netlify/functions/video-upload.js
exports.handler = async (event, context) => {
  const { httpMethod, body } = event
  
  if (httpMethod === 'POST') {
    // 处理视频上传
    const data = JSON.parse(body)
    
    // 连接Supabase
    const { createClient } = require('@supabase/supabase-js')
    const supabase = createClient(
      process.env.SUPABASE_URL,
      process.env.SUPABASE_KEY
    )
    
    // 保存到数据库
    const { data: video, error } = await supabase
      .from('videos')
      .insert(data)
    
    return {
      statusCode: 200,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ video, error })
    }
  }
}
```

---

### 方案D：GitHub Pages + GitHub Actions（纯静态）

**成本：完全免费**
**适合：展示型项目**

#### 转换为纯前端应用
1. 使用GitHub Actions自动构建
2. 部署到GitHub Pages
3. 后端功能通过第三方API实现

---

## 🚀 推荐实施方案：Vercel全栈部署

基于你的项目，我推荐将整个应用迁移到Vercel全栈：

### 1. 重构后端为Vercel API Routes

```bash
# 新的目录结构
video-learning-helper/
├── pages/
│   └── api/
│       ├── auth/
│       ├── videos/
│       └── analysis/
├── components/
├── lib/
└── public/
```

### 2. 一键部署命令

```bash
# 克隆并部署
npx create-next-app --example with-supabase video-helper
cd video-helper
vercel --prod
```

### 3. 环境变量配置

```bash
# 在Vercel中设置
SUPABASE_URL=your-supabase-url
SUPABASE_ANON_KEY=your-supabase-key
NEXT_PUBLIC_SUPABASE_URL=your-supabase-url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-supabase-key
```

---

## 🎯 立即行动方案

### 选择1：快速迁移到Vercel全栈
```bash
# 1. 修改项目结构
# 2. 将FastAPI路由转换为Next.js API Routes
# 3. 一键部署到Vercel
```

### 选择2：保持现有架构，使用免费后端
```bash
# 1. 后端部署到Render.com（免费）
# 2. 前端部署到Vercel
# 3. 数据库使用Supabase
```

### 选择3：完全Serverless
```bash
# 1. 使用Supabase Edge Functions
# 2. 前端部署到Vercel
# 3. 所有后端逻辑移到Edge Functions
```

---

## 💡 立即开始

想要哪种方案？我可以帮你立即实施：

1. **Vercel全栈**（推荐） - 5分钟完成
2. **Render + Vercel** - 10分钟完成  
3. **Netlify全栈** - 8分钟完成

选择一个，我们立即开始迁移！ 
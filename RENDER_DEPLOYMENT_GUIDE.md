# 🚀 Render.com 免费部署指南

## 🎯 为什么选择Render.com？

- ✅ **完全免费**：每月750小时免费额度
- ✅ **零配置**：自动SSL、CDN、监控
- ✅ **简单易用**：比Heroku更简单
- ✅ **稳定可靠**：99.99%在线时间

---

## 📋 具体部署步骤

### 步骤1：准备代码

已经为你修复了依赖问题：
- 移除了有问题的 `whisper-openai` 包
- 创建了 `requirements-minimal.txt` 专用于部署
- 配置了 `render.yaml` 自动部署文件

### 步骤2：部署后端到Render

1. **打开浏览器，访问：** https://render.com
2. **GitHub登录**
3. **点击 "New +"**
4. **选择 "Web Service"**
5. **连接GitHub仓库：** `video-learning-helper`
6. **填写配置：**
   ```
   Name: video-learning-helper-backend
   Region: Ohio (US East)
   Branch: main
   Root Directory: video-learning-helper-backend
   Runtime: Python 3
   Build Command: pip install -r requirements-minimal.txt
   Start Command: uvicorn app.main_supabase:app --host 0.0.0.0 --port $PORT
   ```

7. **添加环境变量：**
   ```
   SUPABASE_URL=你的Supabase项目URL
   SUPABASE_KEY=你的Supabase匿名密钥
   JWT_SECRET_KEY=随便输入一个长密码
   ```

8. **点击 "Create Web Service"**

### 步骤3：等待部署完成

- 部署时间：通常3-5分钟
- 状态查看：在Render面板实时查看日志
- 成功标志：显示 "Live" 状态

### 步骤4：获取后端URL

部署成功后，你会得到一个URL：
```
https://video-learning-helper-backend-xxxx.onrender.com
```

### 步骤5：部署前端到Vercel

1. **访问：** https://vercel.com
2. **Import Project**
3. **选择仓库：** `video-learning-helper`
4. **配置：**
   ```
   Framework: Next.js
   Root Directory: video-learning-helper-frontend
   Build Command: npm run build
   Output Directory: .next
   ```
5. **环境变量：**
   ```
   NEXT_PUBLIC_API_URL=https://video-learning-helper-backend-xxxx.onrender.com
   ```
6. **Deploy**

---

## 🎉 完成！

现在你的应用已经完全部署到公网：

- **前端地址：** https://your-project.vercel.app
- **后端地址：** https://video-learning-helper-backend-xxxx.onrender.com
- **数据库：** Supabase（免费）

## 📊 免费额度说明

### Render.com
- **CPU时间：** 每月750小时（约31天）
- **内存：** 512MB
- **存储：** 1GB SSD
- **带宽：** 100GB/月
- **睡眠时间：** 15分钟无活动后休眠

### Vercel
- **部署：** 无限次
- **带宽：** 100GB/月
- **函数执行：** 100GB-hrs/月
- **团队成员：** 1个

### Supabase
- **数据库：** 500MB PostgreSQL
- **存储：** 1GB 文件存储
- **带宽：** 2GB/月
- **认证：** 50,000 MAU

---

## 🔧 常见问题

### Q: 应用休眠怎么办？
A: Render免费版15分钟无活动会休眠，第一次访问需要30秒启动

### Q: 如何保持应用活跃？
A: 可以使用定时器服务每10分钟ping一次你的应用

### Q: 部署失败怎么办？
A: 查看Render部署日志，通常是依赖或环境变量问题

### Q: 如何更新应用？
A: 推送代码到GitHub main分支，Render会自动重新部署

---

## 🚀 立即开始

现在就开始部署：

1. **检查代码更新**
2. **访问 render.com 开始部署**
3. **按照上述步骤操作**
4. **10分钟后享受你的公网应用！**

**预计总时间：10-15分钟**
**总成本：完全免费** 
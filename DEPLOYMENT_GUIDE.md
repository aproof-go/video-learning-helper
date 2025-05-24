# 🚀 视频学习助手 - 公网部署指南

## 📋 部署方案对比

| 方案 | 成本 | 难度 | 部署时间 | 推荐指数 |
|------|------|------|----------|----------|
| Vercel + Railway | 免费 | ⭐⭐ | 10分钟 | ⭐⭐⭐⭐⭐ |
| GitHub Actions自动部署 | 免费 | ⭐ | 5分钟 | ⭐⭐⭐⭐⭐ |
| VPS Docker | $5-20/月 | ⭐⭐⭐ | 30分钟 | ⭐⭐⭐⭐ |

---

## 🎯 方案一：一键自动部署（推荐）

### 前提条件
- GitHub仓库已配置
- 有GitHub账号

### 步骤

#### 1. 配置GitHub Secrets
进入你的GitHub仓库 → Settings → Secrets and variables → Actions

添加以下Secrets：

```bash
# Supabase配置
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
JWT_SECRET_KEY=your-jwt-secret

# Vercel配置（可选）
VERCEL_TOKEN=your-vercel-token
VERCEL_ORG_ID=your-org-id  
VERCEL_PROJECT_ID=your-project-id

# Railway配置（可选）
RAILWAY_TOKEN=your-railway-token
RAILWAY_PROJECT_ID=your-project-id

# Docker Hub配置（可选）
DOCKER_USERNAME=your-docker-username
DOCKER_PASSWORD=your-docker-password
```

#### 2. 自动部署
```bash
# 运行部署脚本
./deploy.sh

# 选择 "1" - 自动部署
```

#### 3. 查看部署状态
访问：https://github.com/aproof-go/video-learning-helper/actions

---

## 🎯 方案二：手动部署到免费平台

### A. 后端部署到Railway

1. **注册Railway账号**
   - 访问：https://railway.app
   - 使用GitHub登录

2. **创建新项目**
   ```bash
   # 在Railway面板中：
   New Project → Deploy from GitHub repo → 选择你的仓库
   ```

3. **配置后端服务**
   ```bash
   # 选择 video-learning-helper-backend 目录
   # 设置环境变量：
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your-anon-key
   JWT_SECRET_KEY=your-jwt-secret
   ```

4. **获取后端域名**
   ```bash
   # 部署完成后，Railway会给你一个域名如：
   # https://your-app-name.railway.app
   ```

### B. 前端部署到Vercel

1. **注册Vercel账号**
   - 访问：https://vercel.com
   - 使用GitHub登录

2. **导入项目**
   ```bash
   # 在Vercel面板中：
   New Project → Import Git Repository → 选择你的仓库
   ```

3. **配置构建设置**
   ```bash
   Framework Preset: Next.js
   Root Directory: video-learning-helper-frontend
   Build Command: npm run build
   Output Directory: .next
   Install Command: npm ci
   ```

4. **设置环境变量**
   ```bash
   NEXT_PUBLIC_API_URL=https://your-railway-domain.railway.app
   ```

5. **部署**
   点击Deploy按钮，等待部署完成

---

## 🎯 方案三：VPS部署（完全控制）

### 前提条件
- 有VPS服务器（推荐：DigitalOcean、Vultr、腾讯云）
- 已安装Docker和Docker Compose

### 步骤

#### 1. 准备服务器
```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.21.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### 2. 部署项目
```bash
# 克隆项目
git clone https://github.com/aproof-go/video-learning-helper.git
cd video-learning-helper

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的配置

# 启动服务
docker-compose up -d

# 查看状态
docker-compose ps
```

#### 3. 配置域名和SSL（可选）
```bash
# 安装Nginx
sudo apt install nginx -y

# 配置反向代理
sudo nano /etc/nginx/sites-available/video-helper

# 添加以下配置：
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# 启用配置
sudo ln -s /etc/nginx/sites-available/video-helper /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# 安装SSL证书（可选）
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

---

## ⚡ 快速开始（推荐新手）

### 选择最简单的部署方式：

1. **Fork这个项目到你的GitHub**

2. **配置Supabase**
   - 注册Supabase账号：https://supabase.com
   - 创建新项目
   - 获取URL和Key

3. **一键部署前端到Vercel**
   ```bash
   # 访问这个链接，直接部署：
   https://vercel.com/new/clone?repository-url=https://github.com/your-username/video-learning-helper&project-name=video-learning-helper&root-directory=video-learning-helper-frontend
   ```

4. **一键部署后端到Railway**
   ```bash
   # 访问这个链接，直接部署：
   https://railway.app/new/template?template=https://github.com/your-username/video-learning-helper&plugins=postgresql&envs=SUPABASE_URL,SUPABASE_KEY,JWT_SECRET_KEY
   ```

---

## 🔧 部署后配置

### 1. 测试部署
```bash
# 测试后端
curl https://your-railway-domain.railway.app/health

# 测试前端
curl https://your-vercel-domain.vercel.app
```

### 2. 数据库迁移
```bash
# 如果需要初始化数据库表，运行：
python video-learning-helper-backend/migrate_test_data_to_supabase.py
```

### 3. 配置文件上传
确保在Supabase中配置存储桶权限。

---

## 📊 费用说明

### 免费方案
- **Vercel**: 每月100GB带宽，无限部署
- **Railway**: 每月$5免费额度，足够小项目
- **Supabase**: 500MB数据库，50MB文件存储

### 付费升级（如需要）
- **Vercel Pro**: $20/月，更多带宽和功能
- **Railway**: 按使用量付费，通常$5-20/月
- **Supabase Pro**: $25/月，更大存储和更多功能

---

## ❓ 常见问题

### Q: 部署失败怎么办？
A: 查看GitHub Actions日志，或检查环境变量配置

### Q: 如何更新部署？
A: 推送代码到main分支即可自动更新

### Q: 如何查看日志？
A: 
- Vercel: 在Vercel面板查看
- Railway: 在Railway面板查看
- VPS: `docker-compose logs`

### Q: 文件上传失败？
A: 检查Supabase存储配置和权限设置

---

## 🆘 获取帮助

遇到问题？
1. 查看项目README
2. 检查GitHub Issues
3. 查看CI/CD日志
4. 联系项目维护者

**祝你部署成功！** 🎉 
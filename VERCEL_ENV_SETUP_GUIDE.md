# 🔧 Vercel环境变量配置指南

## 📍 您的部署信息
- **Vercel URL**: https://video-learning-helper-iliqc4wiq-aproof-gos-projects.vercel.app/
- **Supabase项目**: video-learning-helper-backend (tjxqzmrmybrcmkflaimq)

## ⚙️ 必需的环境变量

请在 [Vercel控制台](https://vercel.com/dashboard) 中配置以下环境变量：

### 1. Supabase配置
```bash
NEXT_PUBLIC_SUPABASE_URL=https://tjxqzmrmybrcmkflaimq.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRqeHF6bXJteWJyY21rZmxhaW1xIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDgwMTQ2NDIsImV4cCI6MjA2MzU5MDY0Mn0.uOYYkrZP2VFLwNkoU96Qo94A5oh9wJbTIlGnChH2pCg
```

### 2. JWT配置
```bash
JWT_SECRET_KEY=your-super-secret-jwt-key-here-change-me
```

### 3. 服务角色密钥 (需要从Supabase获取)
```bash
SUPABASE_SERVICE_ROLE_KEY=获取方法见下方
```

## 📋 配置步骤

### 步骤1: 登录Vercel控制台
1. 访问 [vercel.com/dashboard](https://vercel.com/dashboard)
2. 找到 `video-learning-helper` 项目
3. 点击项目名称进入详情页

### 步骤2: 配置环境变量
1. 点击 **Settings** 标签
2. 选择左侧菜单的 **Environment Variables**
3. 添加上述所有环境变量

### 步骤3: 获取服务角色密钥
1. 访问 [Supabase控制台](https://supabase.com/dashboard)
2. 选择 `video-learning-helper-backend` 项目
3. 点击左侧菜单的 **Settings** → **API**
4. 在 "Project API keys" 部分找到 **service_role** 密钥
5. 复制并添加到Vercel环境变量

### 步骤4: 重新部署
配置完环境变量后，Vercel会自动重新部署应用。

## 🧪 测试URL

配置完成后，测试以下端点：

- **健康检查**: https://video-learning-helper-iliqc4wiq-aproof-gos-projects.vercel.app/api/health
- **用户注册**: https://video-learning-helper-iliqc4wiq-aproof-gos-projects.vercel.app/register
- **用户登录**: https://video-learning-helper-iliqc4wiq-aproof-gos-projects.vercel.app/login
- **视频页面**: https://video-learning-helper-iliqc4wiq-aproof-gos-projects.vercel.app/videos

## 🎯 预期结果

配置正确后，您应该看到：
- ✅ 健康检查返回 `{"status": "healthy", "timestamp": "..."}`
- ✅ 注册/登录页面正常显示
- ✅ 可以创建新用户账户
- ✅ 可以上传和分析视频

## 🔧 故障排除

如果遇到问题：
1. 检查Vercel部署日志是否有错误
2. 确认所有环境变量都已正确设置
3. 检查Supabase项目是否处于活动状态
4. 测试数据库连接

---

**下一步**: 配置完成后，请告诉我测试结果！ 
# ✅ 快速部署检查清单

## 🎯 目标：10分钟内让你的应用上线

### 准备工作 (2分钟)
- [ ] 确保有GitHub账号
- [ ] 确保有Supabase项目（如果没有，去 https://supabase.com 创建）
- [ ] 获取Supabase URL和Key

### 步骤1：部署后端到Railway (3分钟)

1. [ ] 打开 https://railway.app
2. [ ] 点击 "Login with GitHub"
3. [ ] 点击 "New Project"
4. [ ] 选择 "Deploy from GitHub repo"
5. [ ] 找到并选择 `video-learning-helper` 仓库
6. [ ] 🚨 **重要**：在配置页面，设置 Root Directory 为 `video-learning-helper-backend`
7. [ ] 添加环境变量：
   ```
   SUPABASE_URL=你的Supabase URL
   SUPABASE_KEY=你的Supabase Key  
   JWT_SECRET_KEY=随便输入一个密码
   ```
8. [ ] 点击 "Deploy"
9. [ ] 等待部署完成（通常1-2分钟）
10. [ ] 复制Railway给你的域名（形如：https://xxx.railway.app）

### 步骤2：部署前端到Vercel (3分钟)

1. [ ] 打开 https://vercel.com
2. [ ] 点击 "Continue with GitHub"
3. [ ] 点击 "New Project"
4. [ ] 找到并选择 `video-learning-helper` 仓库
5. [ ] 🚨 **重要**：配置构建设置：
   ```
   Framework Preset: Next.js
   Root Directory: video-learning-helper-frontend
   Build Command: npm run build
   Output Directory: .next
   ```
6. [ ] 添加环境变量：
   ```
   NEXT_PUBLIC_API_URL=你在步骤1中获得的Railway域名
   ```
7. [ ] 点击 "Deploy"
8. [ ] 等待部署完成（通常2-3分钟）
9. [ ] 复制Vercel给你的域名（形如：https://yyy.vercel.app）

### 步骤3：测试访问 (2分钟)

1. [ ] 访问你的Vercel域名
2. [ ] 检查页面是否正常加载
3. [ ] 尝试注册/登录功能
4. [ ] 尝试上传视频功能
5. [ ] 如果有问题，查看浏览器控制台错误信息

## 🎉 完成！

恭喜！你的应用现在已经在公网上运行了！

**你的应用地址：** https://你的vercel域名.vercel.app

## 🔧 如果遇到问题

### 常见问题及解决方案：

1. **部署失败**
   - 检查环境变量是否正确设置
   - 查看部署日志中的错误信息

2. **前端无法连接后端**
   - 确保 `NEXT_PUBLIC_API_URL` 环境变量正确
   - 检查Railway后端是否正常运行

3. **数据库连接失败**
   - 验证Supabase URL和Key是否正确
   - 检查Supabase项目是否激活

4. **文件上传失败**
   - 配置Supabase存储桶
   - 检查文件大小限制

## 📞 获取帮助

如果按照清单操作仍有问题，请：
1. 检查GitHub仓库的Issues页面
2. 查看部署平台的日志
3. 确认所有环境变量都已正确设置

**记住**：Railway和Vercel都有免费额度，足够个人使用！ 
# 🔧 Vercel环境变量配置指南

## 必需的环境变量

在Vercel项目的Settings → Environment Variables中添加以下变量：

### 1. Supabase配置
```bash
# Supabase项目URL (Public)
NEXT_PUBLIC_SUPABASE_URL=https://tjxqzmrmybrcmkflaimq.supabase.co

# Supabase匿名公钥 (Public)
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key_here

# Supabase服务端密钥 (Secret)
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here
```

### 2. JWT配置
```bash
# JWT密钥 (Secret)
JWT_SECRET=your-super-secret-jwt-key-at-least-32-characters-long
```

### 3. 应用配置
```bash
# 前端URL (自动设置，但可以手动覆盖)
NEXT_PUBLIC_APP_URL=https://your-domain.vercel.app

# 环境标识 (可选)
NODE_ENV=production
```

## 📋 配置步骤

### 1. 获取Supabase密钥
1. 登录 [Supabase Dashboard](https://supabase.com/dashboard)
2. 选择你的项目: `tjxqzmrmybrcmkflaimq`
3. 前往 Settings → API
4. 复制以下值:
   - `URL`: 作为 `NEXT_PUBLIC_SUPABASE_URL`
   - `anon public`: 作为 `NEXT_PUBLIC_SUPABASE_ANON_KEY`
   - `service_role`: 作为 `SUPABASE_SERVICE_ROLE_KEY`

### 2. 生成JWT密钥
```bash
# 使用Node.js生成随机密钥
node -e "console.log(require('crypto').randomBytes(64).toString('hex'))"
```

### 3. 在Vercel中配置
1. 访问 [Vercel Dashboard](https://vercel.com/dashboard)
2. 选择你的项目
3. 前往 Settings → Environment Variables
4. 添加上述环境变量
5. 设置适当的环境 (Production, Preview, Development)

## ⚠️ 重要注意事项

1. **密钥安全**: 
   - `SUPABASE_SERVICE_ROLE_KEY` 和 `JWT_SECRET` 必须设置为 Secret
   - 只有 `NEXT_PUBLIC_*` 变量可以设置为 Public

2. **环境分离**:
   - Production: 使用生产环境的Supabase项目
   - Preview: 可以使用相同的配置或单独的开发项目
   - Development: 本地开发配置

3. **重新部署**:
   - 添加环境变量后需要重新部署才能生效

## 🧪 测试部署

配置完成后，测试以下端点：

```bash
# 健康检查
curl https://your-domain.vercel.app/api/health

# 用户API (需要认证)
curl https://your-domain.vercel.app/api/v1/videos

# 预期响应: 401 未授权 (正常，因为没有提供token)
```

## 🔍 故障排除

### 常见错误:
1. **"Invalid API key"**: 检查Supabase密钥配置
2. **"CORS error"**: 已在vercel.json中配置，应该自动解决
3. **"Function timeout"**: API函数已设置30秒超时

### 日志查看:
1. Vercel Dashboard → Functions → 查看实时日志
2. 每个API调用的详细日志都会显示在这里 
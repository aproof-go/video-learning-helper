# 视频学习助手环境配置指南

## 📖 概述

本项目配置为两个环境：

- **🧪 测试环境** (development): 使用现有 Supabase 项目 (tjxqzmrmybrcmkflaimq)
- **🚀 生产环境** (production): 使用独立的 ap-production 项目

## 🛠️ 环境配置

### 测试环境（Development）
- 数据库：现有 Supabase 项目 `tjxqzmrmybrcmkflaimq.supabase.co`
- 存储：本地存储 + Supabase Storage `video-learning-test` 桶
- 用于：本地开发、功能测试、集成测试

### 生产环境（Production）
- 数据库：独立的 ap-production Supabase 项目
- 存储：Supabase Storage `video-learning-prod` 桶
- 用于：正式生产部署

## 🚀 快速开始

### 1. 生成配置文件

```bash
python setup_environments.py
```

这会生成：
- `video-learning-helper-backend/config.development.env`
- `video-learning-helper-backend/config.production.env`
- `video-learning-helper-frontend/.env.local`
- `video-learning-helper-frontend/vercel.production.env.json`
- `production_database_migration.sql`

### 2. 设置生产环境

#### 创建 ap-production Supabase 项目

1. 访问 [Supabase Dashboard](https://supabase.com/dashboard)
2. 创建新项目，命名为 "ap-production"
3. 记录项目 URL 和 anon key

#### 初始化生产数据库

```sql
-- 在 ap-production 项目的 SQL Editor 中执行
-- 内容来自 production_database_migration.sql 文件
```

#### 创建存储桶

在 ap-production 项目中：
1. 进入 Storage 页面
2. 创建名为 `video-learning-prod` 的桶
3. 设置为 public（用于文件访问）

#### 更新生产配置

编辑 `video-learning-helper-backend/config.production.env`：

```env
# 更新为实际的 ap-production 项目信息
SUPABASE_URL_PROD=https://your-actual-ap-production-ref.supabase.co
SUPABASE_KEY_PROD=your-actual-ap-production-anon-key
```

### 3. 本地测试环境运行

```bash
# 后端
cd video-learning-helper-backend
python -m uvicorn app.main_supabase:app --reload

# 前端
cd video-learning-helper-frontend
npm run dev
```

## 🌐 Vercel 部署

### 生产环境变量

在 Vercel Dashboard 中设置以下环境变量：

```
NODE_ENV=production
NEXT_PUBLIC_SUPABASE_URL_PROD=https://your-ap-production-ref.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY_PROD=your-ap-production-anon-key
```

### 部署流程

1. **测试部署** (`preview` 分支):
   - 使用 development 配置
   - 连接现有测试数据库

2. **生产部署** (`main` 分支):
   - 使用 production 配置
   - 连接 ap-production 数据库

## 📂 文件结构

```
video-learning-helper/
├── video-learning-helper-backend/
│   ├── config.development.env      # 测试环境配置
│   ├── config.production.env       # 生产环境配置
│   └── app/core/config.py          # 配置管理模块
├── video-learning-helper-frontend/
│   ├── .env.local                  # 本地开发配置
│   ├── vercel.production.env.json  # Vercel 生产配置
│   └── lib/api.ts                  # API 配置
├── production_database_migration.sql  # 生产数据库初始化
└── SIMPLE_ENVIRONMENT_GUIDE.md    # 本指南
```

## 🔧 环境切换逻辑

### 前端环境检测

```typescript
const getEnvironment = (): 'development' | 'production' => {
  if (process.env.VERCEL_ENV === 'production') return 'production';
  if (process.env.NODE_ENV === 'production') return 'production';
  return 'development';
};
```

### 后端环境检测

```python
@property
def supabase_url(self) -> str:
    if self.node_env == "production":
        return self.supabase_url_prod  # ap-production 项目
    else:
        return self.supabase_url_dev   # 现有测试项目
```

## 🎯 使用场景

| 环境 | 用途 | 数据库 | 存储 | 部署位置 |
|------|------|--------|------|----------|
| 测试 | 开发、测试 | tjxqzmrmybrcmkflaimq | 本地/测试桶 | 本地/Vercel Preview |
| 生产 | 正式服务 | ap-production | 生产桶 | Vercel Production |

## 🚨 注意事项

1. **数据隔离**: 生产和测试环境数据完全分离
2. **密钥安全**: 生产环境密钥不要提交到代码库
3. **存储分离**: 文件上传到不同的存储桶
4. **环境变量**: Vercel 中正确配置生产环境变量

## 🔍 验证部署

### 测试环境验证

```bash
curl http://localhost:8000/api/health
```

应返回现有测试数据库信息。

### 生产环境验证

部署后访问生产域名 `/api/health`，应返回 ap-production 数据库信息。

## ❓ 故障排除

### 常见问题

1. **Linter 错误**: 已修复 NODE_ENV 类型检查
2. **数据库连接**: 检查 Supabase URL 和 Key 是否正确
3. **存储问题**: 确认存储桶已创建且权限正确
4. **环境变量**: 确认 Vercel 环境变量设置正确

### 日志查看

- 前端：浏览器控制台查看环境配置日志
- 后端：启动时会显示当前环境和数据库信息

---

✅ **配置完成后，你将拥有一个完全分离的测试/生产环境设置！** 
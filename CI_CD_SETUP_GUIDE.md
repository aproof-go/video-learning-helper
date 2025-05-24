# 🚀 CI/CD 设置指南

## 📋 概述

本项目使用 GitHub Actions 实现完整的 CI/CD 流程，包括自动化测试、构建、部署和监控。

## 🏗️ CI/CD 架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   开发者推送代码   │───▶│   GitHub Actions │───▶│   自动化部署     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   测试 & 构建    │
                       └─────────────────┘
```

## 🔧 工作流详解

### 1. 🧪 测试工作流 (tests.yml)
- **触发条件**: 推送到 main/develop 分支，或创建 PR
- **包含内容**:
  - 单元测试 (后端 Python + 前端 Node.js)
  - 集成测试 (Docker Compose)
  - 安全测试 (Bandit, npm audit, Trivy)
  - 代码覆盖率统计

### 2. 🚀 主 CI/CD 工作流 (ci-cd.yml)
- **触发条件**: 推送到 main 分支
- **流程**:
  1. **测试阶段**: 运行所有测试
  2. **构建阶段**: Docker 镜像构建
  3. **部署阶段**: 部署到生产环境
  4. **通知阶段**: 发送部署状态通知

## 🔐 GitHub Secrets 配置

需要在 GitHub 仓库设置中配置以下 Secrets：

### 数据库配置
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
JWT_SECRET_KEY=your-jwt-secret
```

### Docker Hub 配置
```
DOCKER_USERNAME=your-docker-username
DOCKER_PASSWORD=your-docker-password
```

### Vercel 部署配置
```
VERCEL_TOKEN=your-vercel-token
VERCEL_ORG_ID=your-org-id
VERCEL_PROJECT_ID=your-project-id
```

### Railway 部署配置
```
RAILWAY_TOKEN=your-railway-token
RAILWAY_PROJECT_ID=your-project-id
```

### 通知配置
```
SLACK_WEBHOOK=your-slack-webhook-url
```

## 🌍 部署环境

### 前端部署 - Vercel
1. 连接 GitHub 仓库到 Vercel
2. 设置构建命令: `cd video-learning-helper-frontend && npm run build`
3. 设置输出目录: `video-learning-helper-frontend/.next`
4. 配置环境变量: `NEXT_PUBLIC_API_URL`

### 后端部署 - Railway
1. 连接 GitHub 仓库到 Railway
2. 选择 `video-learning-helper-backend` 目录
3. 配置环境变量 (Supabase URL, Key, JWT Secret)
4. 设置启动命令: `uvicorn app.main_supabase:app --host 0.0.0.0 --port $PORT`

### 替代部署选项

#### 1. 使用 Docker Compose (VPS 部署)
```bash
# 1. 克隆仓库
git clone https://github.com/aproof-go/video-learning-helper.git
cd video-learning-helper

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 文件

# 3. 启动服务
docker-compose up -d

# 4. 查看状态
docker-compose ps
```

#### 2. 使用 DigitalOcean App Platform
1. 从 GitHub 创建应用
2. 配置两个服务:
   - 前端: Node.js 服务
   - 后端: Python 服务
3. 设置环境变量
4. 配置自动部署

#### 3. 使用 AWS ECS/Fargate
1. 推送 Docker 镜像到 ECR
2. 创建 ECS 集群和服务
3. 配置 Load Balancer
4. 设置 CloudWatch 监控

## 🔧 本地开发

### 使用 Docker Compose
```bash
# 启动开发环境
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 传统方式
```bash
# 后端
cd video-learning-helper-backend
python -m uvicorn app.main_supabase:app --reload --port 8000

# 前端
cd video-learning-helper-frontend
npm run dev
```

## 📊 监控和日志

### 应用监控
- **健康检查**: `/health` 端点
- **指标收集**: Prometheus + Grafana
- **错误追踪**: Sentry 集成
- **日志聚合**: ELK Stack 或 Loki

### GitHub Actions 监控
- **工作流状态**: GitHub Actions 面板
- **测试报告**: 测试覆盖率徽章
- **部署状态**: Slack 通知

## 🔄 分支策略

### GitFlow 工作流
```
main (生产环境)
 ├── develop (开发环境)
 │   ├── feature/new-feature
 │   ├── feature/bug-fix
 │   └── hotfix/critical-fix
 └── release/v1.0.0
```

### 自动化规则
- **main**: 自动部署到生产环境
- **develop**: 自动部署到测试环境
- **feature/***: 运行测试，不部署
- **PR**: 运行完整测试套件

## 🚨 故障排除

### 常见问题

#### 1. Docker 构建失败
```bash
# 清理 Docker 缓存
docker system prune -f
docker-compose build --no-cache
```

#### 2. 测试超时
```yaml
# 增加超时时间
timeout-minutes: 30
```

#### 3. 部署失败
```bash
# 检查环境变量
echo $VERCEL_TOKEN
echo $RAILWAY_TOKEN

# 验证 Secrets 配置
gh secret list
```

#### 4. 数据库连接问题
```bash
# 测试 Supabase 连接
curl -H "apikey: $SUPABASE_KEY" $SUPABASE_URL/rest/v1/
```

## 📝 最佳实践

### 1. 安全性
- ✅ 使用 GitHub Secrets 存储敏感信息
- ✅ 定期轮换 API 密钥
- ✅ 运行安全扫描
- ✅ 限制部署权限

### 2. 性能优化
- ✅ 使用 Docker 多阶段构建
- ✅ 缓存依赖项
- ✅ 并行运行测试
- ✅ 优化镜像大小

### 3. 可维护性
- ✅ 保持工作流简洁
- ✅ 使用有意义的作业名称
- ✅ 添加详细的注释
- ✅ 定期更新依赖

## 📈 扩展建议

### 1. 高级功能
- 🔄 蓝绿部署
- 🎯 金丝雀发布
- 📊 A/B 测试
- 🔍 性能监控

### 2. 多环境管理
- 🧪 开发环境 (develop 分支)
- 🔬 测试环境 (staging 分支)
- 🚀 生产环境 (main 分支)

### 3. 自动化增强
- 🤖 自动依赖更新 (Dependabot)
- 📋 自动化 Changelog 生成
- 🏷️ 自动版本标签
- 📧 高级通知系统

---

## 🚀 快速开始

1. **Fork 本仓库**
2. **配置 GitHub Secrets**
3. **推送代码触发部署**
4. **访问部署的应用**

您的 CI/CD 流程现在已完全自动化！🎉

---

**维护者**: 视频学习助手开发团队  
**最后更新**: 2024年12月 
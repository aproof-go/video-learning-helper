#!/bin/bash

echo "🚀 开始Vercel部署流程..."

# 检查是否在前端目录
if [ ! -f "package.json" ]; then
  echo "❌ 错误: 请在前端项目目录中运行此脚本"
  exit 1
fi

# 清理缓存
echo "🧹 清理构建缓存..."
rm -rf .next
rm -rf node_modules/.cache

# 安装依赖
echo "📦 安装依赖..."
npm config set legacy-peer-deps true
npm install --legacy-peer-deps

# 本地构建测试
echo "🔨 本地构建测试..."
if npm run build; then
  echo "✅ 构建成功!"
else
  echo "❌ 构建失败，请检查错误信息"
  exit 1
fi

# 提交到Git
echo "📤 提交代码到Git..."
git add .
git commit -m "🚀 部署优化: 移除后端依赖，使用纯Next.js全栈架构"
git push origin main

echo "✅ 部署脚本完成!"
echo ""
echo "📋 下一步:"
echo "1. 访问Vercel仪表板查看部署状态"
echo "2. 配置环境变量 (SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY 等)"
echo "3. 测试API端点: https://your-domain.vercel.app/api/health" 
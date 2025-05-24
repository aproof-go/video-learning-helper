#!/bin/bash

echo "🚀 启动开发环境（并发模式）..."

if ! command -v npx &> /dev/null; then
    echo "❌ 需要安装 Node.js 和 npm"
    exit 1
fi

echo "📱 使用并发模式启动前后端..."
echo "💡 日志格式: [backend] 后端日志  [frontend] 前端日志"
echo ""

npx concurrently \
    --names "backend,frontend" \
    --prefix-colors "cyan,magenta" \
    --prefix "[{name}]" \
    --kill-others-on-fail \
    "cd video-learning-helper-backend && python -m uvicorn app.main_supabase:app --reload --host 0.0.0.0 --port 8000" \
    "cd video-learning-helper-frontend && npm run dev" 
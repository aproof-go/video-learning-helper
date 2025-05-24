#!/bin/bash

# 🚀 快速启动脚本 - 并发启动前后端，全程日志可见

set -e

echo "🎬 视频学习助手 - 快速启动"
echo "========================="

# 清理现有进程
echo "🧹 清理现有服务..."
pkill -f "python.*main_supabase" 2>/dev/null || true
pkill -f "uvicorn.*app" 2>/dev/null || true
pkill -f "next dev" 2>/dev/null || true
pkill -f "node.*next" 2>/dev/null || true
sleep 1

# 检查依赖
if [ ! -d "venv" ]; then
    echo "❌ 虚拟环境不存在，请先运行: python3 -m venv venv"
    exit 1
fi

if ! command -v npx &> /dev/null; then
    echo "❌ 需要安装 Node.js 和 npm"
    exit 1
fi

echo "🚀 并发启动前后端服务..."
echo "💡 日志格式: [backend] 后端日志 / [frontend] 前端日志"
echo "📍 后端先启动(5秒)，然后启动前端"
echo "🔥 按 Ctrl+C 停止所有服务"
echo ""

# 激活虚拟环境
source venv/bin/activate

# 并发启动
npx concurrently \
    --names "backend,frontend" \
    --prefix-colors "cyan,magenta" \
    --prefix "[{name}] " \
    --kill-others-on-fail \
    --restart-tries 3 \
    "cd video-learning-helper-backend && python -m uvicorn app.main_supabase:app --reload --host 0.0.0.0 --port 8000" \
    "sleep 5 && cd video-learning-helper-frontend && npm run dev" 
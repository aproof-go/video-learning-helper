#!/bin/bash

# 视频学习助手前端开发服务器启动脚本
# 支持热更新

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🎨 视频学习助手 - 前端开发服务器${NC}"
echo -e "${BLUE}================================${NC}"

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js 未安装，请先安装 Node.js${NC}"
    exit 1
fi

# 检查 npm
if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ npm 未安装，请先安装 npm${NC}"
    exit 1
fi

# 检查是否需要安装依赖
check_deps() {
    if [ ! -d "node_modules" ] || [ ! -f "package-lock.json" ]; then
        echo -e "${YELLOW}📦 安装依赖...${NC}"
        npm install --legacy-peer-deps
    else
        echo -e "${GREEN}✅ 依赖已存在${NC}"
    fi
}

# 清理缓存
clean_cache() {
    echo -e "${YELLOW}🧹 清理开发缓存...${NC}"
    rm -rf .next/cache 2>/dev/null || true
}

# 检查端口
check_ports() {
    ports=(3000 3001 3002 3003)
    available_port=""
    
    for port in "${ports[@]}"; do
        if ! lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            available_port=$port
            break
        fi
    done
    
    if [ -z "$available_port" ]; then
        echo -e "${YELLOW}⚠️  端口 3000-3003 都被占用，Next.js 会自动选择可用端口${NC}"
    else
        echo -e "${GREEN}✅ 端口 $available_port 可用${NC}"
    fi
}

# 启动开发服务器
start_server() {
    echo -e "${GREEN}🚀 启动前端开发服务器 (Turbo热更新模式)...${NC}"
    echo -e "${BLUE}Next.js 会自动选择可用端口${NC}"
    echo -e "${YELLOW}按 Ctrl+C 停止服务器${NC}"
    echo ""
    
    # 设置环境变量
    export NODE_ENV=development
    export NEXT_TELEMETRY_DISABLED=1
    export BACKEND_URL=http://localhost:8000
    export FRONTEND_URL=http://localhost:3000
    
    # 启动 Next.js 开发服务器 (使用Turbo模式)
    echo -e "${GREEN}🔥 启用Turbo模式加速热更新${NC}"
    npm run dev:hot
}

# 信号处理
cleanup() {
    echo -e "\n${YELLOW}🛑 正在停止前端服务器...${NC}"
    pkill -f "next dev" 2>/dev/null || true
    pkill -f "next-server" 2>/dev/null || true
    echo -e "${GREEN}✅ 前端服务器已停止${NC}"
    exit 0
}

# 捕获 Ctrl+C
trap cleanup SIGINT SIGTERM

# 主函数
main() {
    check_deps
    clean_cache
    check_ports
    start_server
}

# 运行主函数
main 
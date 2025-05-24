#!/bin/bash

# 视频学习助手后端开发服务器启动脚本
# 支持热更新和自动重启

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}📹 视频学习助手 - 后端开发服务器${NC}"
echo -e "${BLUE}================================${NC}"

# 检查虚拟环境
if [ ! -d "../venv" ]; then
    echo -e "${RED}❌ 虚拟环境不存在，请先创建虚拟环境${NC}"
    echo -e "${YELLOW}运行: python -m venv ../venv${NC}"
    exit 1
fi

# 激活虚拟环境
echo -e "${YELLOW}🔧 激活虚拟环境...${NC}"
source ../venv/bin/activate

# 检查端口是否被占用
check_port() {
    if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  端口 8000 被占用，尝试清理...${NC}"
        # 杀死占用端口的进程
        pkill -f "python.*main_supabase" 2>/dev/null || true
        pkill -f "uvicorn" 2>/dev/null || true
        sleep 2
        
        # 再次检查
        if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
            echo -e "${RED}❌ 无法清理端口 8000，请手动处理${NC}"
            exit 1
        fi
    fi
}

# 安装依赖
install_deps() {
    echo -e "${YELLOW}📦 检查并安装依赖...${NC}"
    
    # 检查是否有 requirements.txt
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt >/dev/null 2>&1 || {
            echo -e "${YELLOW}⚠️  依赖安装失败，继续运行...${NC}"
        }
    fi
    
    # 安装开发依赖
    pip install watchdog uvicorn[standard] >/dev/null 2>&1 || {
        echo -e "${YELLOW}⚠️  开发依赖安装失败，继续运行...${NC}"
    }
}

# 启动开发服务器
start_server() {
    echo -e "${GREEN}🚀 启动后端开发服务器 (热更新模式)...${NC}"
    echo -e "${BLUE}URL: http://localhost:8000${NC}"
    echo -e "${BLUE}文档: http://localhost:8000/docs${NC}"
    echo -e "${YELLOW}按 Ctrl+C 停止服务器${NC}"
    echo ""
    
    # 使用 uvicorn 的热更新功能
    uvicorn app.main_supabase:app \
        --host 0.0.0.0 \
        --port 8000 \
        --reload \
        --reload-dir app \
        --reload-delay 1 \
        --log-level info
}

# 信号处理
cleanup() {
    echo -e "\n${YELLOW}🛑 正在停止服务器...${NC}"
    pkill -f "uvicorn" 2>/dev/null || true
    echo -e "${GREEN}✅ 服务器已停止${NC}"
    exit 0
}

# 捕获 Ctrl+C
trap cleanup SIGINT SIGTERM

# 主函数
main() {
    check_port
    install_deps
    start_server
}

# 运行主函数
main 
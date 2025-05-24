#!/bin/bash

# 视频学习助手开发环境启动脚本
# 同时管理前后端服务，支持热更新

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 项目目录
BACKEND_DIR="video-learning-helper-backend"
FRONTEND_DIR="video-learning-helper-frontend"

echo -e "${PURPLE}🎬 视频学习助手 - 开发环境管理器${NC}"
echo -e "${PURPLE}======================================${NC}"

# 帮助信息
show_help() {
    echo -e "${CYAN}用法:${NC}"
    echo -e "  $0 [选项]"
    echo ""
    echo -e "${CYAN}选项:${NC}"
    echo -e "  start       启动前后端服务 (默认)"
    echo -e "  backend     只启动后端服务"
    echo -e "  frontend    只启动前端服务"
    echo -e "  stop        停止所有服务"
    echo -e "  status      查看服务状态"
    echo -e "  restart     重启所有服务"
    echo -e "  help        显示此帮助信息"
    echo ""
}

# 检查目录
check_dirs() {
    if [ ! -d "$BACKEND_DIR" ]; then
        echo -e "${RED}❌ 后端目录不存在: $BACKEND_DIR${NC}"
        exit 1
    fi
    
    if [ ! -d "$FRONTEND_DIR" ]; then
        echo -e "${RED}❌ 前端目录不存在: $FRONTEND_DIR${NC}"
        exit 1
    fi
}

# 检查服务状态
check_status() {
    echo -e "${BLUE}📊 服务状态检查:${NC}"
    
    # 检查后端
    if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "  ${GREEN}✅ 后端服务 (端口 8000): 运行中${NC}"
    else
        echo -e "  ${RED}❌ 后端服务 (端口 8000): 未运行${NC}"
    fi
    
    # 检查前端
    frontend_running=false
    for port in 3000 3001 3002 3003; do
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            echo -e "  ${GREEN}✅ 前端服务 (端口 $port): 运行中${NC}"
            frontend_running=true
            break
        fi
    done
    
    if [ "$frontend_running" = false ]; then
        echo -e "  ${RED}❌ 前端服务: 未运行${NC}"
    fi
    
    echo ""
}

# 停止所有服务
stop_services() {
    echo -e "${YELLOW}🛑 停止所有服务...${NC}"
    
    # 停止后端
    pkill -f "python.*main_supabase" 2>/dev/null || true
    pkill -f "uvicorn" 2>/dev/null || true
    
    # 停止前端
    pkill -f "next dev" 2>/dev/null || true
    pkill -f "next-server" 2>/dev/null || true
    pkill -f "node.*next" 2>/dev/null || true
    
    sleep 2
    echo -e "${GREEN}✅ 所有服务已停止${NC}"
}

# 启动后端
start_backend() {
    echo -e "${BLUE}🚀 启动后端服务...${NC}"
    cd "$BACKEND_DIR"
    
    # 给启动脚本执行权限
    chmod +x start_dev.sh 2>/dev/null || true
    
    # 启动后端 (后台运行)
    ./start_dev.sh &
    BACKEND_PID=$!
    
    cd ..
    echo -e "${GREEN}✅ 后端服务已启动 (PID: $BACKEND_PID)${NC}"
}

# 启动前端
start_frontend() {
    echo -e "${BLUE}🚀 启动前端服务...${NC}"
    cd "$FRONTEND_DIR"
    
    # 给启动脚本执行权限
    chmod +x start_dev.sh 2>/dev/null || true
    
    # 启动前端 (后台运行)
    ./start_dev.sh &
    FRONTEND_PID=$!
    
    cd ..
    echo -e "${GREEN}✅ 前端服务已启动 (PID: $FRONTEND_PID)${NC}"
}

# 启动所有服务
start_all() {
    echo -e "${CYAN}🔄 启动开发环境...${NC}"
    
    # 先停止现有服务
    stop_services
    
    # 启动后端
    start_backend
    
    # 等待后端启动
    echo -e "${YELLOW}⏳ 等待后端服务启动...${NC}"
    sleep 5
    
    # 启动前端
    start_frontend
    
    # 等待前端启动
    echo -e "${YELLOW}⏳ 等待前端服务启动...${NC}"
    sleep 5
    
    # 显示状态
    check_status
    
    echo -e "${GREEN}🎉 开发环境启动完成!${NC}"
    echo -e "${BLUE}后端: http://localhost:8000${NC}"
    echo -e "${BLUE}前端: http://localhost:3000 (或自动分配的端口)${NC}"
    echo -e "${YELLOW}按 Ctrl+C 停止所有服务${NC}"
    
    # 等待用户中断
    wait
}

# 信号处理
cleanup() {
    echo -e "\n${YELLOW}🛑 收到停止信号，正在清理...${NC}"
    stop_services
    exit 0
}

# 捕获信号
trap cleanup SIGINT SIGTERM

# 主函数
main() {
    check_dirs
    
    case "${1:-start}" in
        "start")
            start_all
            ;;
        "backend")
            stop_services
            start_backend
            echo -e "${GREEN}🎉 后端服务已启动!${NC}"
            echo -e "${BLUE}URL: http://localhost:8000${NC}"
            wait
            ;;
        "frontend")
            start_frontend
            echo -e "${GREEN}🎉 前端服务已启动!${NC}"
            wait
            ;;
        "stop")
            stop_services
            ;;
        "status")
            check_status
            ;;
        "restart")
            echo -e "${CYAN}🔄 重启所有服务...${NC}"
            stop_services
            sleep 2
            start_all
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            echo -e "${RED}❌ 未知选项: $1${NC}"
            show_help
            exit 1
            ;;
    esac
}

# 运行主函数
main "$@" 
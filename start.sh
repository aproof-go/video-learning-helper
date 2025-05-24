#!/bin/bash

# 🎬 视频学习助手 - 开发环境启动脚本
# 按顺序启动后端→前端，保持日志可见

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${PURPLE}🎬 视频学习助手 - 开发环境启动${NC}"
echo -e "${PURPLE}==============================${NC}"

# 清理现有进程
cleanup_services() {
    echo -e "${YELLOW}🧹 清理现有服务...${NC}"
    pkill -f "python.*main_supabase" 2>/dev/null || true
    pkill -f "uvicorn.*app" 2>/dev/null || true
    pkill -f "next dev" 2>/dev/null || true
    pkill -f "node.*next" 2>/dev/null || true
    sleep 1
    echo -e "${GREEN}✅ 清理完成${NC}"
}

# 检查依赖
check_dependencies() {
    echo -e "${BLUE}🔍 检查依赖...${NC}"
    
    # 检查虚拟环境
    if [ ! -d "venv" ]; then
        echo -e "${RED}❌ Python虚拟环境不存在${NC}"
        echo -e "${YELLOW}请运行: python3 -m venv venv${NC}"
        exit 1
    fi
    
    # 检查后端目录
    if [ ! -d "video-learning-helper-backend" ]; then
        echo -e "${RED}❌ 后端目录不存在${NC}"
        exit 1
    fi
    
    # 检查前端目录
    if [ ! -d "video-learning-helper-frontend" ]; then
        echo -e "${RED}❌ 前端目录不存在${NC}"
        exit 1
    fi
    
    # 检查 Node.js
    if ! command -v node &> /dev/null; then
        echo -e "${RED}❌ Node.js 未安装${NC}"
        exit 1
    fi
    
    # 检查 npm
    if ! command -v npm &> /dev/null; then
        echo -e "${RED}❌ npm 未安装${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ 依赖检查通过${NC}"
}

# 启动方案选择
show_options() {
    echo -e "${CYAN}请选择启动方式:${NC}"
    echo -e "  ${GREEN}1${NC} - 并发启动 (推荐) - 同时看到前后端日志"
    echo -e "  ${GREEN}2${NC} - 顺序启动 - 先后端后前端，分别显示日志"
    echo -e "  ${GREEN}3${NC} - 分离启动 - 后台启动后端，前台启动前端"
    echo -e "  ${GREEN}4${NC} - 仅启动后端"
    echo -e "  ${GREEN}5${NC} - 仅启动前端"
    echo ""
    read -p "请输入选项 (1-5, 默认为1): " choice
    choice=${choice:-1}
}

# 方案1：并发启动 (推荐)
start_concurrent() {
    echo -e "${PURPLE}🚀 并发启动模式${NC}"
    echo -e "${CYAN}💡 日志格式: [backend] 后端日志 / [frontend] 前端日志${NC}"
    echo -e "${YELLOW}📍 后端先启动，前端稍后启动${NC}"
    echo -e "${YELLOW}🔥 按 Ctrl+C 停止所有服务${NC}"
    echo ""
    
    # 激活虚拟环境
    source venv/bin/activate
    
    npx concurrently \
        --names "backend,frontend" \
        --prefix-colors "cyan,magenta" \
        --prefix "[{name}] " \
        --kill-others-on-fail \
        --restart-tries 3 \
        "cd video-learning-helper-backend && python -m uvicorn app.main_supabase:app --reload --host 0.0.0.0 --port 8000" \
        "sleep 5 && cd video-learning-helper-frontend && npm run dev"
}

# 方案2：顺序启动
start_sequential() {
    echo -e "${PURPLE}🚀 顺序启动模式${NC}"
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 启动后端
    echo -e "${BLUE}1️⃣ 启动后端服务...${NC}"
    cd video-learning-helper-backend
    python -m uvicorn app.main_supabase:app --reload --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    cd ..
    
    echo -e "${GREEN}✅ 后端服务已启动 (PID: $BACKEND_PID)${NC}"
    echo -e "${CYAN}🌐 后端URL: http://localhost:8000${NC}"
    echo -e "${CYAN}📚 API文档: http://localhost:8000/docs${NC}"
    
    # 等待后端启动
    echo -e "${YELLOW}⏳ 等待后端服务启动完成...${NC}"
    sleep 5
    
    # 启动前端
    echo -e "${BLUE}2️⃣ 启动前端服务...${NC}"
    cd video-learning-helper-frontend
    npm run dev
}

# 方案3：分离启动
start_detached() {
    echo -e "${PURPLE}🚀 分离启动模式${NC}"
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 后台启动后端
    echo -e "${BLUE}🔧 后台启动后端服务...${NC}"
    cd video-learning-helper-backend
    nohup python -m uvicorn app.main_supabase:app --reload --host 0.0.0.0 --port 8000 > ../backend.log 2>&1 &
    BACKEND_PID=$!
    cd ..
    
    echo -e "${GREEN}✅ 后端服务已启动 (PID: $BACKEND_PID)${NC}"
    echo -e "${CYAN}🌐 后端URL: http://localhost:8000${NC}"
    echo -e "${CYAN}📋 后端日志: tail -f backend.log${NC}"
    
    # 等待后端启动
    echo -e "${YELLOW}⏳ 等待后端服务启动...${NC}"
    sleep 5
    
    # 前台启动前端
    echo -e "${BLUE}🎨 前台启动前端服务...${NC}"
    cd video-learning-helper-frontend
    npm run dev
}

# 方案4：仅启动后端
start_backend_only() {
    echo -e "${PURPLE}🚀 启动后端服务${NC}"
    
    source venv/bin/activate
    cd video-learning-helper-backend
    echo -e "${BLUE}🌐 后端URL: http://localhost:8000${NC}"
    echo -e "${BLUE}📚 API文档: http://localhost:8000/docs${NC}"
    echo -e "${YELLOW}按 Ctrl+C 停止服务${NC}"
    python -m uvicorn app.main_supabase:app --reload --host 0.0.0.0 --port 8000
}

# 方案5：仅启动前端
start_frontend_only() {
    echo -e "${PURPLE}🚀 启动前端服务${NC}"
    
    cd video-learning-helper-frontend
    echo -e "${BLUE}🌐 前端URL: http://localhost:3000 (或自动分配端口)${NC}"
    echo -e "${YELLOW}按 Ctrl+C 停止服务${NC}"
    npm run dev
}

# 信号处理
cleanup() {
    echo -e "\n${YELLOW}🛑 收到停止信号，正在清理...${NC}"
    cleanup_services
    exit 0
}

# 捕获信号
trap cleanup SIGINT SIGTERM

# 主函数
main() {
    cleanup_services
    check_dependencies
    
    # 如果有命令行参数，直接执行对应方案
    case "${1:-}" in
        "1"|"concurrent"|"c")
            start_concurrent
            ;;
        "2"|"sequential"|"s")
            start_sequential
            ;;
        "3"|"detached"|"d")
            start_detached
            ;;
        "4"|"backend"|"be")
            start_backend_only
            ;;
        "5"|"frontend"|"fe")
            start_frontend_only
            ;;
        "help"|"h"|"-h"|"--help")
            show_options
            echo -e "${CYAN}用法示例:${NC}"
            echo -e "  ./start.sh 1        # 并发启动"
            echo -e "  ./start.sh c        # 并发启动"
            echo -e "  ./start.sh backend  # 仅启动后端"
            exit 0
            ;;
        "")
            show_options
            case $choice in
                1)
                    start_concurrent
                    ;;
                2)
                    start_sequential
                    ;;
                3)
                    start_detached
                    ;;
                4)
                    start_backend_only
                    ;;
                5)
                    start_frontend_only
                    ;;
                *)
                    echo -e "${RED}❌ 无效选项${NC}"
                    exit 1
                    ;;
            esac
            ;;
        *)
            echo -e "${RED}❌ 未知参数: $1${NC}"
            echo -e "${CYAN}运行 './start.sh help' 查看帮助${NC}"
            exit 1
            ;;
    esac
}

# 运行主函数
main "$@" 
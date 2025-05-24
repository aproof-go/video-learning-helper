#!/bin/bash

echo "🚀 开始部署视频学习助手到公网..."

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}请选择部署方式:${NC}"
echo "1. 自动部署 (推荐) - 使用GitHub Actions"
echo "2. 手动部署 - Vercel + Railway"
echo "3. VPS部署 - Docker Compose"
read -p "请输入选择 (1-3): " choice

case $choice in
  1)
    echo -e "${GREEN}🔄 使用GitHub Actions自动部署...${NC}"
    
    # 检查GitHub CLI
    if ! command -v gh &> /dev/null; then
        echo -e "${RED}GitHub CLI未安装，请先安装: brew install gh${NC}"
        exit 1
    fi
    
    # 推送到GitHub触发自动部署
    git add .
    git commit -m "Deploy: 触发自动部署"
    git push origin main
    
    echo -e "${GREEN}✅ 代码已推送，GitHub Actions将自动部署!${NC}"
    echo -e "${YELLOW}查看部署状态: https://github.com/aproof-go/video-learning-helper/actions${NC}"
    ;;
    
  2)
    echo -e "${GREEN}🔄 手动部署到Vercel和Railway...${NC}"
    
    # 部署前端到Vercel
    echo -e "${YELLOW}部署前端到Vercel...${NC}"
    cd video-learning-helper-frontend
    
    if ! command -v vercel &> /dev/null; then
        npm install -g vercel
    fi
    
    vercel --prod
    cd ..
    
    echo -e "${GREEN}✅ 前端部署完成!${NC}"
    echo -e "${YELLOW}后端请手动部署到Railway: https://railway.app${NC}"
    ;;
    
  3)
    echo -e "${GREEN}🔄 VPS Docker部署...${NC}"
    
    # 检查Docker
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}Docker未安装，请先安装Docker${NC}"
        exit 1
    fi
    
    # 启动服务
    echo -e "${YELLOW}启动Docker服务...${NC}"
    docker-compose up -d
    
    echo -e "${GREEN}✅ 服务已启动!${NC}"
    echo -e "${YELLOW}前端: http://your-domain${NC}"
    echo -e "${YELLOW}后端: http://your-domain/api${NC}"
    ;;
    
  *)
    echo -e "${RED}❌ 无效选择${NC}"
    exit 1
    ;;
esac

echo -e "${GREEN}🎉 部署完成!${NC}" 
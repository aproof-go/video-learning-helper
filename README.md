# 视频学习助手 (Video Learning Helper)

一个基于AI的视频分析和学习工具，帮助用户深入理解视频内容。

## 🎯 项目概述

视频学习助手是一个全栈Web应用，提供智能视频分析功能，包括视频分割、转场检测、语音转文字、内容分析等。用户可以上传视频文件，系统会自动进行AI分析，并提供详细的分析报告和脚本内容。

## ✨ 主要功能

### 🔐 用户管理
- 用户注册和登录
- JWT Token认证
- 安全的会话管理

### 📹 视频管理
- 视频文件上传（支持MP4、AVI、MOV等格式）
- 视频元数据提取
- 文件安全存储

### 🤖 AI智能分析
- **视频分割**: 智能识别视频片段
- **转场检测**: 自动检测视频转场
- **语音转录**: 音频转文字，支持中文
- **内容分析**: AI分析构图、运镜、主题等
- **报告生成**: 自动生成PDF分析报告

### 📊 结果展示
- 直观的分析结果表格
- 视频片段预览（缩略图/GIF）
- 优化的中文脚本显示
- 分析数据导出功能

## 🏗️ 技术架构

### 后端 (Backend)
- **框架**: FastAPI + Python 3.13
- **数据库**: Supabase (PostgreSQL)
- **认证**: JWT Token
- **AI处理**: 异步任务队列
- **文件存储**: 本地存储 + URL映射

### 前端 (Frontend)
- **框架**: Next.js 15 + React 18
- **语言**: TypeScript
- **UI组件**: Tailwind CSS + shadcn/ui
- **状态管理**: React Context
- **图标**: Lucide React

### 数据库设计
```sql
-- 用户表
users (id, email, password_hash, name, created_at)

-- 视频表
videos (id, title, filename, file_size, user_id, created_at)

-- 分析任务表
analysis_tasks (id, video_id, user_id, status, progress, created_at)

-- 视频片段表
video_segments (id, video_id, start_time, end_time, segment_type)

-- 片段分析表
segment_content_analysis (id, segment_id, caption, composition, camera_movement, theme_analysis, ai_commentary)
```

## 🚀 快速开始

### 环境要求
- Node.js 18+
- Python 3.13+
- Supabase账户

### 1. 克隆项目
```bash
git clone <repository-url>
cd video-learning-helper
```

### 2. 后端设置
```bash
cd video-learning-helper-backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # macOS/Linux
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp config.env.example config.env
# 编辑config.env，填入Supabase连接信息

# 启动后端服务
python -m uvicorn app.main_supabase:app --reload --host 0.0.0.0 --port 8000
```

### 3. 前端设置
```bash
cd video-learning-helper-frontend

# 安装依赖
npm install

# 启动前端服务
npm run dev
```

### 4. 访问应用
- 前端: http://localhost:3000
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

## 📁 项目结构

```
video-learning-helper/
├── video-learning-helper-backend/     # 后端代码
│   ├── app/                          # 应用核心
│   │   ├── api/                      # API路由
│   │   ├── core/                     # 核心配置
│   │   ├── crud/                     # 数据库操作
│   │   ├── models/                   # 数据模型
│   │   ├── schemas/                  # Pydantic模式
│   │   ├── database_supabase.py      # 数据库连接
│   │   ├── main_supabase.py          # FastAPI应用
│   │   ├── task_processor.py         # 任务处理器
│   │   └── video_analyzer.py         # 视频分析器
│   ├── uploads/                      # 上传文件（被忽略）
│   ├── requirements.txt              # Python依赖
│   └── config.env.example            # 环境变量模板
├── video-learning-helper-frontend/    # 前端代码
│   ├── app/                          # Next.js应用
│   │   ├── analysis/                 # 分析结果页面
│   │   ├── videos/                   # 视频列表页面
│   │   └── login/                    # 登录页面
│   ├── components/                   # React组件
│   │   ├── ui/                       # UI基础组件
│   │   ├── analysis-result.tsx       # 分析结果组件
│   │   └── upload.tsx                # 上传组件
│   ├── contexts/                     # React上下文
│   ├── package.json                  # Node.js依赖
│   └── tailwind.config.ts            # Tailwind配置
├── .gitignore                        # Git忽略文件
└── README.md                         # 项目说明
```

## 🔧 开发指南

### 启动开发服务器
使用提供的脚本快速启动：
```bash
# 启动后端
./start_dev.sh

# 或手动启动
cd video-learning-helper-backend
python -m uvicorn app.main_supabase:app --reload --host 0.0.0.0 --port 8000
```

### 数据库迁移
```bash
# 在后端目录执行
python migrate_test_data_to_supabase.py
```

### 测试
```bash
# 后端测试
cd video-learning-helper-backend
python test_complete_functionality.py

# 前端测试
cd video-learning-helper-frontend
npm test
```

## 📋 功能特性详解

### 视频分析流程
1. 用户上传视频文件
2. 系统创建分析任务
3. 异步处理器开始AI分析
4. 生成视频片段和分析数据
5. 保存结果到数据库
6. 前端展示分析结果

### AI分析能力
- **智能分割**: 基于场景变化的智能分割
- **构图分析**: 分析画面构图特点
- **运镜检测**: 识别摄像机运动
- **主题识别**: 理解片段主题内容
- **AI点评**: 提供专业的影视分析观点

### 优化特性
- **性能优化**: 批量数据加载，分页显示
- **中文优化**: 专门针对中文内容的字体和排版
- **响应式设计**: 适配各种屏幕尺寸
- **实时更新**: 任务进度实时显示

## 🔐 安全特性

- JWT Token认证
- 行级安全策略（RLS）
- 文件上传验证
- 用户权限隔离
- 敏感信息加密

## 📊 API文档

主要API端点：

### 认证相关
- `POST /api/v1/auth/register` - 用户注册
- `POST /api/v1/auth/login` - 用户登录
- `GET /api/v1/auth/me` - 获取当前用户信息

### 视频相关
- `POST /api/v1/videos/upload` - 上传视频
- `GET /api/v1/videos/` - 获取视频列表
- `GET /api/v1/videos/{id}` - 获取视频详情
- `DELETE /api/v1/videos/{id}` - 删除视频

### 分析相关
- `POST /api/v1/analysis/tasks` - 创建分析任务
- `GET /api/v1/analysis/tasks/{id}` - 获取任务详情
- `GET /api/v1/analysis/tasks/{id}/segments` - 获取分析结果

## 🚨 注意事项

1. **上传文件**: `uploads/` 目录已添加到 `.gitignore`，不会被提交到版本控制
2. **环境变量**: 确保正确配置 `config.env` 文件
3. **端口冲突**: 默认使用8000(后端)和3000(前端)端口
4. **数据库**: 需要有效的Supabase连接配置

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📝 更新日志

### v1.0.0 (2024-12)
- ✅ 完整的前后端架构
- ✅ 用户认证和视频管理
- ✅ AI视频分析功能
- ✅ 优化的结果展示
- ✅ 中文内容优化
- ✅ 数据库架构优化

## 📄 许可证

本项目使用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📞 联系方式

如有问题或建议，请提交 Issue 或联系开发团队。

---

**开发团队**: 视频学习助手项目组  
**最后更新**: 2024年12月 
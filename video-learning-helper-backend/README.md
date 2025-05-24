# Video Learning Helper Backend

AI拉片助手后端服务

## 功能特性

- 用户认证系统（注册/登录）
- 视频上传与处理
- 自动视频分割与GIF导出
- 转场检测与标注
- 音频转写（Whisper）
- 分析报告生成
- 异步任务处理（Celery）

## 技术栈

- **Web框架**: FastAPI
- **数据库**: PostgreSQL (Supabase)
- **ORM**: SQLAlchemy (异步)
- **认证**: JWT + Bearer Token
- **任务队列**: Celery + Redis
- **视频处理**: OpenCV, MoviePy
- **音频转写**: OpenAI Whisper

## 安装与运行

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `env.example` 为 `.env` 并修改配置：

```bash
cp env.example .env
```

### 3. 启动服务

```bash
python run.py
```

或者：

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. 访问文档

- API文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health

## API接口

### 认证接口

- `POST /api/v1/auth/register` - 用户注册
- `POST /api/v1/auth/login` - 用户登录
- `GET /api/v1/auth/me` - 获取当前用户信息
- `POST /api/v1/auth/token` - OAuth2兼容登录

### 视频分析接口

- `POST /api/v1/videos/upload` - 上传视频
- `POST /api/v1/analysis/create` - 创建分析任务
- `GET /api/v1/analysis/{task_id}` - 获取分析结果
- `GET /api/v1/analysis/{task_id}/download` - 下载分析报告

## 项目结构

```
video-learning-helper-backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI应用入口
│   ├── config.py            # 配置文件
│   ├── database.py          # 数据库连接
│   ├── api/                 # API路由
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── api.py       # 路由聚合
│   │       ├── auth.py      # 认证路由
│   │       └── videos.py    # 视频相关路由
│   ├── core/                # 核心功能
│   │   ├── __init__.py
│   │   └── security.py      # 安全认证
│   ├── crud/                # 数据库操作
│   │   ├── __init__.py
│   │   └── user.py          # 用户CRUD
│   ├── models/              # 数据模型
│   │   ├── __init__.py
│   │   └── user.py          # 用户模型
│   ├── schemas/             # Pydantic模式
│   │   ├── __init__.py
│   │   └── user.py          # 用户模式
│   └── services/            # 业务逻辑服务
│       ├── __init__.py
│       ├── video_processor.py
│       └── analysis_service.py
├── requirements.txt         # Python依赖
├── env.example             # 环境变量示例
├── run.py                  # 启动脚本
└── README.md              # 项目说明
```

## 开发

### 代码格式化

```bash
black app/
```

### 代码检查

```bash
flake8 app/
```

### 运行测试

```bash
pytest
``` 
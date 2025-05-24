# AI视频分析功能说明

## 🎯 功能概述

本系统集成了先进的AI视频分析技术，提供以下核心功能：

### 1. 视频分割 (Video Segmentation)
- **功能**: 基于场景变化自动分割视频片段
- **技术**: OpenCV + K-means聚类算法
- **输出**: 场景时间段、场景类型、持续时间

### 2. 转场检测 (Transition Detection)
- **功能**: 检测视频中的转场和切换点
- **技术**: 帧间差异分析 + 直方图相关性
- **输出**: 转场时间点、转场强度、转场类型

### 3. 音频转录 (Audio Transcription)
- **功能**: 语音识别和字幕生成
- **技术**: OpenAI Whisper模型
- **输出**: 转录文本、时间轴字幕、SRT字幕文件

### 4. 分析报告 (Report Generation)
- **功能**: 生成comprehensive分析报告
- **技术**: ReportLab PDF生成
- **输出**: 格式化PDF报告

## 🚀 快速开始

### 1. 安装依赖

```bash
# 进入后端目录
cd video-learning-helper-backend

# 运行自动安装脚本
python install_dependencies.py

# 或者手动安装
pip install -r requirements.txt
```

### 2. 启动服务

```bash
# 激活虚拟环境（如果使用）
source venv/bin/activate

# 启动后端服务
python -m app.main_supabase
```

### 3. 上传和分析视频

1. 访问前端界面: `http://localhost:3000`
2. 登录账户
3. 上传视频文件
4. 选择分析选项
5. 提交分析任务
6. 等待分析完成

## 📋 系统要求

### 硬件要求
- **CPU**: 多核处理器推荐
- **内存**: 8GB+ RAM推荐
- **存储**: 至少5GB可用空间
- **GPU**: 可选，支持CUDA加速

### 软件要求
- **Python**: 3.8+
- **FFmpeg**: 用于视频处理
- **操作系统**: Windows/macOS/Linux

## 🔧 配置说明

### 任务处理器配置

在 `app/task_processor.py` 中可以调整：

```python
# 最大并发任务数
max_concurrent_tasks = 2

# 任务队列大小
task_queue = asyncio.Queue()
```

### Whisper模型配置

支持的模型大小：
- `tiny`: 最快，准确度较低
- `base`: 平衡速度和准确度（默认）
- `small`: 更准确，稍慢
- `medium`: 高准确度
- `large`: 最高准确度，最慢

修改 `app/video_analyzer.py`：

```python
self.whisper_model = whisper.load_model("base")  # 更改模型大小
```

## 📊 API接口

### 创建分析任务

```http
POST /api/v1/analysis/tasks
Content-Type: application/json
Authorization: Bearer <token>

{
  "video_id": "uuid",
  "video_segmentation": true,
  "transition_detection": true,
  "audio_transcription": true,
  "report_generation": true
}
```

### 查询任务状态

```http
GET /api/v1/analysis/tasks/{task_id}
Authorization: Bearer <token>
```

### 获取视频分析任务列表

```http
GET /api/v1/analysis/videos/{video_id}/tasks
Authorization: Bearer <token>
```

### 查看处理器状态

```http
GET /api/v1/system/processor-status
```

## 📁 文件结构

```
video-learning-helper-backend/
├── app/
│   ├── video_analyzer.py      # 核心分析引擎
│   ├── task_processor.py      # 异步任务处理器
│   ├── main_supabase.py       # 主应用
│   └── database_supabase.py   # 数据库管理
├── analysis_results/          # 分析结果目录
├── uploads/                   # 上传文件目录
└── requirements.txt           # 依赖列表
```

## 🔍 分析流程

1. **任务创建**: 用户提交分析任务
2. **任务入队**: 任务加入处理队列
3. **视频信息提取**: 获取基本视频信息
4. **视频分割**: 场景检测和分割
5. **转场检测**: 识别转场点
6. **音频转录**: 语音识别
7. **报告生成**: 创建PDF报告
8. **结果保存**: 更新数据库和文件

## 📈 性能优化

### 1. 并发处理
- 支持多任务并发分析
- 可配置最大并发数

### 2. 内存管理
- 流式处理大视频文件
- 及时释放内存资源

### 3. 采样优化
- 智能帧采样降低计算量
- 可配置采样频率

### 4. 模型缓存
- Whisper模型预加载
- 避免重复初始化

## ⚠️ 注意事项

### 1. 文件格式支持
支持的视频格式：
- MP4, AVI, MOV, WMV, FLV, WebM, MKV

### 2. 文件大小限制
- 单文件最大：1GB
- 可在配置中调整

### 3. 分析时间
分析时间取决于：
- 视频长度和质量
- 启用的分析功能
- 硬件性能

### 4. 存储空间
确保有足够空间存储：
- 原始视频文件
- 临时处理文件
- 分析结果文件

## 🐛 故障排除

### 常见问题

1. **Whisper模型下载失败**
   ```bash
   # 手动下载模型
   python -c "import whisper; whisper.load_model('base')"
   ```

2. **OpenCV安装问题**
   ```bash
   # 尝试headless版本
   pip install opencv-python-headless
   ```

3. **FFmpeg未找到**
   ```bash
   # macOS
   brew install ffmpeg
   
   # Ubuntu
   sudo apt install ffmpeg
   
   # Windows
   # 下载并添加到PATH
   ```

4. **内存不足**
   - 减少并发任务数
   - 使用更小的Whisper模型
   - 增加系统内存

### 日志查看

```bash
# 查看详细日志
tail -f /path/to/logfile

# 或在代码中调整日志级别
logging.basicConfig(level=logging.DEBUG)
```

## 🔮 未来计划

### 即将推出的功能
- [ ] 目标检测和识别
- [ ] 情感分析
- [ ] 自动摘要生成
- [ ] 多语言支持
- [ ] 实时分析
- [ ] GPU加速优化

### 技术升级
- [ ] 更先进的分割算法
- [ ] 深度学习转场检测
- [ ] 多模态分析
- [ ] 分布式处理

## 📞 技术支持

如果遇到问题或需要帮助：

1. 查看本文档的故障排除部分
2. 检查系统日志
3. 确认依赖安装正确
4. 验证硬件要求

---

**注意**: 首次运行时，系统会自动下载Whisper模型，这可能需要一些时间和网络连接。 
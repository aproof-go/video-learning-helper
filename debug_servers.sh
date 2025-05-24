#!/bin/bash

# 调试服务器启动脚本 - 使用tmux分屏显示前后端日志

echo "🚀 启动视频学习助手调试环境..."

# 检查是否已有video-debug会话
if tmux has-session -t video-debug 2>/dev/null; then
    echo "⚠️  检测到现有的video-debug会话，正在终止..."
    tmux kill-session -t video-debug
fi

# 创建新的tmux会话
echo "📱 创建tmux调试会话..."
tmux new-session -d -s video-debug

# 重命名第一个窗口为后端
tmux rename-window -t video-debug:0 'Backend'

# 在后端窗口启动后端服务
tmux send-keys -t video-debug:0 'cd video-learning-helper-backend' C-m
tmux send-keys -t video-debug:0 'echo "🔧 启动后端服务..."' C-m
tmux send-keys -t video-debug:0 'python -m uvicorn app.main_supabase:app --reload --host 0.0.0.0 --port 8000' C-m

# 创建新窗口用于前端
tmux new-window -t video-debug -n 'Frontend'
tmux send-keys -t video-debug:1 'cd video-learning-helper-frontend' C-m
tmux send-keys -t video-debug:1 'echo "⚛️  启动前端服务..."' C-m
tmux send-keys -t video-debug:1 'npm run dev' C-m

# 创建第三个窗口用于测试和命令
tmux new-window -t video-debug -n 'Commands'
tmux send-keys -t video-debug:2 'echo "🛠️  命令窗口已就绪"' C-m
tmux send-keys -t video-debug:2 'echo "📝 可用命令:"' C-m
tmux send-keys -t video-debug:2 'echo "  - python test_real_ai_analyzer.py  # 测试AI分析器"' C-m
tmux send-keys -t video-debug:2 'echo "  - python test_smart_segmentation.py  # 测试智能分割"' C-m
tmux send-keys -t video-debug:2 'echo "  - Ctrl+B 然后按数字键切换窗口"' C-m
tmux send-keys -t video-debug:2 'echo "  - Ctrl+B 然后按 d 脱离会话"' C-m
tmux send-keys -t video-debug:2 'echo ""' C-m

# 分割后端窗口，上半部分显示后端日志，下半部分显示系统监控
tmux split-window -t video-debug:0 -v -p 30
tmux send-keys -t video-debug:0.1 'echo "📊 系统监控"' C-m
tmux send-keys -t video-debug:0.1 'watch -n 2 "echo \"=== 后端进程 ===\" && ps aux | grep uvicorn | grep -v grep && echo \"\" && echo \"=== 内存使用 ===\" && free -h 2>/dev/null || vm_stat | head -10 && echo \"\" && echo \"=== 磁盘空间 ===\" && df -h . | tail -1"' C-m

# 回到后端窗口
tmux select-window -t video-debug:0

echo ""
echo "✅ 调试环境已启动！"
echo ""
echo "📖 使用说明:"
echo "  🖥️  访问前端: http://localhost:3000"
echo "  🔧 访问后端API: http://localhost:8000"
echo "  📚 API文档: http://localhost:8000/docs"
echo ""
echo "🎛️  tmux快捷键:"
echo "  Ctrl+B 然后按 0  -> 后端窗口"
echo "  Ctrl+B 然后按 1  -> 前端窗口"  
echo "  Ctrl+B 然后按 2  -> 命令窗口"
echo "  Ctrl+B 然后按 d  -> 脱离会话（后台运行）"
echo "  Ctrl+B 然后按 &  -> 关闭当前窗口"
echo ""
echo "🔄 重新进入会话: tmux attach -t video-debug"
echo "🛑 完全停止服务: tmux kill-session -t video-debug"
echo ""

# 等待3秒让用户看到说明
sleep 3

# 附加到会话
echo "🎯 进入调试会话..."
tmux attach -t video-debug 
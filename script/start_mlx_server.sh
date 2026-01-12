#!/bin/bash

# 获取脚本所在目录并进入
cd "$(dirname "$0")"

# 配置
VENV_PATH="../.venv/bin/activate"
LOG_FILE="mlx_server.log"
PID_FILE="mlx_server.pid"
# 默认模型路径，可通过环境变量 MODEL_PATH 覆盖
DEFAULT_MODEL="../models/Qwen3-14B-MLX"
MODEL_PATH="${MODEL_PATH:-$DEFAULT_MODEL}"
HOST="127.0.0.1"
PORT="8080"

# 检查虚拟环境
if [ ! -f "$VENV_PATH" ]; then
    echo "Error: Virtual environment not found at $VENV_PATH"
    exit 1
fi

source "$VENV_PATH"

start() {
    if [ -f "$PID_FILE" ]; then
        if ps -p $(cat "$PID_FILE") > /dev/null; then
            echo "✅ Server is already running (PID: $(cat "$PID_FILE"))"
            return
        else
            echo "⚠️  Found stale PID file. Removing..."
            rm "$PID_FILE"
        fi
    fi

    echo "🚀 Starting MLX Server for Qwen3-14B-MLX..."
    # 强制使用当前虚拟环境中的 python
    "../.venv/bin/python" -m mlx_lm server \
        --model "$MODEL_PATH" \
        --host "$HOST" \
        --port "$PORT" \
        --trust-remote-code \
        --use-default-chat-template \
        --chat-template-args '{"enable_thinking": false}' \
        --temp 0.7 \
        --top-p 0.9 \
        --max-tokens 4096 \
        > "$LOG_FILE" 2>&1 < /dev/null &
    
    PID=$!
    disown $PID
    echo $PID > "$PID_FILE"
    echo "✅ Server started with PID $PID"
    echo "📄 Logs are being written to $LOG_FILE"
}

stop() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p $PID > /dev/null; then
            echo "🛑 Stopping server (PID: $PID)..."
            kill $PID
            rm "$PID_FILE"
            echo "✅ Server stopped."
        else
            echo "⚠️  Server process $PID not found. Removing stale PID file."
            rm "$PID_FILE"
        fi
    else
        echo "ℹ️  No PID file found. Server might not be running."
    fi
}

status() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p $PID > /dev/null; then
            echo "✅ Server is running (PID: $PID)"
            echo "--- Last 5 lines of logs ---"
            tail -n 5 "$LOG_FILE"
        else
            echo "⚠️  Server is NOT running (Stale PID file found)"
        fi
    else
        echo "ℹ️  Server is NOT running"
    fi
}

case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        stop
        sleep 2
        start
        ;;
    status)
        status
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        echo "Defaulting to 'start'..."
        start
        ;;
esac


# # 激活虚拟环境
# source .venv/bin/activate

# # 启动 MLX Server
# # --model: 指定本地模型路径
# # --host/--port: 服务地址与端口
# # --trust-remote-code: 信任自定义代码（如 tokenizer）
# # --use-default-chat-template: 使用模型自带的聊天模板
# # --chat-template-args: 传递参数给模板（此处关闭思考过程输出）

# echo "Starting MLX Server for Qwen3-0.6B..."
# python -m mlx_lm server \
#     --model /Users/kakack/Documents/Models/Qwen3-0.6B \
#     --host 127.0.0.1 \
#     --port 8080 \
#     --trust-remote-code \
#     --use-default-chat-template \
#     --chat-template-args '{"enable_thinking": false}'
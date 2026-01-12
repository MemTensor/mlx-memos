#!/bin/bash

# 获取脚本所在目录并进入
cd "$(dirname "$0")"

# 配置
VENV_PATH="../.venv/bin/activate"
LOG_FILE="embedding_server.log"
PID_FILE="embedding_server.pid"
PORT="8081"

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

    echo "🚀 Starting Embedding & Rerank Server (Port $PORT)..."
    nohup python embedding_rerank_server.py > "$LOG_FILE" 2>&1 &
    
    PID=$!
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

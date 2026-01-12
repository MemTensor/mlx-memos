#!/bin/bash

# 获取脚本所在目录并进入
cd "$(dirname "$0")"

# 配置
VENV_PATH="../.venv/bin/activate"
MODEL_NAME="Qwen/Qwen3-14B"
MLX_PATH="../models/Qwen3-14B-MLX"

# 检查虚拟环境
if [ ! -f "$VENV_PATH" ]; then
    echo "Error: Virtual environment not found at $VENV_PATH"
    exit 1
fi

source "$VENV_PATH"

echo "🚀 Starting conversion for $MODEL_NAME..."
echo "📂 Output path: $MLX_PATH"
echo "ℹ️  This requires ~10GB of free disk space (in addition to the cached original model)."

python -m mlx_lm convert \
    --model "$MODEL_NAME" \
    --mlx-path "$MLX_PATH" \
    --trust-remote-code \
    -q \
    --q-bits 4 \
    --q-group-size 32

if [ $? -eq 0 ]; then
    echo "✅ Conversion completed successfully!"
    echo "💡 You can now start the server with: ./start_mlx_server.sh restart"
else
    echo "❌ Conversion failed."
fi

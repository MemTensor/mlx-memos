#!/bin/bash

set -euo pipefail

# 获取脚本所在目录并进入
cd "$(dirname "$0")"

# 配置
# 指向本地已下载的原始模型目录
MODEL_REPO="../models/Qwen3-4B"
OUTPUT_DIR="../models/Qwen3-4B-MLX"
VENV_PATH="../.venv/bin/activate"

# 检查虚拟环境
if [ ! -f "$VENV_PATH" ]; then
    echo "Error: Virtual environment not found at $VENV_PATH"
    exit 1
fi

source "$VENV_PATH"

# 检查本地源模型是否存在
if [ ! -d "$MODEL_REPO" ]; then
    echo "Error: Local model directory not found at $MODEL_REPO"
    exit 1
fi

echo "🚀 Starting LOCAL conversion for $MODEL_REPO..."
echo "📂 Output directory: $OUTPUT_DIR"

# 创建输出目录
mkdir -p ../models

# 运行转换命令
# --hf-path: 指向本地目录
python -m mlx_lm convert \
    --hf-path "$MODEL_REPO" \
    -q \
    --q-bits 4 \
    --mlx-path "$OUTPUT_DIR"

echo "✅ Conversion complete! Model saved to $OUTPUT_DIR"

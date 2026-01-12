#!/bin/bash

echo "🚀 Sending verification request to Qwen3-14B-MLX server..."

curl http://127.0.0.1:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "../models/Qwen3-14B-MLX",
    "messages": [
      {"role": "user", "content": "你好，请做一个简短的自我介绍。"}
    ],
    "temperature": 0.7,
    "max_tokens": 200,
    "stream": false
  }' | jq .

echo -e "\n-----------------------------------"
echo "Note: If you see raw unicode characters (like \u4f60\u597d), jq handles the decoding automatically."

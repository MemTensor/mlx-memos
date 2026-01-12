#!/bin/bash

echo "🔍 Verifying Embedding API (bge-m3)..."
curl -s -X POST http://127.0.0.1:8081/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{
    "model": "bge-m3",
    "input": "The weather is nice today."
  }' | jq .
echo -e "\n-----------------------------------"

echo "🔍 Verifying Rerank API (bge-reranker-v2-m3)..."
curl -s -X POST http://127.0.0.1:8081/v1/rerank \
  -H "Content-Type: application/json" \
  -d '{
    "model": "bge-reranker-v2-m3",
    "query": "What is deep learning?",
    "documents": [
      "Deep learning is a subset of machine learning.",
      "I love eating apples.",
      "Neural networks are used in deep learning."
    ],
    "top_n": 3
  }' | jq .
echo -e "\n✅ Verification requests sent."

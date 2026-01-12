import os
import torch
import uvicorn
from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel, Field
from typing import List, Union, Optional
from sentence_transformers import SentenceTransformer, CrossEncoder

# 配置
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
EMBEDDING_MODEL_PATH = os.path.abspath(os.path.join(SCRIPT_DIR, "../models/bge-m3"))
RERANKER_MODEL_PATH = os.path.abspath(os.path.join(SCRIPT_DIR, "../models/bge-reranker-v2-m3"))
HOST = "127.0.0.1"
PORT = 8081

app = FastAPI(title="Embedding & Rerank Server")

# 全局模型变量
embedding_model = None
reranker_model = None

# 数据模型
class EmbeddingRequest(BaseModel):
    input: Union[str, List[str]]
    model: Optional[str] = None
    encoding_format: Optional[str] = "float"

class EmbeddingResponse(BaseModel):
    object: str = "list"
    data: List[dict]
    model: str
    usage: dict

class RerankRequest(BaseModel):
    model: Optional[str] = None
    query: str
    documents: List[str]
    top_n: Optional[int] = None
    return_documents: Optional[bool] = False

class RerankResponse(BaseModel):
    id: Optional[str] = None
    results: List[dict]

@app.on_event("startup")
async def load_models():
    global embedding_model, reranker_model
    
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    print(f"🚀 Loading models on device: {device}")

    # 加载 Embedding 模型
    if os.path.exists(EMBEDDING_MODEL_PATH):
        print(f"Loading Embedding model from {EMBEDDING_MODEL_PATH}...")
        try:
            # 尝试优先加载 (可能是 safetensors 问题，显式允许 pytorch 权重)
            embedding_model = SentenceTransformer(
                EMBEDDING_MODEL_PATH, 
                device=device,
                trust_remote_code=True,
            )
        except Exception as e:
            print(f"⚠️ Failed to load embedding model directly: {e}")
            print("Trying with use_safetensors=False...")
            embedding_model = SentenceTransformer(
                EMBEDDING_MODEL_PATH, 
                device=device,
                trust_remote_code=True,
                model_kwargs={"use_safetensors": False}
            )
    else:
        print(f"⚠️ Embedding model not found at {EMBEDDING_MODEL_PATH}")

    # 加载 Reranker 模型
    if os.path.exists(RERANKER_MODEL_PATH):
        print(f"Loading Reranker model from {RERANKER_MODEL_PATH}...")
        try:
            reranker_model = CrossEncoder(
                RERANKER_MODEL_PATH, 
                device=device,
                trust_remote_code=True,
                automodel_args={"use_safetensors": True} # 这个有 safetensors
            )
        except Exception:
             reranker_model = CrossEncoder(
                RERANKER_MODEL_PATH, 
                device=device,
                trust_remote_code=True
            )
    else:
        print(f"⚠️ Reranker model not found at {RERANKER_MODEL_PATH}")

@app.post("/v1/embeddings", response_model=EmbeddingResponse)
async def create_embedding(request: EmbeddingRequest):
    if not embedding_model:
        raise HTTPException(status_code=503, detail="Embedding model not loaded")
    
    inputs = [request.input] if isinstance(request.input, str) else request.input
    
    # 执行推理
    embeddings = embedding_model.encode(inputs, normalize_embeddings=True)
    
    data = []
    for i, emb in enumerate(embeddings):
        data.append({
            "object": "embedding",
            "index": i,
            "embedding": emb.tolist()
        })
        
    return EmbeddingResponse(
        data=data,
        model=request.model or "bge-m3",
        usage={"prompt_tokens": 0, "total_tokens": 0} # 简化处理
    )

@app.post("/v1/rerank", response_model=RerankResponse)
async def rerank(request: RerankRequest):
    if not reranker_model:
        raise HTTPException(status_code=503, detail="Reranker model not loaded")
    
    # 构造 (query, doc) 对
    pairs = [[request.query, doc] for doc in request.documents]
    
    # 执行推理
    scores = reranker_model.predict(pairs)
    
    results = []
    for i, score in enumerate(scores):
        results.append({
            "index": i,
            "relevance_score": float(score),
            "document": request.documents[i] if request.return_documents else None
        })
    
    # 排序
    results.sort(key=lambda x: x["relevance_score"], reverse=True)
    
    # Top N 截断
    if request.top_n:
        results = results[:request.top_n]
        
    return RerankResponse(results=results)

if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT)

# MLX-MemOS

**MLX-MemOS** is a high-performance LLM serving and RAG (Retrieval-Augmented Generation) infrastructure toolkit optimized for Apple Silicon (macOS). Built on top of Apple's [MLX](https://github.com/ml-explore/mlx) framework, it provides a seamless experience for running large language models (like Qwen3) and embedding/reranking models locally with OpenAI-compatible APIs.

## 🚀 Key Features

*   **Apple Silicon Optimized**: Leverages MLX for efficient inference on Mac devices (M1/M2/M3/M4).
*   **OpenAI Compatible**: Provides a drop-in replacement for OpenAI's Chat Completions API.
*   **RAG Ready**: Includes a dedicated server for Embeddings (`bge-m3`) and Reranking (`bge-reranker-v2-m3`).
*   **Model Management**: Ready-to-use scripts for converting and managing Qwen3 models (0.6B, 4B, 8B, 14B).
*   **Production Friendly**: Includes startup/shutdown scripts, PID management, and logging.
*   **Benchmarking**: Built-in tools to stress test and verify model performance.

## 📋 Prerequisites

*   macOS 13.0+ (Ventura or later recommended)
*   Python 3.10+
*   Apple Silicon (M-series chip)

## 🛠️ Installation

1.  **Clone the repository**
    ```bash
    git clone https://github.com/yourusername/MLX-MemOS.git
    cd MLX-MemOS
    ```

2.  **Create and activate a virtual environment**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

## 🏗️ Model Preparation
41→
42→MLX-MemOS expects models to be placed in the `models/` directory.
43→
44→### ⚠️ Important: Restore Large Models
45→
46→Due to GitHub's file size limits, some large model files (over 2GB) are split into chunks. **You must run the following command after cloning to restore them:**
47→
48→```bash
49→./script/manage_large_files.sh merge
50→```
51→
52→This will reassemble files like `pytorch_model.bin` and `model.safetensors` from their split parts. Specifically, it handles:

*   `models/bge-m3/pytorch_model.bin`
*   `models/bge-reranker-v2-m3/model.safetensors`
*   `models/Qwen3-8B-MLX/model.safetensors`
*   `models/Qwen3-4B-MLX/model.safetensors`
*   `models/Qwen3-14B-MLX/model-00001-of-00002.safetensors`
*   `models/Qwen3-14B-MLX/model-00002-of-00002.safetensors`
53→
54→### Download & Convert Models
55→
56→We also provide scripts to help you convert Hugging Face models to MLX format.

```bash
# Example: Convert Qwen3-14B
./script/convert_qwen3_14b.sh

# Example: Convert Qwen3-8B
./script/convert_qwen3_8b.sh
```

*Ensure you have sufficient disk space and memory for the conversion process.*

## 🚦 Usage

### 1. Start the LLM Server (Chat Completions)

This starts an OpenAI-compatible server hosting the LLM (default: Qwen3-14B-MLX).

```bash
./script/start_mlx_server.sh start
```

*   **Port**: 8080
*   **Endpoint**: `http://127.0.0.1:8080/v1/chat/completions`
*   **Logs**: `logs/mlx_server.log`

To stop or restart:
```bash
./script/start_mlx_server.sh stop
./script/start_mlx_server.sh restart
./script/start_mlx_server.sh status
```

### 2. Start the Embedding & Rerank Server

This starts a separate server for text embeddings and document reranking.

```bash
./script/start_embedding_server.sh start
```

*   **Port**: 8081
*   **Endpoints**:
    *   Embeddings: `http://127.0.0.1:8081/v1/embeddings`
    *   Rerank: `http://127.0.0.1:8081/v1/rerank`
*   **Logs**: `logs/embedding_server.log`

### 3. Verification

Verify that the servers are running correctly:

```bash
# Verify LLM Server
./script/verify_mlx_curl.sh
# OR using Python script
python script/verify_mlx_server.py

# Verify Embedding/Rerank Server
./script/verify_embedding_server.sh
```

## 📊 Benchmarking

You can benchmark the performance of the LLM server using the included Python script:

```bash
python script/benchmark_mlx.py
```

This script will simulate concurrent requests and report token generation speeds (TPS) and latency metrics.

## 📂 Project Structure

```
MLX-MemOS/
├── models/                 # Model checkpoints (MLX format)
├── script/                 # Operation scripts
│   ├── start_mlx_server.sh         # Manage LLM server
│   ├── start_embedding_server.sh   # Manage Embedding server
│   ├── convert_*.sh                # Model conversion scripts
│   ├── verify_*.sh                 # Verification scripts
│   └── benchmark_mlx.py            # Performance testing
├── logs/                   # Server logs
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation
```

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

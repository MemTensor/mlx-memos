import requests
import time
import json
import random
import statistics
import concurrent.futures
import string
import os

# ================= 配置区域 =================
# 服务地址
API_URL = "http://127.0.0.1:8080/v1/chat/completions"
# 模型路径（需与启动服务时一致）
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.abspath(os.path.join(SCRIPT_DIR, "../models/Qwen3-14B-MLX"))

# 压测参数
INPUT_TOKENS_TARGET = 5000  # 目标输入 Token 长度
OUTPUT_TOKENS_TARGET = 3000 # 目标输出 Token 长度 (max_tokens)
TOTAL_REQUESTS = 20         # 每个并发层级的总请求数
CONCURRENCY_LEVELS = [1, 3] # 并发层级列表

# 随机词库（用于生成 Prompt）
WORDS = ["apple", "banana", "cherry", "date", "elderberry", "fig", "grape", "honeydew", 
         "kiwi", "lemon", "mango", "nectarine", "orange", "papaya", "quince", "raspberry", 
         "strawberry", "tangerine", "ugli", "vanilla", "watermelon", "xigua", "yam", "zucchini",
         "run", "jump", "walk", "sleep", "eat", "drink", "think", "code", "debug", "deploy",
         "fast", "slow", "hard", "easy", "complex", "simple", "red", "green", "blue", "yellow"]

def generate_random_prompt(target_tokens):
    """
    生成近似指定 token 数量的随机文本。
    对于大多数 Tokenizer，英文单词 + 空格通常约为 1-1.3 tokens。
    这里简单按 1 word ≈ 1 token 估算。
    """
    # 为了性能，先生成一个较长的基础块，然后重复
    base_len = 100
    base_words = [random.choice(WORDS) for _ in range(base_len)]
    
    total_words_needed = target_tokens
    repeats = total_words_needed // base_len
    remainder = total_words_needed % base_len
    
    words = []
    for _ in range(repeats):
        words.extend(base_words)
    words.extend([random.choice(WORDS) for _ in range(remainder)])
    
    return " ".join(words)

# 预生成一个 Prompt 以保证所有请求输入一致（控制变量），也可以改为每次随机
print(f"🔄 Generating random prompt with ~{INPUT_TOKENS_TARGET} tokens...")
SHARED_PROMPT = generate_random_prompt(INPUT_TOKENS_TARGET)
print(f"✅ Prompt ready. Length in chars: {len(SHARED_PROMPT)}")

def calculate_percentiles(data):
    """计算 P50, P95, P99 等统计值"""
    if not data:
        return {k: 0 for k in ["mean", "min", "max", "p50", "p95", "p99"]}
    
    data.sort()
    n = len(data)
    
    def get_p(p):
        idx = int(n * p)
        return data[min(idx, n - 1)]

    return {
        "mean": statistics.mean(data),
        "min": data[0],
        "max": data[-1],
        "p50": get_p(0.50),  # Median
        "p95": get_p(0.95),
        "p99": get_p(0.99)
    }

def send_request(req_id):
    """发送单个请求并记录详细指标"""
    payload = {
        "model": MODEL_PATH,
        "messages": [{"role": "user", "content": SHARED_PROMPT}],
        "temperature": 0.7,
        "max_tokens": OUTPUT_TOKENS_TARGET,
        "stream": True 
    }
    
    start_time = time.time()
    first_token_time = None
    last_token_time = None
    token_count = 0
    
    try:
        with requests.post(API_URL, json=payload, stream=True) as response:
            if response.status_code != 200:
                return {"error": f"Status {response.status_code}"}

            for line in response.iter_lines():
                if not line: continue
                decoded_line = line.decode('utf-8')
                if not decoded_line.startswith('data: '): continue
                
                data_str = decoded_line[6:].strip()
                if data_str == '[DONE]': break
                
                try:
                    data = json.loads(data_str)
                    delta = data['choices'][0]['delta']
                    if 'content' in delta and delta['content']:
                        curr_t = time.time()
                        if first_token_time is None:
                            first_token_time = curr_t
                        last_token_time = curr_t
                        token_count += 1
                except:
                    continue

        end_time = time.time()
        
        # 计算核心指标
        ttft = (first_token_time - start_time) if first_token_time else 0
        latency = end_time - start_time
        
        # Inter-Token Latency (排除首字)
        itl = 0
        if token_count > 1 and last_token_time and first_token_time:
            itl = (last_token_time - first_token_time) / (token_count - 1)
            
        # Tokens Per Second (针对该请求)
        tps = token_count / latency if latency > 0 else 0

        return {
            "req_id": req_id,
            "success": True,
            "ttft": ttft,
            "itl": itl,
            "latency": latency,
            "tokens": token_count,
            "tps": tps
        }

    except Exception as e:
        return {"error": str(e)}

def print_stats_table(name, data, unit="s"):
    """打印格式化的统计表格"""
    stats = calculate_percentiles(data)
    print(f"   {name:<15} | Mean: {stats['mean']:6.4f}{unit} | Min: {stats['min']:6.4f}{unit} | Max: {stats['max']:6.4f}{unit} | P50: {stats['p50']:6.4f}{unit} | P95: {stats['p95']:6.4f}{unit} | P99: {stats['p99']:6.4f}{unit}")

def run_benchmark(concurrency):
    print(f"\n{'='*80}")
    print(f"🚀 Starting Benchmark | Concurrency: {concurrency} | Total Requests: {TOTAL_REQUESTS}")
    print(f"{'='*80}")
    
    results = []
    start_wall_time = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(send_request, i) for i in range(TOTAL_REQUESTS)]
        
        for future in concurrent.futures.as_completed(futures):
            res = future.result()
            if "error" in res:
                print(f"❌ Request failed: {res['error']}")
            else:
                results.append(res)
                # 实时简报：Req ID | TTFT | Tokens
                print(f"   [Req {res['req_id']:02d}] TTFT: {res['ttft']:.3f}s | Tokens: {res['tokens']} | ITL: {res['itl']:.3f}s | TPS: {res['tps']:.1f}")

    end_wall_time = time.time()
    total_wall_time = end_wall_time - start_wall_time
    
    if not results:
        print("❌ No successful requests.")
        return

    # 聚合数据
    ttfts = [r['ttft'] for r in results]
    itls = [r['itl'] for r in results]
    latencies = [r['latency'] for r in results]
    req_tpss = [r['tps'] for r in results]
    total_tokens = sum(r['tokens'] for r in results)
    
    # 系统总吞吐 (Tokens / Wall Time)
    system_tps = total_tokens / total_wall_time
    # 系统 QPS (Requests / Wall Time)
    system_qps = len(results) / total_wall_time

    print(f"\n📊 Detailed Statistics (Concurrency {concurrency})")
    print("-" * 80)
    
    print_stats_table("TTFT", ttfts, "s")
    print_stats_table("ITL", itls, "s")
    print_stats_table("Latency", latencies, "s")
    print_stats_table("Req TPS", req_tpss, "")
    
    print("-" * 80)
    print(f"   Total Generated Tokens : {total_tokens}")
    print(f"   Total Wall Time        : {total_wall_time:.2f} s")
    print(f"   System QPS             : {system_qps:.2f} req/s")
    print(f"   System Throughput      : {system_tps:.2f} tokens/s")
    print("-" * 80)

if __name__ == "__main__":
    for c in CONCURRENCY_LEVELS:
        run_benchmark(c)
        time.sleep(3)

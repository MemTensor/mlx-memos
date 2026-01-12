import requests
import json
import time

def verify_server():
    url = "http://127.0.0.1:8080/v1/chat/completions"
    headers = {"Content-Type": "application/json"}
    
    # 这里的 model 参数值通常不影响 MLX Server 的实际运行模型，但为了规范还是填上
    data = {
        "model": "Qwen3-14B-MLX",
        "messages": [
            {"role": "user", "content": "你好，请简要介绍一下你自己。"}
        ],
        "temperature": 0.7,
        "max_tokens": 200,
        "stream": False
    }

    print(f"🚀 Sending verification request to {url}...")
    start_time = time.time()
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=120) # 第一次请求可能较慢（加载模型/预热）
        response.raise_for_status()
        
        elapsed = time.time() - start_time
        print(f"⏱️  Request took {elapsed:.2f} seconds")
        
        result = response.json()
        
        print("\n✅ Response received (JSON):")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # 提取内容
        choices = result.get("choices", [])
        if choices:
            content = choices[0].get("message", {}).get("content", "")
            print(f"\n📝 Decoded Content:\n{content}")
            if content:
                print("\n✅ Verification SUCCESS!")
            else:
                print("\n⚠️  Verification warning: Empty content.")
        else:
            print("\n⚠️  No choices in response.")
            
    except requests.exceptions.ConnectionError:
        print("\n❌ Connection Error: Is the server running on port 8080?")
        print("💡 Try running: ./start_mlx_server.sh restart")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    verify_server()

import requests
import json

api_key = "sk-fqtorqeqoafdilkroppjlcidwphfjtkdqdsslzvcgysbqwap"
api_base = "https://api.siliconflow.cn/v1"

# 要测试的模型列表
models = [
    "deepseek-ai/deepseek-coder-6.7b-instruct",
    "deepseek-ai/deepseek-math-7b-instruct",
    "deepseek-ai/deepseek-moe-16b-chat",
    "deepseek-ai/DeepSeek-V2.5"
]

# 准备请求数据
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

def test_model(model_name):
    print(f"\n测试模型: {model_name}")
    print("-" * 50)
    
    data = {
        "model": model_name,
        "messages": [{"role": "user", "content": "你好，请做个简单的自我介绍"}]
    }

    try:
        # 发送请求
        response = requests.post(
            f"{api_base}/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        
        # 打印响应信息
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
    except Exception as e:
        print(f"错误: {str(e)}")

# 测试所有模型
for model in models:
    test_model(model)

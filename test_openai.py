from openai import OpenAI
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 获取环境变量
api_key = os.getenv("SF_API_KEY")
api_base = os.getenv("SF_API_BASE_URL")

# 要测试的模型列表
models = [
    "chatglm_pro",
    "chatglm_std",
    "chatglm_lite"
]

def test_model(model_name):
    print(f"\n测试模型: {model_name}")
    print("-" * 50)
    
    try:
        # 创建客户端
        client = OpenAI(
            api_key=api_key,
            base_url=api_base
        )
        
        # 发送请求
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": "你好，请做个简单的自我介绍"}],
            stream=False
        )
        
        # 打印响应
        print("响应内容:")
        print(response.choices[0].message.content)
        
    except Exception as e:
        print(f"错误: {str(e)}")

# 测试所有模型
for model in models:
    test_model(model)

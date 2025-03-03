import requests
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 获取环境变量
api_key = os.getenv("SF_API_KEY")
api_base = os.getenv("SF_API_BASE_URL")

# 准备请求
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

try:
    # 获取模型列表
    response = requests.get(
        f"{api_base}/models",
        headers=headers
    )
    
    # 打印响应
    print(f"状态码: {response.status_code}")
    print("\n响应内容:")
    print(response.text)
    
except Exception as e:
    print(f"错误: {str(e)}")

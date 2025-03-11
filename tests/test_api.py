import requests
import json
import time

def print_response(response, title):
    """打印响应内容"""
    print(f"\n{'='*20} {title} {'='*20}")
    print(f"状态码: {response.status_code}")
    
    try:
        content = response.json()
        print("\n响应内容:")
        for key, value in content.items():
            print(f"\n{key}:")
            if isinstance(value, (dict, list)):
                print(json.dumps(value, ensure_ascii=False, indent=2))
            else:
                print(value)
    except Exception as e:
        print(f"解析响应时出错: {e}")
        print("原始响应:", response.text)

def test_chat():
    """测试聊天接口"""
    url = "http://localhost:8000/api/v1/chat"
    headers = {"Content-Type": "application/json"}
    data = {
        "message": "你好，请介绍一下你自己",
        "version": "api"
    }
    
    response = requests.post(url, headers=headers, json=data)
    print_response(response, "测试聊天接口")

def test_load_dsl():
    """测试加载DSL功能"""
    url = "http://localhost:8000/api/v1/load_dsl"
    headers = {"Content-Type": "application/json"}
    
    # 创建一个包含items的复杂DSL
    complex_dsl = {
        "id": "674",
        "name": "关键词生成页面新设计",
        "type": "app",
        "tenantId": "PGY02019_S0000000_ST00000000_U00000000_EQ000000000000_MP0000000",
        "items": [
            {
                "id": "edoms_page_new_design",
                "type": "page",
                "layout": "absolute",
                "style": {
                    "width": "100%",
                    "height": "100%",
                    "position": "relative",
                    "top": 0,
                    "left": 0,
                    "visibility": "",
                    "backgroundColor": "rgba(240, 240, 240, 1)"
                },
                "name": "主页",
                "items": [
                    {
                        "id": "edoms_container_top_bar",
                        "type": "container",
                        "layout": "absolute",
                        "style": {
                            "width": "100%",
                            "height": "80px",
                            "position": "absolute",
                            "top": 0,
                            "left": 0,
                            "backgroundColor": "#004D7F",
                            "zIndex": "1000",
                            "borderRadius": "0px 0px 12px 12px",
                            "boxShadow": "0 4px 6px rgba(0, 0, 0, 0.1)"
                        },
                        "name": "顶部导航条",
                        "items": [
                            {
                                "id": "edoms_text_logo",
                                "type": "text",
                                "style": {
                                    "width": "300px",
                                    "height": "40px",
                                    "fontSize": "24px",
                                    "color": "#ffffff",
                                    "lineHeight": "40px",
                                    "textAlign": "center",
                                    "fontWeight": "bold",
                                    "position": "absolute",
                                    "left": "50%",
                                    "top": "20px",
                                    "transform": "translateX(-50%)"
                                },
                                "name": "Logo",
                                "text": "智慧园区",
                                "multiple": True,
                                "tag": "h1"
                            }
                        ]
                    }
                ]
            }
        ]
    }
    
    data = {
        "dsl_content": json.dumps(complex_dsl),
        "version": "api"
    }
    
    # 加载DSL
    response = requests.post(url, headers=headers, json=data)
    print_response(response, "测试加载DSL")
    
    # 等待一秒确保DSL已加载
    time.sleep(1)
    
    # 分析DSL结构
    chat_url = "http://localhost:8000/api/v1/chat"
    chat_data = {
        "message": "请分析当前DSL的结构",
        "version": "api"
    }
    
    response = requests.post(chat_url, headers=headers, json=chat_data)
    print_response(response, "测试DSL分析")

if __name__ == "__main__":
    print("开始测试DSL助手API...")
    test_chat()
    print("\n等待3秒后继续测试...")
    time.sleep(3)
    test_load_dsl()
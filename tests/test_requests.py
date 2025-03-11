import requests
import json
import time
import sys

BASE_URL = "http://localhost:8000"

def wait_for_server(timeout=30):
    """等待服务器启动"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"{BASE_URL}/docs")
            if response.status_code == 200:
                print("服务器已启动")
                return True
            time.sleep(1)
        except requests.exceptions.ConnectionError:
            print("等待服务器启动...", end="\r")
            time.sleep(1)
    print("\n服务器启动超时")
    return False

def print_response(response, test_name):
    """格式化打印响应"""
    print(f"\n=== {test_name} ===")
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        try:
            result = response.json()
            print("\n响应内容:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            if "response_type" in result:
                print(f"\n响应类型: {result.get('response_type')}")
        except json.JSONDecodeError as e:
            print(f"解析响应失败: {str(e)}")
            print("原始响应:", response.text)
    else:
        print("错误响应:", response.text)
    
    print("-" * 80)

def test_load_dsl():
    """测试加载DSL"""
    dsl = {
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
    
    response = requests.post(
        f"{BASE_URL}/load_dsl",
        json={"dsl_content": json.dumps(dsl), "version": "api"}
    )
    print_response(response, "测试加载DSL")
    return response.status_code == 200

def test_chat_analysis():
    """测试分析DSL结构（文本响应）"""
    response = requests.post(
        f"{BASE_URL}/chat",
        json={"message": "分析一下当前DSL的结构", "version": "api"}
    )
    print_response(response, "测试分析DSL结构")
    return response.status_code == 200

def test_chat_modification():
    """测试DSL修改（JSON响应）"""
    response = requests.post(
        f"{BASE_URL}/chat",
        json={"message": "将顶部导航条的高度改为100px", "version": "api"}
    )
    print_response(response, "测试DSL修改")
    return response.status_code == 200

def test_chat_question():
    """测试普通问题（文本响应）"""
    response = requests.post(
        f"{BASE_URL}/chat",
        json={"message": "这个DSL是用来做什么的？", "version": "api"}
    )
    print_response(response, "测试普通问题")
    return response.status_code == 200

def test_history():
    """测试获取历史记录"""
    response = requests.get(f"{BASE_URL}/history?version=api")
    print_response(response, "测试获取历史记录")
    return response.status_code == 200

def test_clear_history():
    """测试清空历史记录"""
    response = requests.post(f"{BASE_URL}/clear_history?version=api")
    print_response(response, "测试清空历史记录")
    return response.status_code == 200

def main():
    """运行所有测试"""
    if not wait_for_server():
        sys.exit(1)
    
    tests = [
        ("加载DSL", test_load_dsl),
        ("分析DSL结构", test_chat_analysis),
        ("修改DSL", test_chat_modification),
        ("普通问题", test_chat_question),
        ("获取历史记录", test_history),
        ("清空历史记录", test_clear_history)
    ]
    
    results = []
    for name, test in tests:
        try:
            success = test()
            results.append((name, "成功" if success else "失败"))
            time.sleep(1)  # 在测试之间添加延迟
        except Exception as e:
            print(f"测试出错: {str(e)}")
            results.append((name, "错误"))
    
    print("\n=== 测试结果汇总 ===")
    all_success = True
    for name, result in results:
        print(f"{name}: {result}")
        if result != "成功":
            all_success = False
    
    sys.exit(0 if all_success else 1)

if __name__ == "__main__":
    main()

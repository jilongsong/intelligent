"""
测试 LangChain 集成功能
"""
import json
import asyncio
from chat_model import DSLAssistant

async def test_dsl_assistant():
    print("开始测试 DSL 助手...")
    assistant = DSLAssistant()
    
    # 测试 1: 加载 DSL
    print("\n1. 测试加载 DSL...")
    test_dsl = {
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
    
    success = assistant.load_dsl(json.dumps(test_dsl))
    print(f"DSL 加载结果: {'成功' if success else '失败'}")
    
    # 测试 2: 基本对话
    print("\n2. 测试基本对话...")
    test_messages = [
        "你好，请帮我分析当前 DSL 的结构",
        "请帮我修改顶部导航条的背景颜色为深蓝色 (#001F3F)",
        "在顶部导航条中添加一个搜索框",
        "请把 Logo 文字改为'智慧园区管理系统'"
    ]
    
    for message in test_messages:
        print(f"\n发送消息: {message}")
        try:
            response = await assistant.process_request(message)
            print(f"助手回复: {response}")
        except Exception as e:
            print(f"错误: {str(e)}")
    
    # 测试 3: 获取对话历史
    print("\n3. 测试获取对话历史...")
    history = assistant.get_chat_history()
    print(f"对话历史条数: {len(history)}")
    
    # 测试 4: 错误处理
    print("\n4. 测试错误处理...")
    try:
        success = assistant.load_dsl("invalid json")
        print("应该抛出异常但没有")
    except Exception as e:
        print(f"正确捕获到异常: {str(e)}")

async def main():
    await test_dsl_assistant()

if __name__ == "__main__":
    asyncio.run(main())

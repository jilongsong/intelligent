import os
import sys
import json
import pytest
import logging

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.dsl_assistant_api import DSLAssistantAPI, DSLError

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_dsl_assistant_api():
    try:
        # 创建DSL助手实例
        assistant = DSLAssistantAPI()
        
        # 测试用的简单DSL
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
        
        # 测试1: 加载DSL
        logger.info("\n=== 测试1: 加载DSL ===")
        success = assistant.load_dsl(json.dumps(test_dsl))
        assert success, "DSL加载失败"
        logger.info("DSL加载成功")
        
        # 测试2: 发送消息
        logger.info("\n=== 测试2: 发送消息 ===")
        response = assistant.process_request("分析一下这个DSL的结构")
        assert response, "没有收到响应"
        logger.info(f"收到响应: {response}")
        
        # 测试3: 获取历史记录
        logger.info("\n=== 测试3: 获取历史记录 ===")
        history = assistant.get_chat_history()
        assert len(history) > 0, "历史记录为空"
        logger.info(f"历史记录数量: {len(history)}")
        
        # 测试4: 清空历史记录
        logger.info("\n=== 测试4: 清空历史记录 ===")
        assistant.clear_history()
        history = assistant.get_chat_history()
        assert len(history) == 0, "历史记录未清空"
        logger.info("历史记录已清空")
        
        # 测试5: 获取完整DSL
        logger.info("\n=== 测试5: 获取完整DSL ===")
        complete_dsl = assistant.get_complete_dsl()
        assert complete_dsl, "无法获取完整DSL"
        logger.info("成功获取完整DSL")
        
    except Exception as e:
        logger.error(f"测试过程中发生错误: {str(e)}")
        raise

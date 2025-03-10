"""
测试DSL助手API版本的功能
"""
import asyncio
import json
import logging
from dsl_assistant_api import DSLAssistantAPI, DSLError

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_dsl_assistant():
    try:
        # 初始化DSL助手
        logger.info("初始化DSL助手")
        assistant = DSLAssistantAPI()
        
        # 测试用的简单DSL
        test_dsl = {
            "type": "container",
            "children": [
                {
                    "type": "text",
                    "content": "Hello World"
                }
            ]
        }
        
        # 测试1: 加载DSL
        logger.info("\n=== 测试1: 加载DSL ===")
        try:
            success = assistant.load_dsl(json.dumps(test_dsl))
            logger.info(f"DSL加载结果: {'成功' if success else '失败'}")
        except DSLError as e:
            logger.error(f"加载DSL失败: {str(e)}")
        
        # 测试2: 处理简单请求
        logger.info("\n=== 测试2: 处理简单请求 ===")
        test_request = "将文本内容改为'你好，世界'"
        try:
            result = await assistant.process_request(test_request)
            if isinstance(result, dict):
                logger.info("处理成功，结果:")
                print(json.dumps(result, indent=2, ensure_ascii=False))
            else:
                logger.error(f"处理失败: {result}")
        except Exception as e:
            logger.error(f"处理请求时出错: {str(e)}")
        
        # 测试3: 获取对话历史
        logger.info("\n=== 测试3: 获取对话历史 ===")
        history = assistant.get_chat_history()
        logger.info("对话历史:")
        for msg in history:
            print(f"{msg['role']}: {msg['content'][:100]}...")
        
        # 测试4: 清空历史
        logger.info("\n=== 测试4: 清空历史 ===")
        assistant.clear_history()
        history = assistant.get_chat_history()
        logger.info(f"清空后的历史记录数: {len(history)}")
        
    except Exception as e:
        logger.error(f"测试过程中发生错误: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_dsl_assistant())

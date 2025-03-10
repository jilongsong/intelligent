"""
智能 DSL 助手 - API 版本
直接使用 API 调用实现 DSL 文件的智能理解和编辑

主要功能：
1. 加载和解析DSL文件
2. 根据用户自然语言指令修改DSL
3. 维护对话历史
4. 确保DSL的完整性和正确性
"""
from typing import List, Dict, Optional, Union, Any
import json
import requests
import os
from dotenv import load_dotenv
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()

class DSLError(Exception):
    """DSL处理相关的自定义异常"""
    pass

class DSLAssistantAPI:
    def __init__(self, model_name: str = "qwq-32b"):
        """
        初始化 DSL 助手
        
        Args:
            model_name: 要使用的模型名称
        """
        self.api_key = os.getenv("SF_API_KEY")
        if not self.api_key:
            raise ValueError("未找到API密钥，请确保在.env文件中设置SF_API_KEY")
            
        self.api_base = "http://192.100.8.139:8080/v1"
        self.model_name = model_name
        
        # 设置API请求头
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # 系统提示词
        self.system_prompt = """你是一个专业的低代码平台 DSL 助手。你的主要职责是：
1. 理解用户提供的 DSL 结构，并确保修改后保持完整性
2. 根据用户的自然语言描述精准修改 DSL
3. 确保返回的 DSL 100% 符合 JSON 语法，避免任何格式错误, **杜绝掺杂注释**

**重要规则（必须严格遵守）：**
1. **严禁丢失任何字段**，尤其是 `image`、`src`、`url` 等图片地址和资源路径
2. **保证 DSL 结构完整**，修改时不可删除未要求删除的字段
3. **必须返回标准 JSON 格式**，不能包含任何形式的注释（如 `//`、`/* */`、`#`）
4. **确保 DSL 可用**，不能返回格式错误、字段丢失、重复键名、或结构损坏的 JSON
5. **确保数据一致性**，特别是图片资源、引用 ID 和层级关系不能被误改
6. **只返回完整的 JSON**，不能有额外的说明、解释或文本
7. **DSL 不能被重新格式化为 Markdown 或其他格式**，只能是纯 JSON
"""
        
        # 对话历史
        self.chat_history: List[Dict[str, str]] = []
        
        # 当前加载的 DSL 内容
        self.current_dsl: Optional[Dict] = None
        
        logger.info(f"DSL助手初始化完成，使用模型: {model_name}")

    def _validate_dsl(self, dsl: Dict) -> bool:
        """
        验证DSL的基本结构是否正确
        
        Args:
            dsl: 要验证的DSL字典
            
        Returns:
            bool: DSL是否有效
        """
        # 这里可以添加更多的验证规则
        required_fields = ["type"]
        return all(field in dsl for field in required_fields)

    def load_dsl(self, dsl_content: str) -> bool:
        """
        加载并解析 DSL 文件
        
        Args:
            dsl_content: DSL 文件内容
            
        Returns:
            bool: 是否成功加载
            
        Raises:
            DSLError: 当DSL解析或验证失败时
        """
        try:
            logger.info("开始加载DSL文件")
            
            # 清空对话历史
            self.chat_history = []
            
            # 解析DSL
            parsed_dsl = json.loads(dsl_content)
            
            # 验证DSL结构
            if not self._validate_dsl(parsed_dsl):
                raise DSLError("DSL结构验证失败，缺少必要字段")
            
            self.current_dsl = parsed_dsl
            
            # 将 DSL 加载事件添加到对话历史
            self.chat_history.append({
                "role": "user",
                "content": f"我已经加载了以下 DSL:\n{json.dumps(self.current_dsl, indent=2, ensure_ascii=False)}"
            })
            self.chat_history.append({
                "role": "assistant",
                "content": "DSL 已成功加载，我可以帮您分析和修改它。"
            })
            
            logger.info("DSL文件加载成功")
            return True
            
        except json.JSONDecodeError as e:
            logger.error(f"DSL解析错误: {str(e)}")
            raise DSLError(f"DSL JSON解析失败: {str(e)}")
        except Exception as e:
            logger.error(f"加载DSL时发生未知错误: {str(e)}")
            raise

    async def process_request(self, user_input: str) -> Union[Dict[str, Any], str]:
        """
        处理用户请求，并返回完整、严格的 DSL JSON 格式
        
        Args:
            user_input: 用户输入的消息
            
        Returns:
            Union[Dict[str, Any], str]: 成功时返回修改后的DSL字典，失败时返回错误信息
            
        Raises:
            DSLError: 当处理请求过程中发生DSL相关错误时
        """
        try:
            logger.info(f"开始处理用户请求: {user_input[:100]}...")
            
            # 准备完整的消息历史
            messages = [
                {"role": "system", "content": self.system_prompt}
            ]
            messages.extend(self.chat_history)
            messages.append({"role": "user", "content": user_input})
            
            # 准备API请求数据
            data = {
                "model": self.model_name,
                "messages": messages,
                "temperature": 0.3
            }
            
            # 发送API请求
            logger.info("发送API请求")
            start_time = datetime.now()
            
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers=self.headers,
                json=data,
                timeout=60
            )
            
            process_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"API请求完成，耗时: {process_time:.2f}秒")
            
            if response.status_code != 200:
                error_msg = f"API请求失败，状态码: {response.status_code}, 错误信息: {response.text}"
                logger.error(error_msg)
                raise DSLError(error_msg)
            
            # 解析响应
            result = response.json()
            print(result)
            raw_output = result["choices"][0]["message"]["content"]
            
            # 提取 JSON 格式的 DSL
            json_start = raw_output.find("{")
            json_end = raw_output.rfind("}") + 1
            
            if json_start == -1 or json_end == -1:
                raise DSLError("无法从响应中提取有效的JSON")
            
            dsl_json_str = raw_output[json_start:json_end]
            
            # 确保返回合法 JSON
            modified_dsl = json.loads(dsl_json_str)
            
            # 验证修改后的DSL
            if not self._validate_dsl(modified_dsl):
                raise DSLError("修改后的DSL结构验证失败")
            
            # 更新当前 DSL 和对话历史
            self.current_dsl = modified_dsl
            self.chat_history.append({"role": "user", "content": user_input})
            self.chat_history.append({"role": "assistant", "content": raw_output})
            
            logger.info("请求处理成功")
            return self.current_dsl
            
        except requests.RequestException as e:
            error_msg = f"API请求异常: {str(e)}"
            logger.error(error_msg)
            return error_msg
        except json.JSONDecodeError as e:
            error_msg = f"JSON解析错误: {str(e)}"
            logger.error(error_msg)
            return error_msg
        except DSLError as e:
            logger.error(str(e))
            return str(e)
        except Exception as e:
            error_msg = f"处理请求时发生未知错误: {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    def get_chat_history(self) -> List[Dict[str, str]]:
        """
        获取对话历史
        
        Returns:
            List[Dict[str, str]]: 对话历史记录，每条记录包含role和content
        """
        return self.chat_history
        
    def clear_history(self) -> None:
        """清空对话历史"""
        self.chat_history = []
        logger.info("对话历史已清空")

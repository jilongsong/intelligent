"""
智能 DSL 助手 - API 版本
直接使用 API 调用实现 DSL 文件的智能理解和编辑
"""
from typing import List, Dict, Optional, Union, Any, Tuple
import json
import requests
import os
from dotenv import load_dotenv
import logging
from datetime import datetime
import copy
import time

# 配置日志
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()

class DSLError(Exception):
    """DSL处理相关的自定义异常"""
    pass

class DSLAssistantAPI:
    def __init__(self, model_name: str = os.getenv("LOCAL_MODEL_NAME")):
        """
        初始化 DSL 助手
        
        Args:
            model_name: 要使用的模型名称
        """
        self.api_key = os.getenv("LOCAL_MODEL_API_KEY")
        self.api_base = os.getenv("LOCAL_MODEL_API_BASE")
        self.model_name = model_name
        
        # 设置API请求头
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # 系统提示词
        self.system_prompt = """你是一个专业的低代码平台 DSL 助手。"""
        
        # 对话历史
        self.chat_history: List[Dict[str, str]] = []
        
        # 当前加载的 DSL 内容
        self.current_dsl: Optional[Dict] = None
        
        # 分离的子级DSL内容
        self.separated_items: Dict[str, List[Dict]] = {}
        
        logger.info(f"DSL助手初始化完成，使用模型: {model_name}")

    def _send_api_request(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> Optional[Dict[str, Any]]:
        """
        发送API请求到语言模型服务，包含重试机制
        
        Args:
            messages: 对话消息列表
            temperature: 温度参数，控制输出的随机性
            
        Returns:
            Optional[Dict[str, Any]]: API响应数据，如果请求失败则返回None
        """
        max_retries = 3
        retry_delay = 5  # 重试间隔秒数
        
        for attempt in range(max_retries):
            try:
                payload = {
                    "model": self.model_name,
                    "messages": messages,
                    "temperature": temperature
                }
                
                logger.info(f"正在发送API请求到 {self.api_base}，第 {attempt + 1} 次尝试")
                
                response = requests.post(
                    f"{self.api_base}/chat/completions",
                    headers=self.headers,
                    json=payload,
                    timeout=60  # 增加超时时间到60秒
                )
                
                response.raise_for_status()
                result = response.json()
                
                if "choices" in result and len(result["choices"]) > 0:
                    return {"text": result["choices"][0]["message"]["content"]}
                else:
                    logger.error("API响应格式不正确")
                    return None
                    
            except requests.exceptions.Timeout:
                logger.warning(f"请求超时 (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                else:
                    logger.error("连接模型服务器超时，请检查网络连接或服务器状态")
                    return None
                    
            except requests.exceptions.ConnectionError:
                logger.warning(f"连接错误 (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                else:
                    logger.error(f"无法连接到模型服务器 {self.api_base}，请检查服务器地址是否正确")
                    return None
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"API请求失败: {str(e)}")
                return None
                
            except Exception as e:
                logger.error(f"处理API响应时发生错误: {str(e)}")
                return None

    def _validate_dsl(self, dsl: Dict) -> bool:
        """
        验证DSL的基本结构是否正确
        
        Args:
            dsl: 要验证的DSL字典
            
        Returns:
            bool: DSL是否有效
        """
        required_fields = ["type"]
        return all(field in dsl for field in required_fields)

    def _separate_items(self, dsl: Dict, path: str = "") -> Tuple[Dict, Dict[str, List[Dict]]]:
        """
        分离DSL中的items节点
        
        Args:
            dsl: DSL字典
            path: 当前节点路径
            
        Returns:
            Tuple[Dict, Dict[str, List[Dict]]]: 返回处理后的DSL和分离出的items
        """
        result = copy.deepcopy(dsl)
        separated = {}
        
        # 处理当前节点的items
        if "items" in result:
            items = result.pop("items")
            current_path = f"{path}.items" if path else "items"
            separated[current_path] = items
        
        # 递归处理children
        if "children" in result:
            for i, child in enumerate(result["children"]):
                child_path = f"{path}.children[{i}]" if path else f"children[{i}]"
                processed_child, child_items = self._separate_items(child, child_path)
                result["children"][i] = processed_child
                separated.update(child_items)
        
        return result, separated

    def _combine_items(self, dsl: Dict, items: Dict[str, List[Dict]], path: str = "") -> Dict:
        """
        重新组合DSL和items
        
        Args:
            dsl: 处理后的DSL
            items: 分离的items
            path: 当前节点路径
            
        Returns:
            Dict: 组合后的完整DSL
        """
        result = copy.deepcopy(dsl)
        
        # 处理当前节点的items
        current_path = f"{path}.items" if path else "items"
        if current_path in items:
            result["items"] = items[current_path]
        
        # 递归处理children
        if "children" in result:
            for i, child in enumerate(result["children"]):
                child_path = f"{path}.children[{i}]" if path else f"children[{i}]"
                result["children"][i] = self._combine_items(child, items, child_path)
        
        return result

    def load_dsl(self, dsl_content: str) -> bool:
        """
        加载并解析 DSL 文件，同时分离items节点
        
        Args:
            dsl_content: DSL 文件内容
            
        Returns:
            bool: 是否成功加载
        """
        try:
            logger.info("开始加载DSL文件")
            
            # 清空对话历史和分离的items
            self.chat_history = []
            self.separated_items = {}
            
            # 解析DSL
            parsed_dsl = json.loads(dsl_content)
            
            # 验证DSL结构
            if not self._validate_dsl(parsed_dsl):
                raise DSLError("DSL结构验证失败，缺少必要字段")
            
            # 分离items
            self.current_dsl, self.separated_items = self._separate_items(parsed_dsl)
            
            # 将 DSL 加载事件添加到对话历史
            self.chat_history.append({
                "role": "user",
                "content": f"我已经加载了以下 DSL:\n{json.dumps(self.current_dsl, indent=2, ensure_ascii=False)}"
            })
            self.chat_history.append({
                "role": "assistant",
                "content": "DSL 已成功加载，我可以帮您分析和修改它。"
            })
            
            logger.info(f"DSL文件加载成功，分离出 {len(self.separated_items)} 个items节点")
            return True
            
        except json.JSONDecodeError as e:
            logger.error(f"DSL解析错误: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"加载DSL时发生未知错误: {str(e)}")
            return False

    def get_complete_dsl(self) -> Dict:
        """
        获取完整的DSL（包含items）
        
        Returns:
            Dict: 完整的DSL
        """
        if not self.current_dsl:
            return {}
        return self._combine_items(self.current_dsl, self.separated_items)

    def _format_dsl_structure(self) -> str:
        """
        格式化DSL结构信息
        
        Returns:
            str: 格式化后的DSL结构描述
        """
        if not self.current_dsl:
            return "当前没有加载任何DSL文件"
            
        lines = []
        lines.append(f"当前DSL的结构如下：")
        lines.append(f"1. 根节点类型为 {self.current_dsl['type']}")
        
        if "children" in self.current_dsl:
            for i, child in enumerate(self.current_dsl["children"], 1):
                lines.append(f"{i}. 子节点 {i} 类型为 {child['type']}")
                if "content" in child:
                    lines.append(f"   - 内容：{child['content']}")
                if "children" in child:
                    for j, grandchild in enumerate(child["children"], 1):
                        lines.append(f"   {i}.{j}. 子节点类型为 {grandchild['type']}")
                        if "content" in grandchild:
                            lines.append(f"      - 内容：{grandchild['content']}")
        
        if self.separated_items:
            lines.append("\n分离的items节点：")
            for path, items in self.separated_items.items():
                lines.append(f"- {path}: 包含 {len(items)} 个项目")
                for i, item in enumerate(items[:3], 1):
                    lines.append(f"  {i}. 类型：{item['type']}")
                    if "content" in item:
                        lines.append(f"     - 内容：{item['content']}")
                    elif "label" in item:
                        lines.append(f"     - 标签：{item['label']}")
                if len(items) > 3:
                    lines.append(f"  ... 还有 {len(items) - 3} 个项目")
        
        return "\n".join(lines)

    def process_request(self, message: str) -> str:
        """
        处理用户请求，根据内容类型返回不同格式的响应：
        - 如果是普通对话，返回字符串
        - 如果是DSL修改，返回JSON格式的DSL
        
        Args:
            message: 用户输入的消息
            
        Returns:
            str: 助手的响应消息或JSON字符串
        """
        try:
            logger.info(f"开始处理用户请求: {message[:100]}...")
            
            # 根据当前状态生成响应
            if not self.current_dsl:
                return "你好！我是DSL智能助手，我可以帮助你理解和修改DSL结构。目前没有加载任何DSL文件，你可以先使用load_dsl接口加载一个DSL文件。"
            
            if "分析" in message or "结构" in message:
                return self._format_dsl_structure()
            
            # 准备API请求
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            # 构建系统提示词
            system_prompt = """你是一个专业的低代码平台 DSL 助手。你的主要职责是：
1. 理解用户提供的 DSL 结构，并确保修改后保持完整性
2. 根据用户的自然语言描述精准修改 DSL
3. 确保返回的 DSL 100% 符合 JSON 语法，避免任何格式错误

**重要规则：**
1. 如果用户要求修改DSL，你必须返回完整的JSON格式DSL
2. 如果是普通对话（如询问、分析等），你应该返回普通文本
3. 严禁在JSON中添加任何注释
4. 确保返回的JSON中所有字段完整且正确

**处理原则：**
1. 修改DSL时：返回完整的JSON，不要有任何额外说明
2. 普通对话时：返回清晰的文本描述，不要包含JSON
3. 分析DSL时：返回结构化的文本描述，不要包含JSON"""
            
            # 构建对话历史
            messages = [{"role": "system", "content": system_prompt}]
            
            # 添加DSL上下文
            dsl_context = f"当前DSL结构:\n{json.dumps(self.current_dsl, indent=2, ensure_ascii=False)}"
            messages.append({"role": "assistant", "content": dsl_context})
            
            # 添加历史消息
            messages.extend(self.chat_history)
            
            # 添加当前用户消息
            messages.append({"role": "user", "content": message})
            
            # 发送请求
            response = self._send_api_request(
                messages=messages,
                temperature=0.3  # 降低温度以获得更确定性的输出
            )
            
            if not response:
                return "抱歉，处理请求时出现错误。"
            
            # 解析响应
            raw_output = response.get("text", "")
            
            # 检查是否包含JSON结构
            json_start = raw_output.find("{")
            json_end = raw_output.rfind("}") + 1
            
            if json_start != -1 and json_end != -1:
                try:
                    # 尝试解析JSON
                    dsl_json_str = raw_output[json_start:json_end]
                    modified_dsl = json.loads(dsl_json_str)
                    
                    # 验证是否是有效的DSL
                    if self._validate_dsl(modified_dsl):
                        # 更新DSL
                        self.current_dsl, self.separated_items = self._separate_items(modified_dsl)
                        
                        # 更新对话历史
                        self.chat_history.append({"role": "user", "content": message})
                        self.chat_history.append({"role": "assistant", "content": json.dumps(modified_dsl, ensure_ascii=False)})
                        
                        return json.dumps(modified_dsl, ensure_ascii=False, indent=2)
                except json.JSONDecodeError:
                    # 如果不是有效的JSON，当作普通对话处理
                    pass
            
            # 处理为普通对话
            # 移除可能的JSON格式内容
            if json_start != -1 and json_end != -1:
                conversation_text = raw_output[:json_start].strip() + " " + raw_output[json_end:].strip()
            else:
                conversation_text = raw_output.strip()
            
            # 更新对话历史
            self.chat_history.append({"role": "user", "content": message})
            self.chat_history.append({"role": "assistant", "content": conversation_text})
            
            return conversation_text
            
        except Exception as e:
            error_msg = f"处理请求时发生错误: {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    def get_chat_history(self) -> List[Dict[str, str]]:
        """
        获取对话历史
        
        Returns:
            List[Dict[str, str]]: 对话历史记录
        """
        return self.chat_history
        
    def clear_history(self) -> None:
        """清空对话历史"""
        self.chat_history = []
        logger.info("对话历史已清空")

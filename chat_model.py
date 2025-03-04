"""
智能 DSL 助手
使用 LangChain 框架实现 DSL 文件的智能理解和编辑
"""
from typing import List, Dict, Optional
import os
import json
from dotenv import load_dotenv
from langchain_community.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import LLMChain
from langchain.tools import Tool
from langchain.agents import initialize_agent, AgentType

# 加载环境变量
load_dotenv()

class DSLAssistant:
    def __init__(self, model_name: str = "Qwen/Qwen2.5-72B-Instruct"):
        """初始化 DSL 助手"""
        self.api_key = os.getenv("SF_API_KEY")
        self.api_base = os.getenv("SF_API_BASE_URL")
        
        # 初始化聊天模型
        self.chat = ChatOpenAI(
            model_name=model_name,
            openai_api_key=self.api_key,
            openai_api_base=self.api_base,
            temperature=0.3,  # 降低温度以获得更确定性的输出
        )
        
        # 创建系统提示词
        system_prompt = """你是一个专业的低代码平台 DSL 助手。你的主要职责是：
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
        
        # 初始化记忆系统
        self.memory = ConversationBufferMemory(
            return_messages=True,
            memory_key="chat_history"
        )
        
        # 创建基本对话链
        self.chain = LLMChain(
            llm=self.chat,
            prompt=ChatPromptTemplate.from_messages([
                SystemMessage(content=system_prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}")
            ]),
            memory=self.memory,
            verbose=True
        )
        
        # 当前加载的 DSL 内容
        self.current_dsl: Optional[Dict] = None
    
    def load_dsl(self, dsl_content: str) -> bool:
        """
        加载并解析 DSL 文件
        
        Args:
            dsl_content: DSL 文件内容
            
        Returns:
            bool: 是否成功加载
        """
        try:
            self.current_dsl = json.loads(dsl_content)
            # 将 DSL 加载事件添加到对话历史
            self.memory.chat_memory.add_user_message(f"我已经加载了以下 DSL:\n{json.dumps(self.current_dsl, indent=2, ensure_ascii=False)}")
            self.memory.chat_memory.add_ai_message("DSL 已成功加载，我可以帮您分析和修改它。")
            return True
        except json.JSONDecodeError as e:
            print(f"DSL 解析错误: {str(e)}")
            return False
    
    async def process_request(self, user_input: str) -> str:
        """
        处理用户请求，并返回完整、严格的 DSL JSON 格式（JSON中不允许有注释）
        
        Args:
            user_input: 用户输入的消息
            
        Returns:
            str: 仅包含修改后的完整 DSL JSON
        """
        try:
            # 使用对话链处理请求
            response = await self.chain.ainvoke({"input": user_input})
            print(response)
            # return response["text"]
            raw_output = response["text"]
            # 提取 JSON 格式的 DSL
            json_start = raw_output.find("{")
            json_end = raw_output.rfind("}") + 1

            if json_start == -1 or json_end == -1:
                return "无法解析 DSL JSON，请检查输入。"

            dsl_json_str = raw_output[json_start:json_end]
            print(dsl_json_str)
            # 确保返回合法 JSON
            modified_dsl = json.loads(dsl_json_str)
            # 更新当前 DSL 并返回完整 DSL
            self.current_dsl = modified_dsl
            print(self.current_dsl)
            return self.current_dsl
            
        except Exception as e:
            return f"处理请求时发生错误: {str(e)}"
    
    def get_chat_history(self) -> List[Dict]:
        """
        获取对话历史
        
        Returns:
            List[Dict]: 对话历史记录
        """
        history = []
        for message in self.memory.chat_memory.messages:
            if isinstance(message, HumanMessage):
                history.append({"role": "user", "content": message.content})
            elif isinstance(message, AIMessage):
                history.append({"role": "assistant", "content": message.content})
        return history

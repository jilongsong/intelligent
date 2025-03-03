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
    def __init__(self, model_name: str = "deepseek-ai/DeepSeek-V2.5"):
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
1. 理解用户的 DSL 文件结构
2. 帮助用户根据自然语言描述修改 DSL
3. 确保生成的 DSL 符合规范和语法
4. 提供清晰的修改建议和解释

当处理 DSL 时，请遵循以下规则：
1. 保持 DSL 结构的完整性
2. 确保修改不会破坏现有的配置
3. 验证所有必需的字段都存在
4. 保持良好的格式化
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
        处理用户请求
        
        Args:
            user_input: 用户输入的消息
            
        Returns:
            str: 助手的回复
        """
        try:
            # 使用对话链处理请求
            response = await self.chain.ainvoke({"input": user_input})
            return response["text"]
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

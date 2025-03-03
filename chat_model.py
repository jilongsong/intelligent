"""
本地智能对话模型实现
使用 OpenAI SDK 调用 Silicon Flow API 实现智能对话功能
"""
from typing import List, Dict
import os
from dotenv import load_dotenv
from openai import OpenAI

# 加载环境变量
load_dotenv()

class ChatModel:
    def __init__(self, model_name: str = "deepseek-ai/DeepSeek-V2.5"):
        """初始化对话模型"""
        self.api_key = os.getenv("SF_API_KEY")
        self.api_base = os.getenv("SF_API_BASE_URL")
        self.model = model_name
        self.messages = []
        
        # 验证环境变量
        if not self.api_key or not self.api_base:
            raise ValueError("请确保设置了 SF_API_KEY 和 SF_API_BASE_URL 环境变量")
            
        # 初始化 OpenAI 客户端
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.api_base
        )
    
    def chat_with_model(self, message: str) -> str:
        """
        处理用户输入并返回响应
        
        Args:
            message: 用户输入的消息
            
        Returns:
            str: 模型的回复
        """
        try:
            # 添加用户消息到历史
            self.messages.append({"role": "user", "content": message})
            
            # 获取模型响应
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                stream=False
            )
            
            # 获取助手回复
            assistant_message = {
                "role": "assistant",
                "content": response.choices[0].message.content
            }
            
            # 添加助手消息到历史
            self.messages.append(assistant_message)
            
            return assistant_message["content"]
                
        except Exception as e:
            return f"发生错误: {str(e)}"
    
    def get_chat_history(self) -> List[Dict]:
        """
        获取对话历史
        
        Returns:
            List[Dict]: 对话历史记录
        """
        return self.messages

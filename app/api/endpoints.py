"""
API路由模块
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Literal, Any, Optional, Union
import logging
import json

from app.core.config import settings
from app.models.dsl_assistant_langchain import DSLAssistant
from app.models.dsl_assistant_api import DSLAssistantAPI

# 配置日志
logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter()

# 初始化两个版本的助手
langchain_assistant = DSLAssistant()
api_assistant = DSLAssistantAPI()

class ChatRequest(BaseModel):
    message: str = Field(..., description="用户的输入消息", min_length=1)
    version: Literal["langchain", "api"] = Field(
        default="api",
        description="使用的助手版本：langchain（LangChain版本）或api（直接API调用版本）"
    )

class DSLRequest(BaseModel):
    dsl_content: str = Field(..., description="DSL 文件内容", min_length=1)
    version: Literal["langchain", "api"] = Field(
        default="api",
        description="使用的助手版本：langchain（LangChain版本）或api（直接API调用版本）"
    )

class ChatResponse(BaseModel):
    """聊天响应模型，支持文本或DSL响应"""
    response: str = Field(..., description="助手的响应内容")
    response_type: Literal["text", "dsl"] = Field(..., description="响应类型：text（文本）或dsl（DSL JSON）")
    dsl: Optional[Dict] = Field(None, description="如果响应包含DSL修改，则返回完整的DSL")
    history: List[Dict[str, str]] = Field(..., description="对话历史记录")

class HistoryResponse(BaseModel):
    history: List[Dict[str, str]]

class DSLResponse(BaseModel):
    """DSL加载响应模型"""
    message: str = Field(..., description="操作结果消息")
    dsl: Optional[Dict] = Field(None, description="加载的DSL内容")

def get_assistant(version: str):
    """根据版本获取对应的助手实例"""
    if version == "langchain":
        return langchain_assistant
    return api_assistant

def is_json_response(response: str) -> bool:
    """
    判断响应是否是JSON格式
    """
    try:
        json_start = response.find("{")
        if json_start == -1:
            return False
        json_end = response.rfind("}") + 1
        json.loads(response[json_start:json_end])
        return True
    except json.JSONDecodeError:
        return False

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    处理用户聊天请求
    
    请求示例:
    {
        "message": "你好，请帮我分析一下当前的 DSL 结构",
        "version": "api"  // 可选，默认使用api版本
    }
    
    响应示例:
    {
        "response": "...",  // 响应内容
        "response_type": "text",  // 或 "dsl"
        "dsl": {...},  // 可选，当response_type为"dsl"时存在
        "history": [...]
    }
    """
    try:
        logger.info(f"收到聊天请求，使用{request.version}版本")
        assistant = get_assistant(request.version)
        response = assistant.process_request(request.message)  
        history = assistant.get_chat_history()
        
        # 判断响应类型
        response_type = "dsl" if is_json_response(response) else "text"
        
        # 获取完整的DSL（如果有）
        dsl = None
        if response_type == "dsl":
            if hasattr(assistant, "get_complete_dsl"):
                dsl = assistant.get_complete_dsl()
            else:
                # 如果响应是JSON格式但助手没有get_complete_dsl方法
                try:
                    dsl = json.loads(response)
                except json.JSONDecodeError:
                    pass
        
        # 使用JSONResponse以确保正确的编码
        return JSONResponse(
            content={
                "response": response,
                "response_type": response_type,
                "dsl": dsl,
                "history": history
            },
            media_type="application/json; charset=utf-8"
        )
    except Exception as e:
        logger.error(f"处理聊天请求时出错: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/load_dsl", response_model=DSLResponse)
async def load_dsl(request: DSLRequest):
    """
    加载 DSL 文件
    
    请求示例:
    {
        "dsl_content": "{\"type\": \"container\", \"children\": []}",
        "version": "api"  // 可选，默认使用api版本
    }
    
    响应示例:
    {
        "message": "DSL 加载成功",
        "dsl": {...}  // 加载的DSL内容
    }
    """
    try:
        logger.info(f"收到加载DSL请求，使用{request.version}版本")
        assistant = get_assistant(request.version)
        success = assistant.load_dsl(request.dsl_content)
        if not success:
            raise HTTPException(status_code=400, detail="DSL 格式无效")
        
        # 获取完整的DSL（如果有）
        dsl = None
        if hasattr(assistant, "get_complete_dsl"):
            dsl = assistant.get_complete_dsl()
        
        # 使用JSONResponse以确保正确的编码
        return JSONResponse(
            content={
                "message": "DSL 加载成功",
                "dsl": dsl
            },
            media_type="application/json; charset=utf-8"
        )
    except Exception as e:
        logger.error(f"加载DSL时出错: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history", response_model=HistoryResponse)
async def get_history(version: Literal["langchain", "api"] = "api"):
    """
    获取对话历史记录
    
    参数:
    - version: 使用的助手版本，可选值：langchain或api，默认为api
    """
    try:
        logger.info(f"获取历史记录，使用{version}版本")
        assistant = get_assistant(version)
        history = assistant.get_chat_history()
        
        # 使用JSONResponse以确保正确的编码
        return JSONResponse(
            content={"history": history},
            media_type="application/json; charset=utf-8"
        )
    except Exception as e:
        logger.error(f"获取历史记录时出错: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/clear_history")
async def clear_history(version: Literal["langchain", "api"] = "api"):
    """
    清空对话历史
    
    参数:
    - version: 使用的助手版本，可选值：langchain或api，默认为api
    """
    try:
        logger.info(f"清空历史记录，使用{version}版本")
        assistant = get_assistant(version)
        assistant.clear_history()
        return JSONResponse({"message": "历史记录已清空"})
    except Exception as e:
        logger.error(f"清空历史记录时出错: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
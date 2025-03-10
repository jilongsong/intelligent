"""
FastAPI 应用入口
提供 DSL 智能助手的 API 接口，支持多种模型后端
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Literal
from dsl_assistant_langchain import DSLAssistant
from dsl_assistant_api import DSLAssistantAPI
import uvicorn
import json
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="DSL 智能助手")

# 添加 CORS 支持
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    response: Dict
    history: List[Dict]

class HistoryResponse(BaseModel):
    history: List[Dict]

def get_assistant(version: str):
    """根据版本获取对应的助手实例"""
    if version == "langchain":
        return langchain_assistant
    return api_assistant

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理"""
    logger.error(f"发生错误: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": f"服务器错误: {str(exc)}"}
    )

@app.exception_handler(json.JSONDecodeError)
async def json_exception_handler(request: Request, exc: json.JSONDecodeError):
    """JSON 解析错误处理"""
    logger.error(f"JSON解析错误: {str(exc)}")
    return JSONResponse(
        status_code=400,
        content={"detail": f"JSON 格式错误: {str(exc)}"}
    )

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    处理用户聊天请求
    
    请求示例:
    {
        "message": "你好，请帮我分析一下当前的 DSL 结构",
        "version": "api"  // 可选，默认使用api版本
    }
    """
    try:
        logger.info(f"收到聊天请求，使用{request.version}版本")
        assistant = get_assistant(request.version)
        response = await assistant.process_request(request.message)
        history = assistant.get_chat_history()
        return ChatResponse(response=response, history=history)
    except Exception as e:
        logger.error(f"处理聊天请求时出错: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/load_dsl")
async def load_dsl(request: DSLRequest):
    """
    加载 DSL 文件
    
    请求示例:
    {
        "dsl_content": "{\"type\": \"container\", \"children\": []}",
        "version": "api"  // 可选，默认使用api版本
    }
    """
    try:
        logger.info(f"收到加载DSL请求，使用{request.version}版本")
        assistant = get_assistant(request.version)
        success = assistant.load_dsl(request.dsl_content)
        if not success:
            raise HTTPException(status_code=400, detail="DSL 格式无效")
        return {"message": "DSL 加载成功"}
    except json.JSONDecodeError as e:
        logger.error(f"DSL JSON解析错误: {str(e)}")
        raise HTTPException(status_code=400, detail=f"DSL JSON 格式错误: {str(e)}")
    except Exception as e:
        logger.error(f"加载DSL时出错: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history")
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
        return HistoryResponse(history=history)
    except Exception as e:
        logger.error(f"获取历史记录时出错: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/clear_history")
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
        return {"message": "历史记录已清空"}
    except Exception as e:
        logger.error(f"清空历史记录时出错: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    logger.info("启动DSL智能助手服务...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
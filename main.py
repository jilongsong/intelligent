"""
FastAPI 应用入口
提供 DSL 智能助手的 API 接口
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict
from chat_model import DSLAssistant
import uvicorn
import json

app = FastAPI(title="DSL 智能助手")

# 添加 CORS 支持
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

assistant = DSLAssistant()

class ChatRequest(BaseModel):
    message: str = Field(..., description="用户的输入消息", min_length=1)

class DSLRequest(BaseModel):
    dsl_content: str = Field(..., description="DSL 文件内容", min_length=1)

class ChatResponse(BaseModel):
    response: str
    history: List[Dict]

class HistoryResponse(BaseModel):
    history: List[Dict]

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理"""
    return JSONResponse(
        status_code=500,
        content={"detail": f"服务器错误: {str(exc)}"}
    )

@app.exception_handler(json.JSONDecodeError)
async def json_exception_handler(request: Request, exc: json.JSONDecodeError):
    """JSON 解析错误处理"""
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
        "message": "你好，请帮我分析一下当前的 DSL 结构"
    }
    """
    try:
        response = await assistant.process_request(request.message)
        history = assistant.get_chat_history()
        return ChatResponse(response=response, history=history)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/load_dsl")
async def load_dsl(request: DSLRequest):
    """
    加载 DSL 文件
    
    请求示例:
    {
        "dsl_content": "{\"type\": \"container\", \"children\": []}"
    }
    """
    try:
        success = assistant.load_dsl(request.dsl_content)
        if not success:
            raise HTTPException(status_code=400, detail="DSL 格式无效")
        return {"message": "DSL 加载成功"}
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"DSL JSON 格式错误: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history", response_model=HistoryResponse)
async def get_history():
    """获取对话历史记录"""
    try:
        history = assistant.get_chat_history()
        return HistoryResponse(history=history)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

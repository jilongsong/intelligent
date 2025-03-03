"""
主程序入口
提供 FastAPI 接口服务
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from chat_model import ChatModel
import uvicorn

app = FastAPI(title="本地智能对话系统")

# 初始化聊天模型
chat_model = ChatModel()

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    处理聊天请求
    
    Args:
        request: 包含用户消息的请求对象
        
    Returns:
        ChatResponse: 包含模型回复的响应对象
    """
    try:
        response = chat_model.chat_with_model(request.message)
        return ChatResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history")
async def get_history():
    """
    获取对话历史
    
    Returns:
        List: 对话历史记录
    """
    return chat_model.get_chat_history()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

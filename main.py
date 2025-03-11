"""
FastAPI 应用入口
提供 DSL 智能助手的 API 接口，支持多种模型后端
"""
import os
import sys
import logging
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.endpoints import router

# 配置日志
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format=settings.LOG_FORMAT,
    handlers=[
        logging.FileHandler(settings.LOG_FILE)
    ]
)

# 重定向标准输出和标准错误到日志文件
sys.stdout = open(settings.LOG_FILE, 'a')
sys.stderr = open(settings.LOG_FILE, 'a')

logger = logging.getLogger(__name__)

app = FastAPI(title=settings.PROJECT_NAME)

# 添加 CORS 支持
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(router)  # 移除prefix，直接使用根路径

if __name__ == "__main__":
    logger.info(f"启动{settings.PROJECT_NAME}服务...")
    uvicorn.run(
        app,
        host=os.getenv("HOST", "127.0.0.1"),  # 修改默认host为localhost
        port=int(os.getenv("PORT", 8000)),
        log_config=None  # 禁用uvicorn的默认日志配置
    )
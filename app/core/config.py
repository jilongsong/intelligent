"""
配置管理模块
"""
import os
from typing import Optional, List
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Settings(BaseSettings):
    """应用配置类"""
    # API设置
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "DSL 智能助手"
    
    # 模型设置
    MODEL_NAME: str = "qwq-32b"
    MODEL_API_BASE: str = "http://192.100.8.139:8080/v1"
    MODEL_API_KEY: Optional[str] = os.getenv("SF_API_KEY", "not-needed")
    
    # CORS设置
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    # 日志设置
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE: str = "app.log"  # 添加日志文件配置
    
    class Config:
        case_sensitive = True

# 创建全局设置实例
settings = Settings()
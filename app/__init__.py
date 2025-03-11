"""
DSL智能助手应用包
"""
from app.core.config import settings

__version__ = "0.1.0"
__author__ = "Intelligent Team"

# 设置包级别的日志配置
import logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format=settings.LOG_FORMAT
)
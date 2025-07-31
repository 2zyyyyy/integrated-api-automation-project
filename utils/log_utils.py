import logging
import os
from pathlib import Path
from pythonjsonlogger import jsonlogger
from datetime import datetime

# 日志目录
LOG_DIR = os.path.join(Path(__file__).parent.parent.resolve(), "reports", "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# 日志文件名（包含日期）
LOG_FILE = os.path.join(LOG_DIR, f"test_{datetime.now().strftime('%Y%m%d')}.log")

def setup_logger():
    """配置日志系统"""
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    
    # 避免重复添加处理器
    if logger.handlers:
        return logger
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    
    # 文件处理器（JSON格式）
    file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    json_formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s %(module)s %(funcName)s'
    )
    file_handler.setFormatter(json_formatter)
    
    # 添加处理器
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger

# 全局日志对象
logger = setup_logger()

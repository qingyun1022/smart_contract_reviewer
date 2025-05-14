import os
import logging
from logging.handlers import RotatingFileHandler

# 默认日志配置
DEFAULT_LOG_LEVEL = logging.INFO
DEFAULT_LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
DEFAULT_LOG_FILE = 'logs/system.log'
DEFAULT_MAX_BYTES = 10 * 1024 * 1024  # 10MB
DEFAULT_BACKUP_COUNT = 5

# 确保日志目录存在
os.makedirs(os.path.dirname(DEFAULT_LOG_FILE), exist_ok=True)

# 配置根日志记录器
root_logger = logging.getLogger()
root_logger.setLevel(DEFAULT_LOG_LEVEL)

# 添加控制台处理器
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter(DEFAULT_LOG_FORMAT))
root_logger.addHandler(console_handler)

# 添加文件处理器
file_handler = RotatingFileHandler(
    DEFAULT_LOG_FILE,
    maxBytes=DEFAULT_MAX_BYTES,
    backupCount=DEFAULT_BACKUP_COUNT,
    encoding='utf-8'
)
file_handler.setFormatter(logging.Formatter(DEFAULT_LOG_FORMAT))
root_logger.addHandler(file_handler)

def get_logger(name):
    """获取指定名称的日志记录器
    
    Args:
        name: 日志记录器名称
        
    Returns:
        日志记录器实例
    """
    return logging.getLogger(name)

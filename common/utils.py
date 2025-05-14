import os
import json
import uuid
import hashlib
from datetime import datetime
from typing import Dict, Any, List, Optional
from common.logger import get_logger

logger = get_logger(__name__)

def generate_uuid() -> str:
    """生成UUID
    
    Returns:
        UUID字符串
    """
    return str(uuid.uuid4())

def hash_text(text: str) -> str:
    """计算文本的哈希值
    
    Args:
        text: 输入文本
        
    Returns:
        哈希字符串
    """
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def load_json(file_path: str) -> Dict[str, Any]:
    """加载JSON文件
    
    Args:
        file_path: 文件路径
        
    Returns:
        JSON数据
    """
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            logger.warning(f"文件不存在: {file_path}")
            return {}
    except Exception as e:
        logger.error(f"加载JSON文件失败: {str(e)}")
        return {}

def save_json(data: Dict[str, Any], file_path: str) -> bool:
    """保存JSON文件
    
    Args:
        data: JSON数据
        file_path: 文件路径
        
    Returns:
        是否成功保存
    """
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return True
    except Exception as e:
        logger.error(f"保存JSON文件失败: {str(e)}")
        return False

def format_timestamp(timestamp: Optional[float] = None, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """格式化时间戳
    
    Args:
        timestamp: 时间戳，如果为None则使用当前时间
        format_str: 格式字符串
        
    Returns:
        格式化的时间字符串
    """
    if timestamp is None:
        dt = datetime.now()
    else:
        dt = datetime.fromtimestamp(timestamp)
    
    return dt.strftime(format_str)

def ensure_dir(directory: str) -> bool:
    """确保目录存在
    
    Args:
        directory: 目录路径
        
    Returns:
        是否成功创建
    """
    try:
        os.makedirs(directory, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"创建目录失败: {str(e)}")
        return False

def get_file_extension(filename: str) -> str:
    """获取文件扩展名
    
    Args:
        filename: 文件名
        
    Returns:
        文件扩展名（小写）
    """
    return os.path.splitext(filename)[1].lower()

def is_valid_file_type(filename: str, allowed_extensions: List[str]) -> bool:
    """检查文件类型是否有效
    
    Args:
        filename: 文件名
        allowed_extensions: 允许的扩展名列表
        
    Returns:
        是否为有效文件类型
    """
    ext = get_file_extension(filename)
    return ext in allowed_extensions

def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """截断文本
    
    Args:
        text: 输入文本
        max_length: 最大长度
        suffix: 后缀
        
    Returns:
        截断后的文本
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix

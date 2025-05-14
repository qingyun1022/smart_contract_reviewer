from typing import Dict, Any, Optional
from time import sleep
from common.logger import get_logger
from common.config import get_config

logger = get_logger(__name__)
config = get_config()

class RetryStrategy:
    """重试策略处理器，管理失败操作的重试逻辑"""
    
    def __init__(self):
        """初始化重试策略处理器"""
        self.retry_config = config.get("error_handling.retry", {})
        self.max_attempts = self.retry_config.get("max_attempts", 3)
        self.initial_delay = self.retry_config.get("initial_delay", 1)
        self.max_delay = self.retry_config.get("max_delay", 30)
        self.backoff_factor = self.retry_config.get("backoff_factor", 2)
    
    def should_retry(self, error: Exception, attempt: int) -> bool:
        """判断是否应该重试
        
        Args:
            error: 错误对象
            attempt: 当前尝试次数
            
        Returns:
            是否应该重试
        """
        # 检查是否超过最大重试次数
        if attempt >= self.max_attempts:
            logger.warning(f"已达到最大重试次数{self.max_attempts}，停止重试")
            return False
        
        # 获取错误类型配置
        error_type = type(error).__name__
        error_config = config.get(f"error_handling.error_types.{error_type}", {})
        
        # 检查错误类型是否允许重试
        if not error_config.get("retry", True):
            logger.info(f"错误类型{error_type}配置为不重试")
            return False
        
        # 检查是否超过错误类型的最大重试次数
        max_type_retries = error_config.get("max_retries", self.max_attempts)
        if attempt >= max_type_retries:
            logger.warning(f"错误类型{error_type}已达到最大重试次数{max_type_retries}")
            return False
        
        return True
    
    def get_retry_delay(self, attempt: int) -> float:
        """计算重试延迟时间
        
        Args:
            attempt: 当前尝试次数
            
        Returns:
            延迟秒数
        """
        # 使用指数退避算法计算延迟
        delay = self.initial_delay * (self.backoff_factor ** (attempt - 1))
        
        # 确保不超过最大延迟
        return min(delay, self.max_delay)
    
    def execute_with_retry(self, func, *args, **kwargs) -> Any:
        """使用重试策略执行函数
        
        Args:
            func: 要执行的函数
            *args: 位置参数
            **kwargs: 关键字参数
            
        Returns:
            函数执行结果
        """
        attempt = 0
        last_error = None
        
        while attempt < self.max_attempts:
            try:
                # 执行函数
                result = func(*args, **kwargs)
                
                # 如果成功，返回结果
                if attempt > 0:
                    logger.info(f"在第{attempt + 1}次尝试后成功执行")
                return result
            
            except Exception as e:
                attempt += 1
                last_error = e
                
                # 检查是否应该重试
                if not self.should_retry(e, attempt):
                    break
                
                # 计算延迟时间
                delay = self.get_retry_delay(attempt)
                logger.warning(f"执行失败，{delay}秒后进行第{attempt + 1}次重试: {str(e)}")
                
                # 等待后重试
                sleep(delay)
        
        # 所有重试都失败
        logger.error(f"在{attempt}次尝试后仍然失败: {str(last_error)}")
        raise last_error
    
    def get_retry_stats(self) -> Dict[str, Any]:
        """获取重试统计信息
        
        Returns:
            重试统计信息
        """
        return {
            "max_attempts": self.max_attempts,
            "initial_delay": self.initial_delay,
            "max_delay": self.max_delay,
            "backoff_factor": self.backoff_factor
        }
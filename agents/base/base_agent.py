from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from common.logger import get_logger
from common.config import get_config

logger = get_logger(__name__)
config = get_config()

class BaseAgent(ABC):
    """基础代理类，定义了所有代理的通用接口和功能"""
    
    def __init__(self, agent_id: str, agent_type: str):
        """初始化基础代理
        
        Args:
            agent_id: 代理唯一标识
            agent_type: 代理类型
        """
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.state = "idle"
        self.error_count = 0
        self.max_retries = config.get("agents.max_retries", 3)
        
    @abstractmethod
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理输入数据
        
        Args:
            input_data: 输入数据
            
        Returns:
            处理结果
        """
        pass
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """验证输入数据
        
        Args:
            input_data: 输入数据
            
        Returns:
            是否有效
        """
        return True
    
    def handle_error(self, error: Exception) -> Optional[Dict[str, Any]]:
        """处理错误
        
        Args:
            error: 错误对象
            
        Returns:
            错误处理结果
        """
        self.error_count += 1
        logger.error(f"代理{self.agent_id}处理失败: {str(error)}")
        
        # 检查是否需要重试
        if self.error_count < self.max_retries:
            logger.info(f"代理{self.agent_id}准备重试，当前重试次数：{self.error_count}")
            return {
                "retry": True,
                "error": str(error),
                "retry_count": self.error_count
            }
        
        # 超过最大重试次数
        logger.error(f"代理{self.agent_id}超过最大重试次数，转入死信队列")
        return {
            "retry": False,
            "error": str(error),
            "retry_count": self.error_count
        }
    
    def update_state(self, new_state: str):
        """更新代理状态
        
        Args:
            new_state: 新状态
        """
        self.state = new_state
        logger.info(f"代理{self.agent_id}状态更新为：{new_state}")
    
    def reset(self):
        """重置代理状态"""
        self.state = "idle"
        self.error_count = 0
        logger.info(f"代理{self.agent_id}已重置")
    
    def get_status(self) -> Dict[str, Any]:
        """获取代理状态
        
        Returns:
            状态信息
        """
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "state": self.state,
            "error_count": self.error_count
        }

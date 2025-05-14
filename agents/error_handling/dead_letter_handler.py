from typing import Dict, Any, Optional
from common.logger import get_logger
from common.config import get_config
from message_broker.core.queue_manager import QueueManager

logger = get_logger(__name__)
config = get_config()

class DeadLetterHandler:
    """死信处理器，处理无法正常处理的消息"""
    
    def __init__(self):
        """初始化死信处理器"""
        self.queue_manager = QueueManager()
        self.dead_letter_config = config.get("error_handling.dead_letter", {})
        self.setup_dead_letter_queue()
    
    def setup_dead_letter_queue(self):
        """设置死信队列"""
        try:
            # 创建死信交换机
            self.queue_manager.declare_exchange(
                self.dead_letter_config.get("exchange", "dead_letter_exchange"),
                "direct",
                durable=True
            )
            
            # 创建死信队列
            self.queue_manager.declare_queue(
                self.dead_letter_config.get("queue", "dead_letter_queue"),
                durable=True,
                arguments={
                    "x-message-ttl": self.dead_letter_config.get("ttl", 86400) * 1000,  # 转换为毫秒
                    "x-dead-letter-exchange": "",  # 空字符串表示默认交换机
                    "x-dead-letter-routing-key": "retry_queue"  # 重试队列
                }
            )
            
            # 绑定队列和交换机
            self.queue_manager.bind_queue(
                self.dead_letter_config.get("queue", "dead_letter_queue"),
                self.dead_letter_config.get("exchange", "dead_letter_exchange"),
                self.dead_letter_config.get("routing_key", "dead_letter")
            )
            
            logger.info("死信队列设置成功")
        except Exception as e:
            logger.error(f"设置死信队列失败: {str(e)}")
    
    def handle_dead_letter(self, message: Dict[str, Any]) -> bool:
        """处理死信消息
        
        Args:
            message: 死信消息
            
        Returns:
            是否成功处理
        """
        try:
            # 记录死信消息
            logger.error(f"接收到死信消息: {message}")
            
            # 发送到死信队列
            self.queue_manager.publish_message(
                self.dead_letter_config.get("exchange", "dead_letter_exchange"),
                self.dead_letter_config.get("routing_key", "dead_letter"),
                message
            )
            
            # 触发人工干预通知
            self._notify_human_intervention(message)
            
            return True
        except Exception as e:
            logger.error(f"处理死信消息失败: {str(e)}")
            return False
    
    def _notify_human_intervention(self, message: Dict[str, Any]):
        """通知人工干预
        
        Args:
            message: 死信消息
        """
        # 获取人工干预配置
        intervention_config = config.get("error_handling.human_intervention", {})
        
        if intervention_config.get("enabled", True):
            # 发送邮件通知
            if intervention_config.get("notification.email", True):
                self._send_email_notification(message)
            
            # 发送Slack通知
            if intervention_config.get("notification.slack", False):
                self._send_slack_notification(message)
    
    def _send_email_notification(self, message: Dict[str, Any]):
        """发送邮件通知
        
        Args:
            message: 死信消息
        """
        # TODO: 实现邮件通知
        logger.info(f"发送邮件通知: {message}")
    
    def _send_slack_notification(self, message: Dict[str, Any]):
        """发送Slack通知
        
        Args:
            message: 死信消息
        """
        # TODO: 实现Slack通知
        logger.info(f"发送Slack通知: {message}")
    
    def retry_message(self, message: Dict[str, Any]) -> bool:
        """重试死信消息
        
        Args:
            message: 死信消息
            
        Returns:
            是否成功重试
        """
        try:
            # 获取原始路由信息
            original_exchange = message.get("original_exchange", "")
            original_routing_key = message.get("original_routing_key", "")
            
            if not original_exchange or not original_routing_key:
                logger.error("缺少原始路由信息，无法重试消息")
                return False
            
            # 重新发送消息
            self.queue_manager.publish_message(
                original_exchange,
                original_routing_key,
                message.get("body", {})
            )
            
            logger.info(f"成功重试消息: {message}")
            return True
        except Exception as e:
            logger.error(f"重试消息失败: {str(e)}")
            return False
from typing import Dict, Any, Optional
from datetime import datetime
from common.logger import get_logger
from common.config import get_config
from common.utils import format_timestamp

logger = get_logger(__name__)
config = get_config()

class HumanInterventionHandler:
    """人工干预处理器，处理需要人工介入的情况"""
    
    def __init__(self):
        """初始化人工干预处理器"""
        self.intervention_config = config.get("error_handling.human_intervention", {})
        self.error_threshold = self.intervention_config.get("threshold.error_count", 3)
        self.error_rate_threshold = self.intervention_config.get("threshold.error_rate", 0.1)
        self.error_stats = {}
    
    def check_intervention_needed(self, agent_id: str, error: Exception) -> bool:
        """检查是否需要人工干预
        
        Args:
            agent_id: 代理ID
            error: 错误对象
            
        Returns:
            是否需要人工干预
        """
        # 更新错误统计
        if agent_id not in self.error_stats:
            self.error_stats[agent_id] = {
                "error_count": 0,
                "total_requests": 0,
                "last_error_time": None,
                "errors": []
            }
        
        stats = self.error_stats[agent_id]
        stats["error_count"] += 1
        stats["total_requests"] += 1
        stats["last_error_time"] = datetime.now()
        stats["errors"].append({
            "time": datetime.now(),
            "error": str(error)
        })
        
        # 检查错误次数
        if stats["error_count"] >= self.error_threshold:
            logger.warning(f"代理{agent_id}错误次数超过阈值{self.error_threshold}，需要人工干预")
            return True
        
        # 检查错误率
        error_rate = stats["error_count"] / stats["total_requests"]
        if error_rate >= self.error_rate_threshold:
            logger.warning(f"代理{agent_id}错误率{error_rate}超过阈值{self.error_rate_threshold}，需要人工干预")
            return True
        
        return False
    
    def handle_intervention(self, agent_id: str, error: Exception) -> Dict[str, Any]:
        """处理人工干预
        
        Args:
            agent_id: 代理ID
            error: 错误对象
            
        Returns:
            处理结果
        """
        try:
            # 生成干预记录
            intervention_record = self._create_intervention_record(agent_id, error)
            
            # 发送通知
            self._send_notifications(intervention_record)
            
            # 暂停代理
            self._pause_agent(agent_id)
            
            logger.info(f"已为代理{agent_id}创建人工干预记录")
            return intervention_record
        except Exception as e:
            logger.error(f"处理人工干预失败: {str(e)}")
            return {
                "error": True,
                "message": f"处理人工干预失败: {str(e)}"
            }
    
    def _create_intervention_record(self, agent_id: str, error: Exception) -> Dict[str, Any]:
        """创建干预记录
        
        Args:
            agent_id: 代理ID
            error: 错误对象
            
        Returns:
            干预记录
        """
        stats = self.error_stats.get(agent_id, {})
        return {
            "intervention_id": generate_uuid(),
            "agent_id": agent_id,
            "timestamp": format_timestamp(),
            "error_count": stats.get("error_count", 0),
            "error_rate": stats.get("error_count", 0) / stats.get("total_requests", 1),
            "last_error": str(error),
            "error_history": stats.get("errors", []),
            "status": "pending",
            "resolution": None,
            "resolved_by": None,
            "resolved_at": None
        }
    
    def _send_notifications(self, intervention_record: Dict[str, Any]):
        """发送干预通知
        
        Args:
            intervention_record: 干预记录
        """
        if self.intervention_config.get("notification.email", True):
            self._send_email_notification(intervention_record)
        
        if self.intervention_config.get("notification.slack", False):
            self._send_slack_notification(intervention_record)
    
    def _send_email_notification(self, intervention_record: Dict[str, Any]):
        """发送邮件通知
        
        Args:
            intervention_record: 干预记录
        """
        # TODO: 实现邮件通知
        logger.info(f"发送人工干预邮件通知: {intervention_record}")
    
    def _send_slack_notification(self, intervention_record: Dict[str, Any]):
        """发送Slack通知
        
        Args:
            intervention_record: 干预记录
        """
        # TODO: 实现Slack通知
        logger.info(f"发送人工干预Slack通知: {intervention_record}")
    
    def _pause_agent(self, agent_id: str):
        """暂停代理
        
        Args:
            agent_id: 代理ID
        """
        # TODO: 实现代理暂停逻辑
        logger.info(f"暂停代理{agent_id}")
    
    def resolve_intervention(self, intervention_id: str, resolution: Dict[str, Any]) -> bool:
        """解决干预
        
        Args:
            intervention_id: 干预ID
            resolution: 解决方案
            
        Returns:
            是否成功解决
        """
        try:
            # TODO: 实现干预解决逻辑
            logger.info(f"解决干预{intervention_id}: {resolution}")
            return True
        except Exception as e:
            logger.error(f"解决干预失败: {str(e)}")
            return False
    
    def get_intervention_status(self, intervention_id: str) -> Dict[str, Any]:
        """获取干预状态
        
        Args:
            intervention_id: 干预ID
            
        Returns:
            干预状态
        """
        # TODO: 实现获取干预状态逻辑
        return {
            "intervention_id": intervention_id,
            "status": "pending"
        }
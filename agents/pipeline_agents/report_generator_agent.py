from typing import Dict, Any
from agents.base.base_agent import BaseAgent
from common.logger import get_logger
from common.config import get_config
from report.generator import ReportGenerator

logger = get_logger(__name__)
config = get_config()

class ReportGeneratorAgent(BaseAgent):
    """报告生成代理，负责生成最终的审查报告"""
    
    def __init__(self, agent_id: str):
        """初始化报告生成代理
        
        Args:
            agent_id: 代理唯一标识
        """
        super().__init__(agent_id, "report_generator")
        self.generator = ReportGenerator()
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理报告生成任务
        
        Args:
            input_data: 输入数据，包含所有分析结果
            
        Returns:
            生成的报告
        """
        try:
            # 验证输入数据
            if not self.validate_input(input_data):
                raise ValueError("输入数据格式无效")
            
            # 更新状态
            self.update_state("processing")
            
            # 获取各项分析结果
            contract_analysis = input_data.get("contract_analysis", {})
            legal_assessment = input_data.get("legal_assessment", {})
            risk_analysis = input_data.get("risk_analysis", {})
            
            # 生成执行摘要
            executive_summary = self.generator.generate_executive_summary(
                contract_analysis,
                legal_assessment,
                risk_analysis
            )
            
            # 生成详细分析报告
            detailed_analysis = self.generator.generate_detailed_analysis(
                contract_analysis,
                legal_assessment,
                risk_analysis
            )
            
            # 生成建议和结论
            recommendations = self.generator.generate_recommendations(
                contract_analysis,
                legal_assessment,
                risk_analysis
            )
            
            # 生成完整报告
            report = {
                "executive_summary": executive_summary,
                "detailed_analysis": detailed_analysis,
                "recommendations": recommendations,
                "metadata": {
                    **input_data.get("metadata", {}),
                    "generated_at": self.generator.get_timestamp()
                }
            }
            
            # 更新状态
            self.update_state("completed")
            
            return report
        
        except Exception as e:
            # 处理错误
            error_result = self.handle_error(e)
            if error_result.get("retry", False):
                # 如果需要重试，递归调用
                return self.process(input_data)
            
            # 更新状态
            self.update_state("failed")
            
            # 返回错误信息
            return {
                "error": True,
                "message": str(e),
                "error_details": error_result
            }
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """验证输入数据
        
        Args:
            input_data: 输入数据
            
        Returns:
            是否有效
        """
        # 检查必要字段
        if not isinstance(input_data, dict):
            return False
        
        # 检查各项分析结果
        required_results = ["contract_analysis", "legal_assessment", "risk_analysis"]
        for result in required_results:
            if result not in input_data:
                return False
            if not isinstance(input_data[result], dict):
                return False
        
        return True
    
    def get_report_summary(self) -> Dict[str, Any]:
        """获取报告摘要
        
        Returns:
            报告摘要
        """
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "state": self.state,
            "generator_status": self.generator.get_status()
        }
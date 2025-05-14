from typing import Dict, Any
from agents.base.base_agent import BaseAgent
from common.logger import get_logger
from common.config import get_config
from risk.analyzer import RiskAnalyzer

logger = get_logger(__name__)
config = get_config()

class RiskAnalystAgent(BaseAgent):
    """风险分析代理，负责评估合同中的各类风险"""
    
    def __init__(self, agent_id: str):
        """初始化风险分析代理
        
        Args:
            agent_id: 代理唯一标识
        """
        super().__init__(agent_id, "risk_analyst")
        self.analyzer = RiskAnalyzer()
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理风险分析任务
        
        Args:
            input_data: 输入数据，包含合同分析结果
            
        Returns:
            风险分析结果
        """
        try:
            # 验证输入数据
            if not self.validate_input(input_data):
                raise ValueError("输入数据格式无效")
            
            # 更新状态
            self.update_state("processing")
            
            # 获取合同分析结果
            contract_analysis = input_data.get("contract_analysis", {})
            
            # 财务风险分析
            financial_risks = self.analyzer.analyze_financial_risks(contract_analysis)
            
            # 业务风险分析
            business_risks = self.analyzer.analyze_business_risks(contract_analysis)
            
            # 技术风险分析
            technical_risks = self.analyzer.analyze_technical_risks(contract_analysis)
            
            # 安全风险分析
            security_risks = self.analyzer.analyze_security_risks(contract_analysis)
            
            # 生成风险评分
            risk_scores = self.analyzer.calculate_risk_scores({
                "financial": financial_risks,
                "business": business_risks,
                "technical": technical_risks,
                "security": security_risks
            })
            
            # 生成风险缓解建议
            mitigation_suggestions = self.analyzer.generate_mitigation_suggestions({
                "financial": financial_risks,
                "business": business_risks,
                "technical": technical_risks,
                "security": security_risks
            })
            
            # 生成分析结果
            analysis_result = {
                "financial_risks": financial_risks,
                "business_risks": business_risks,
                "technical_risks": technical_risks,
                "security_risks": security_risks,
                "risk_scores": risk_scores,
                "mitigation_suggestions": mitigation_suggestions,
                "metadata": input_data.get("metadata", {})
            }
            
            # 更新状态
            self.update_state("completed")
            
            return analysis_result
        
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
        
        # 检查合同分析结果
        contract_analysis = input_data.get("contract_analysis", {})
        if not isinstance(contract_analysis, dict):
            return False
        
        # 检查必要的分析结果字段
        required_fields = ["contract_type", "structure", "key_clauses", "entities"]
        for field in required_fields:
            if field not in contract_analysis:
                return False
        
        return True
    
    def get_risk_summary(self) -> Dict[str, Any]:
        """获取风险摘要
        
        Returns:
            风险摘要
        """
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "state": self.state,
            "analyzer_status": self.analyzer.get_status()
        }
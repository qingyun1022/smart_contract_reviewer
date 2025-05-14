from typing import Dict, Any
from agents.base.base_agent import BaseAgent
from common.logger import get_logger
from common.config import get_config
from legal.advisor import LegalAdvisor

logger = get_logger(__name__)
config = get_config()

class LegalCounselAgent(BaseAgent):
    """法律顾问代理，负责提供法律建议和风险评估"""
    
    def __init__(self, agent_id: str):
        """初始化法律顾问代理
        
        Args:
            agent_id: 代理唯一标识
        """
        super().__init__(agent_id, "legal_counsel")
        self.advisor = LegalAdvisor()
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理法律咨询任务
        
        Args:
            input_data: 输入数据，包含合同分析结果
            
        Returns:
            法律建议和评估结果
        """
        try:
            # 验证输入数据
            if not self.validate_input(input_data):
                raise ValueError("输入数据格式无效")
            
            # 更新状态
            self.update_state("processing")
            
            # 获取合同分析结果
            contract_analysis = input_data.get("contract_analysis", {})
            
            # 法律合规性检查
            compliance_check = self.advisor.check_compliance(contract_analysis)
            
            # 权利义务分析
            rights_obligations = self.advisor.analyze_rights_obligations(contract_analysis)
            
            # 法律风险评估
            legal_risks = self.advisor.assess_legal_risks(contract_analysis)
            
            # 生成法律建议
            legal_advice = self.advisor.generate_legal_advice(
                contract_analysis,
                compliance_check,
                legal_risks
            )
            
            # 生成评估结果
            assessment_result = {
                "compliance_check": compliance_check,
                "rights_obligations": rights_obligations,
                "legal_risks": legal_risks,
                "legal_advice": legal_advice,
                "metadata": input_data.get("metadata", {})
            }
            
            # 更新状态
            self.update_state("completed")
            
            return assessment_result
        
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
    
    def get_assessment_summary(self) -> Dict[str, Any]:
        """获取评估摘要
        
        Returns:
            评估摘要
        """
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "state": self.state,
            "advisor_status": self.advisor.get_status()
        }
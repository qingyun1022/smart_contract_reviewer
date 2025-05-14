from typing import Dict, Any
from agents.base.base_agent import BaseAgent
from common.logger import get_logger
from common.config import get_config
from contract.analyzer import ContractAnalyzer

logger = get_logger(__name__)
config = get_config()

class ContractAnalystAgent(BaseAgent):
    """合同分析代理，负责分析合同内容和结构"""
    
    def __init__(self, agent_id: str):
        """初始化合同分析代理
        
        Args:
            agent_id: 代理唯一标识
        """
        super().__init__(agent_id, "contract_analyst")
        self.analyzer = ContractAnalyzer()
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理合同分析任务
        
        Args:
            input_data: 输入数据，包含合同文本和元数据
            
        Returns:
            分析结果
        """
        try:
            # 验证输入数据
            if not self.validate_input(input_data):
                raise ValueError("输入数据格式无效")
            
            # 更新状态
            self.update_state("processing")
            
            # 提取合同文本
            contract_text = input_data.get("contract_text", "")
            if not contract_text:
                raise ValueError("合同文本为空")
            
            # 分析合同结构
            structure_analysis = self.analyzer.analyze_structure(contract_text)
            
            # 提取关键条款
            key_clauses = self.analyzer.extract_key_clauses(contract_text)
            
            # 识别合同类型
            contract_type = self.analyzer.identify_contract_type(contract_text)
            
            # 提取实体信息
            entities = self.analyzer.extract_entities(contract_text)
            
            # 生成分析结果
            analysis_result = {
                "contract_type": contract_type,
                "structure": structure_analysis,
                "key_clauses": key_clauses,
                "entities": entities,
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
        
        # 检查合同文本
        if "contract_text" not in input_data:
            return False
        
        # 检查文本内容
        contract_text = input_data.get("contract_text", "")
        if not isinstance(contract_text, str) or not contract_text.strip():
            return False
        
        return True
    
    def get_analysis_summary(self) -> Dict[str, Any]:
        """获取分析摘要
        
        Returns:
            分析摘要
        """
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "state": self.state,
            "analyzer_status": self.analyzer.get_status()
        }
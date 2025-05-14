import re
import pandas as pd
from typing import List, Dict, Any
from common.logger import get_logger

logger = get_logger(__name__)

class ClauseParser:
    """合同条款解析器，负责从合同文本中提取和分类条款"""
    
    def __init__(self, knowledge_base_path: str = None):
        """初始化条款解析器
        
        Args:
            knowledge_base_path: 知识库路径，包含条款分类规则
        """
        self.clause_patterns = {
            "价格条款": r"价格|费用|报酬|金额|付款|￥|\$|人民币|美元",
            "交付条款": r"交付|交货|运输|物流|配送|到货",
            "违约责任": r"违约|赔偿|罚款|责任|索赔|争议",
            "保密条款": r"保密|机密|秘密|信息安全|数据保护",
            "合同期限": r"期限|有效期|终止|解除|到期|续约"
        }
        
        # 如果提供了知识库路径，从知识库加载更多规则
        if knowledge_base_path:
            try:
                self._load_patterns_from_knowledge_base(knowledge_base_path)
            except Exception as e:
                logger.error(f"加载知识库失败: {str(e)}")
    
    def _load_patterns_from_knowledge_base(self, kb_path: str):
        """从知识库加载条款模式
        
        Args:
            kb_path: 知识库文件路径
        """
        try:
            kb_data = pd.read_csv(kb_path)
            for _, row in kb_data.iterrows():
                if 'clause_type' in row and 'pattern' in row:
                    self.clause_patterns[row['clause_type']] = row['pattern']
        except Exception as e:
            logger.error(f"从知识库加载条款模式失败: {str(e)}")
            raise
    
    def extract_clauses(self, text: str) -> List[Dict[str, Any]]:
        """从文本中提取条款
        
        Args:
            text: 合同文本
            
        Returns:
            提取的条款列表，每个条款包含类型、内容和位置信息
        """
        clauses = []
        
        # 简单的条款分隔模式，假设条款以数字编号开头
        clause_split_pattern = r"第[一二三四五六七八九十\d]+条|[一二三四五六七八九十\d]+\.\s"
        potential_clauses = re.split(clause_split_pattern, text)
        
        # 移除空白条款
        potential_clauses = [c.strip() for c in potential_clauses if c.strip()]
        
        for i, clause_text in enumerate(potential_clauses):
            clause_type = self._classify_clause(clause_text)
            clauses.append({
                "id": i + 1,
                "type": clause_type,
                "content": clause_text,
                "position": {
                    "start": text.find(clause_text),
                    "end": text.find(clause_text) + len(clause_text)
                }
            })
        
        return clauses
    
    def _classify_clause(self, clause_text: str) -> str:
        """对条款进行分类
        
        Args:
            clause_text: 条款文本
            
        Returns:
            条款类型
        """
        for clause_type, pattern in self.clause_patterns.items():
            if re.search(pattern, clause_text, re.IGNORECASE):
                return clause_type
        
        return "其他条款"  # 默认分类
    
    def analyze_price_clauses(self, clauses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析价格条款
        
        Args:
            clauses: 提取的条款列表
            
        Returns:
            价格条款分析结果
        """
        price_clauses = [c for c in clauses if c["type"] == "价格条款"]
        
        if not price_clauses:
            return {"found": False, "message": "未找到价格条款"}
        
        # 提取金额
        amounts = []
        for clause in price_clauses:
            # 匹配金额模式
            amount_patterns = [
                r"(人民币|RMB|￥)\s*([\d,]+\.?\d*)\s*(元|万元|亿元)?",
                r"(\$|USD)\s*([\d,]+\.?\d*)\s*(dollars|美元)?"
            ]
            
            for pattern in amount_patterns:
                matches = re.findall(pattern, clause["content"])
                for match in matches:
                    currency = match[0]
                    value = match[1].replace(',', '')
                    unit = match[2] if len(match) > 2 else ""
                    
                    try:
                        amount = float(value)
                        # 处理单位转换
                        if unit == "万元":
                            amount *= 10000
                        elif unit == "亿元":
                            amount *= 100000000
                            
                        amounts.append({
                            "currency": currency,
                            "value": amount,
                            "original": f"{currency}{value}{unit}"
                        })
                    except ValueError:
                        logger.warning(f"无法解析金额: {match}")
        
        return {
            "found": True,
            "count": len(price_clauses),
            "amounts": amounts,
            "clauses": price_clauses
        }

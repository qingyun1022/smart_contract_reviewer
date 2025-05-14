from typing import Dict, Any, List, Optional
import importlib
import json
from common.logger import get_logger
from common.config import get_config

logger = get_logger(__name__)
config = get_config()

class ModelRouter:
    """模型路由器，负责将请求路由到适当的模型服务"""
    
    def __init__(self):
        """初始化模型路由器"""
        self.models = {}
        self.default_model = config.get("model_services", {}).get("default_model", "legal_small_model")
        self._load_models()
    
    def _load_models(self):
        """加载可用的模型服务"""
        try:
            # 加载内置模型
            from model_services.legal_small_model import LegalSmallModel
            self.models["legal_small_model"] = LegalSmallModel()
            
            # 尝试加载DeepSeek API模型（如果配置了）
            if config.get("model_services", {}).get("deepseek_api", {}).get("api_key"):
                from model_services.deepseek_api import DeepSeekAPI
                self.models["deepseek_api"] = DeepSeekAPI()
            
            logger.info(f"成功加载{len(self.models)}个模型服务")
        except Exception as e:
            logger.error(f"加载模型服务失败: {str(e)}")
    
    def get_available_models(self) -> List[str]:
        """获取可用的模型列表
        
        Returns:
            可用模型名称列表
        """
        return list(self.models.keys())
    
    def route_request(self, request: Dict[str, Any], model_name: str = None) -> Dict[str, Any]:
        """路由请求到指定模型
        
        Args:
            request: 请求数据
            model_name: 模型名称，如果为None则使用默认模型
            
        Returns:
            模型响应
        """
        # 如果没有指定模型，使用默认模型
        if not model_name:
            model_name = self.default_model
        
        # 检查模型是否可用
        if model_name not in self.models:
            logger.error(f"模型{model_name}不可用，使用默认模型{self.default_model}")
            model_name = self.default_model
        
        try:
            # 获取模型实例并处理请求
            model = self.models[model_name]
            response = model.process(request)
            
            logger.info(f"模型{model_name}成功处理请求")
            return response
        except Exception as e:
            logger.error(f"模型{model_name}处理请求失败: {str(e)}")
            return {
                "error": True,
                "message": f"模型处理失败: {str(e)}",
                "data": None
            }
    
    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """获取模型信息
        
        Args:
            model_name: 模型名称
            
        Returns:
            模型信息
        """
        if model_name not in self.models:
            return {"error": True, "message": f"模型{model_name}不存在"}
        
        try:
            model = self.models[model_name]
            return {
                "name": model_name,
                "description": getattr(model, "description", "无描述"),
                "capabilities": getattr(model, "capabilities", []),
                "parameters": getattr(model, "parameters", {})
            }
        except Exception as e:
            logger.error(f"获取模型{model_name}信息失败: {str(e)}")
            return {"error": True, "message": f"获取模型信息失败: {str(e)}"}

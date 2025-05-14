import os
import yaml
from typing import Dict, Any, Optional
from common.logger import get_logger

logger = get_logger(__name__)

class Config:
    """配置管理类，负责加载和管理应用配置"""
    
    _instance = None
    _config_data = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self):
        """加载配置文件"""
        config_path = os.getenv("CONFIG_PATH", "config/config.yaml")
        
        try:
            if os.path.exists(config_path):
                with open(config_path, "r", encoding="utf-8") as f:
                    self._config_data = yaml.safe_load(f)
                logger.info(f"成功从{config_path}加载配置")
            else:
                logger.warning(f"配置文件{config_path}不存在，使用默认配置")
                self._config_data = self._get_default_config()
        except Exception as e:
            logger.error(f"加载配置文件失败: {str(e)}，使用默认配置")
            self._config_data = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置
        
        Returns:
            默认配置字典
        """
        return {
            "app": {
                "name": "智能合同审查系统",
                "version": "1.0.0",
                "debug": True
            },
            "logging": {
                "level": "INFO",
                "file": "logs/system.log",
                "max_size": 10485760,  # 10MB
                "backup_count": 5
            },
            "rabbitmq": {
                "host": "localhost",
                "port": 5672,
                "username": "guest",
                "password": "guest",
                "virtual_host": "/"
            },
            "database": {
                "type": "mysql",
                "host": "localhost",
                "port": 3306,
                "username": "root",
                "password": "",
                "database": "contract_reviewer"
            },
            "chroma": {
                "persist_directory": "data/chroma_db"
            },
            "embedding": {
                "model_name": "all-MiniLM-L6-v2"
            },
            "file_storage": {
                "type": "local",
                "base_path": "data/files",
                "encrypt": True
            },
            "model_services": {
                "default_model": "legal_small_model",
                "timeout": 60
            },
            "budget": {
                "default_limit": 1000,
                "alert_threshold": 0.8
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值
        
        Args:
            key: 配置键，支持点号分隔的多级键
            default: 默认值
            
        Returns:
            配置值
        """
        if not self._config_data:
            return default
        
        # 处理多级键
        if "." in key:
            parts = key.split(".")
            current = self._config_data
            for part in parts:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    return default
            return current
        
        return self._config_data.get(key, default)
    
    def set(self, key: str, value: Any):
        """设置配置值
        
        Args:
            key: 配置键，支持点号分隔的多级键
            value: 配置值
        """
        if not self._config_data:
            self._config_data = {}
        
        # 处理多级键
        if "." in key:
            parts = key.split(".")
            current = self._config_data
            for i, part in enumerate(parts[:-1]):
                if part not in current:
                    current[part] = {}
                current = current[part]
            current[parts[-1]] = value
        else:
            self._config_data[key] = value
    
    def save(self, config_path: str = None):
        """保存配置到文件
        
        Args:
            config_path: 配置文件路径，如果为None则使用默认路径
        """
        if not config_path:
            config_path = os.getenv("CONFIG_PATH", "config/config.yaml")
        
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            
            with open(config_path, "w", encoding="utf-8") as f:
                yaml.dump(self._config_data, f, default_flow_style=False, allow_unicode=True)
            
            logger.info(f"成功保存配置到{config_path}")
        except Exception as e:
            logger.error(f"保存配置文件失败: {str(e)}")

def get_config() -> Dict[str, Any]:
    """获取配置实例
    
    Returns:
        配置字典
    """
    return Config()._config_data
import os
import pika
from typing import Callable, Dict, Any, Optional
from common.logger import get_logger
from common.config import get_config

logger = get_logger(__name__)
config = get_config()

class RabbitMQConnection:
    """RabbitMQ连接管理器，负责创建和管理与RabbitMQ的连接"""
    
    def __init__(self, host: str = None, port: int = None, 
                 username: str = None, password: str = None,
                 virtual_host: str = "/"):
        """初始化RabbitMQ连接
        
        Args:
            host: RabbitMQ主机地址
            port: RabbitMQ端口
            username: 用户名
            password: 密码
            virtual_host: 虚拟主机
        """
        # 优先使用传入的参数，否则从配置或环境变量获取
        self.host = host or config.get("rabbitmq", {}).get("host") or os.getenv("RABBITMQ_HOST", "localhost")
        self.port = port or config.get("rabbitmq", {}).get("port") or int(os.getenv("RABBITMQ_PORT", "5672"))
        self.username = username or config.get("rabbitmq", {}).get("username") or os.getenv("RABBITMQ_USERNAME", "guest")
        self.password = password or config.get("rabbitmq", {}).get("password") or os.getenv("RABBITMQ_PASSWORD", "guest")
        self.virtual_host = virtual_host or config.get("rabbitmq", {}).get("virtual_host") or os.getenv("RABBITMQ_VHOST", "/")
        
        self.connection = None
        self.channel = None
    
    def connect(self) -> bool:
        """建立与RabbitMQ的连接
        
        Returns:
            是否成功连接
        """
        try:
            # 创建连接参数
            credentials = pika.PlainCredentials(self.username, self.password)
            parameters = pika.ConnectionParameters(
                host=self.host,
                port=self.port,
                virtual_host=self.virtual_host,
                credentials=credentials
            )
            
            # 建立连接
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            logger.info(f"成功连接到RabbitMQ: {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"连接RabbitMQ失败: {str(e)}")
            return False
    
    def close(self):
        """关闭连接"""
        if self.connection and self.connection.is_open:
            self.connection.close()
            logger.info("RabbitMQ连接已关闭")
    
    def declare_queue(self, queue_name: str, durable: bool = True, 
                     arguments: Dict[str, Any] = None) -> bool:
        """声明队列
        
        Args:
            queue_name: 队列名称
            durable: 是否持久化
            arguments: 队列参数
            
        Returns:
            是否成功声明
        """
        try:
            if not self.channel:
                if not self.connect():
                    return False
            
            self.channel.queue_declare(
                queue=queue_name,
                durable=durable,
                arguments=arguments
            )
            
            logger.info(f"成功声明队列: {queue_name}")
            return True
        except Exception as e:
            logger.error(f"声明队列失败: {str(e)}")
            return False
    
    def declare_exchange(self, exchange_name: str, exchange_type: str = "direct",
                        durable: bool = True) -> bool:
        """声明交换机
        
        Args:
            exchange_name: 交换机名称
            exchange_type: 交换机类型
            durable: 是否持久化
            
        Returns:
            是否成功声明
        """
        try:
            if not self.channel:
                if not self.connect():
                    return False
            
            self.channel.exchange_declare(
                exchange=exchange_name,
                exchange_type=exchange_type,
                durable=durable
            )
            
            logger.info(f"成功声明交换机: {exchange_name}, 类型: {exchange_type}")
            return True
        except Exception as e:
            logger.error(f"声明交换机失败: {str(e)}")
            return False
    
    def bind_queue(self, queue_name: str, exchange_name: str, routing_key: str) -> bool:
        """绑定队列到交换机
        
        Args:
            queue_name: 队列名称
            exchange_name: 交换机名称
            routing_key: 路由键
            
        Returns:
            是否成功绑定
        """
        try:
            if not self.channel:
                if not self.connect():
                    return False
            
            self.channel.queue_bind(
                queue=queue_name,
                exchange=exchange_name,
                routing_key=routing_key
            )
            
            logger.info(f"成功绑定队列{queue_name}到交换机{exchange_name}，路由键: {routing_key}")
            return True
        except Exception as e:
            logger.error(f"绑定队列失败: {str(e)}")
            return False
    
    def publish_message(self, exchange_name: str, routing_key: str, 
                       message: str, properties: pika.BasicProperties = None) -> bool:
        """发布消息
        
        Args:
            exchange_name: 交换机名称
            routing_key: 路由键
            message: 消息内容
            properties: 消息属性
            
        Returns:
            是否成功发布
        """
        try:
            if not self.channel:
                if not self.connect():
                    return False
            
            # 如果没有指定属性，创建默认属性
            if properties is None:
                properties = pika.BasicProperties(
                    delivery_mode=2,  # 持久化消息
                    content_type='application/json'
                )
            
            self.channel.basic_publish(
                exchange=exchange_name,
                routing_key=routing_key,
                body=message,
                properties=properties
            )
            
            logger.debug(f"成功发布消息到{exchange_name}，路由键: {routing_key}")
            return True
        except Exception as e:
            logger.error(f"发布消息失败: {str(e)}")
            return False
    
    def consume(self, queue_name: str, callback: Callable, auto_ack: bool = False):
        """消费消息
        
        Args:
            queue_name: 队列名称
            callback: 回调函数
            auto_ack: 是否自动确认
        """
        try:
            if not self.channel:
                if not self.connect():
                    return
            
            self.channel.basic_consume(
                queue=queue_name,
                on_message_callback=callback,
                auto_ack=auto_ack
            )
            
            logger.info(f"开始消费队列: {queue_name}")
            self.channel.start_consuming()
        except Exception as e:
            logger.error(f"消费消息失败: {str(e)}")
    
    def acknowledge(self, delivery_tag: int):
        """确认消息
        
        Args:
            delivery_tag: 投递标签
        """
        try:
            if self.channel:
                self.channel.basic_ack(delivery_tag=delivery_tag)
        except Exception as e:
            logger.error(f"确认消息失败: {str(e)}")
    
    def reject(self, delivery_tag: int, requeue: bool = False):
        """拒绝消息
        
        Args:
            delivery_tag: 投递标签
            requeue: 是否重新入队
        """
        try:
            if self.channel:
                self.channel.basic_reject(delivery_tag=delivery_tag, requeue=requeue)
        except Exception as e:
            logger.error(f"拒绝消息失败: {str(e)}")

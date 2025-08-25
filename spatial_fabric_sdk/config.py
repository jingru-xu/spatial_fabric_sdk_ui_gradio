"""
配置模块

定义空间数据管理客户端的配置类
"""

from typing import Optional
from dataclasses import dataclass


@dataclass
class ClientConfig:
    """
    客户端配置类
    
    包含连接Handle和Gard服务所需的配置参数
    """
    
    # Gard服务的基础URL
    gard_base_url: str = "https://your-gard-service.com"
    
    # Handle前缀
    handle_prefix: str = "86.1009.24"
    
    # 连接超时时间（秒）
    timeout: int = 30
    
    # 连接池大小
    connection_pool_size: int = 10
    
    # 是否启用SSL验证
    verify_ssl: bool = False
    
    # 自定义证书路径
    cert_path: Optional[str] = None
    
    # 自定义密钥路径
    key_path: Optional[str] = None
    
    def __post_init__(self):
        """配置验证"""
        if not self.gard_base_url:
            raise ValueError("gard_base_url 不能为空")
        
        if not self.handle_prefix:
            raise ValueError("handle_prefix 不能为空")
        
        if self.timeout <= 0:
            raise ValueError("timeout 必须大于0")
        
        if self.connection_pool_size <= 0:
            raise ValueError("connection_pool_size 必须大于0")

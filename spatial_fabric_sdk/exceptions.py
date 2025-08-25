"""
Spatial Fabric SDK 异常定义
"""

class SpatialFabricError(Exception):
    """Spatial Fabric SDK 基础异常类"""
    pass


class HandleError(SpatialFabricError):
    """Handle 相关操作异常"""
    pass


class GardError(SpatialFabricError):
    """Gard 相关操作异常"""
    pass


class ConfigurationError(SpatialFabricError):
    """配置错误异常"""
    pass


class ValidationError(SpatialFabricError):
    """数据验证错误异常"""
    pass


class ConnectionError(SpatialFabricError):
    """连接错误异常"""
    pass 
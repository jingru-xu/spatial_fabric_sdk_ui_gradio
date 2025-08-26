"""
Spatial Fabric SDK - 空间数据管理统一接口

这个SDK封装了Handle SDK和PyGard SDK，提供统一的空间数据管理接口。
"""

from .client import SpatialFabricClient
from .models import SpatialData, SpatialMetadata, SearchFilter, SearchResult
from .exceptions import SpatialFabricError, HandleError, GardError, ConfigurationError
from .config import ClientConfig
def gradio_ui() -> None:
    """Lazy import UI to avoid heavy side effects at package import time."""
    from .gradio_ui import gradio_ui as _gradio_ui
    _gradio_ui()

__version__ = "1.0.0"
__author__ = "Spatial Fabric Team"

__all__ = [
    "SpatialFabricClient",
    "SpatialData", 
    "SpatialMetadata",
    "SearchFilter",
    "SearchResult",
    "SpatialFabricError",
    "HandleError",
    "GardError",
    "ConfigurationError",
    "ClientConfig",
    "gradio_ui"
] 
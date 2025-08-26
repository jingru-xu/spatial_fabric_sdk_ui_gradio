"""
Spatial Fabric SDK 数据模型
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
@dataclass
class StorageLocation:
    """描述一个可访问的存储位置（不含敏感凭据）。"""
    type: str                 # e.g., "s3", "bds", "calcite", "https", "fs"
    url: str                  # 规范化的定位符，如 s3://bucket/key, https://..., calcite://...
    access_method: Optional[str] = None  # e.g., presign, public, query
    region: Optional[str] = None
    content_type: Optional[str] = None
    size: Optional[int] = None
    checksum: Optional[Dict[str, Any]] = None  # {"algo": "sha256", "value": "..."}
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StorageDescriptor:
    """用于在元数据中记录与数据访问相关的非敏感信息。"""
    storage: List[StorageLocation] = field(default_factory=list)
    preferred: Optional[str] = None  # type of preferred location
    version: Optional[str] = None
    created_at: Optional[datetime] = None
    deprecated: bool = False



@dataclass
class SpatialMetadata:
    """空间数据元数据"""
    name: str
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    type: str = "GEOMETRY"
    is_spatial: bool = True
    is_temporal: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    custom_fields: Dict[str, Any] = field(default_factory=dict)
    storage_descriptor: Optional[StorageDescriptor] = None  # 将非敏感存储描述写入元数据


@dataclass
class SpatialData:
    """空间数据记录"""
    metadata: SpatialMetadata
    id: Optional[str] = None
    handle_id: Optional[str] = None
    spatial_info: Optional[Dict[str, Any]] = None
    temporal_info: Optional[Dict[str, Any]] = None
    data_url: Optional[str] = None
    file_path: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()


@dataclass
class SearchFilter:
    """搜索过滤器"""
    tags: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    spatial_bounds: Optional[Dict[str, float]] = None
    temporal_range: Optional[Dict[str, datetime]] = None
    data_type: Optional[str] = None
    custom_filters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SearchResult:
    """搜索结果"""
    records: List[SpatialData]
    total_count: int
    page: int
    page_size: int
    has_next: bool
    has_previous: bool 
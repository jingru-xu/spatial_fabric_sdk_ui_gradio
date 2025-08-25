"""
Spatial Fabric SDK 基本测试
"""

import pytest
import asyncio
from spatial_fabric_sdk import (
    SpatialFabricClient, 
    SpatialData, 
    SpatialMetadata, 
    SearchFilter,
    SpatialFabricError,
    HandleError,
    GardError
)


class TestSpatialFabricClient:
    """测试SpatialFabricClient类"""
    
    def test_init(self):
        """测试客户端初始化"""
        client = SpatialFabricClient(
            gard_base_url="https://test-gard-service.com",
            handle_prefix="86.1009.24"
        )
        
        assert client.gard_base_url == "https://test-gard-service.com"
        assert client.handle_prefix == "86.1009.24"
        assert not client._initialized
    
    def test_init_without_handle_prefix(self):
        """测试不带Handle前缀的初始化"""
        client = SpatialFabricClient("https://test-gard-service.com")
        
        assert client.gard_base_url == "https://test-gard-service.com"
        assert client.handle_prefix is None
        assert not client._initialized


class TestSpatialMetadata:
    """测试SpatialMetadata类"""
    
    def test_create_metadata(self):
        """测试创建元数据"""
        metadata = SpatialMetadata(
            name="测试数据",
            description="这是一个测试",
            tags=["test", "demo"],
            type="GEOMETRY",
            is_spatial=True,
            is_temporal=False
        )
        
        assert metadata.name == "测试数据"
        assert metadata.description == "这是一个测试"
        assert metadata.tags == ["test", "demo"]
        assert metadata.type == "GEOMETRY"
        assert metadata.is_spatial is True
        assert metadata.is_temporal is False
    
    def test_metadata_defaults(self):
        """测试元数据默认值"""
        metadata = SpatialMetadata(name="测试数据")
        
        assert metadata.description is None
        assert metadata.tags == []
        assert metadata.type == "GEOMETRY"
        assert metadata.is_spatial is True
        assert metadata.is_temporal is False
        assert metadata.custom_fields == {}


class TestSpatialData:
    """测试SpatialData类"""
    
    def test_create_spatial_data(self):
        """测试创建空间数据"""
        metadata = SpatialMetadata(name="测试数据")
        spatial_data = SpatialData(
            metadata=metadata,
            spatial_info={"bounds": {"min_lat": 0, "max_lat": 1}},
            data_url="https://example.com/data.geojson"
        )
        
        assert spatial_data.metadata == metadata
        assert spatial_data.spatial_info == {"bounds": {"min_lat": 0, "max_lat": 1}}
        assert spatial_data.data_url == "https://example.com/data.geojson"
        assert spatial_data.id is None
        assert spatial_data.handle_id is None
    
    def test_spatial_data_timestamps(self):
        """测试空间数据时间戳"""
        metadata = SpatialMetadata(name="测试数据")
        spatial_data = SpatialData(metadata=metadata)
        
        assert spatial_data.created_at is not None
        assert spatial_data.updated_at is not None
        assert spatial_data.created_at == spatial_data.updated_at


class TestSearchFilter:
    """测试SearchFilter类"""
    
    def test_create_search_filter(self):
        """测试创建搜索过滤器"""
        search_filter = SearchFilter(
            tags=["geology", "stratigraphy"],
            keywords=["地层", "岩石"],
            data_type="GEOMETRY"
        )
        
        assert search_filter.tags == ["geology", "stratigraphy"]
        assert search_filter.keywords == ["地层", "岩石"]
        assert search_filter.data_type == "GEOMETRY"
        assert search_filter.spatial_bounds is None
        assert search_filter.temporal_range is None
        assert search_filter.custom_filters == {}
    
    def test_search_filter_defaults(self):
        """测试搜索过滤器默认值"""
        search_filter = SearchFilter()
        
        assert search_filter.tags is None
        assert search_filter.keywords is None
        assert search_filter.data_type is None
        assert search_filter.spatial_bounds is None
        assert search_filter.temporal_range is None
        assert search_filter.custom_filters == {}


class TestSearchResult:
    """测试SearchResult类"""
    
    def test_create_search_result(self):
        """测试创建搜索结果"""
        metadata = SpatialMetadata(name="测试数据")
        spatial_data = SpatialData(metadata=metadata)
        
        search_result = SearchResult(
            records=[spatial_data],
            total_count=1,
            page=1,
            page_size=10,
            has_next=False,
            has_previous=False
        )
        
        assert len(search_result.records) == 1
        assert search_result.total_count == 1
        assert search_result.page == 1
        assert search_result.page_size == 10
        assert search_result.has_next is False
        assert search_result.has_previous is False


class TestExceptions:
    """测试异常类"""
    
    def test_exception_inheritance(self):
        """测试异常继承关系"""
        assert issubclass(HandleError, SpatialFabricError)
        assert issubclass(GardError, SpatialFabricError)
        assert issubclass(SpatialFabricError, Exception)


# 异步测试
@pytest.mark.asyncio
async def test_client_initialization():
    """测试客户端异步初始化"""
    client = SpatialFabricClient("https://test-gard-service.com")
    
    # 注意：这里只是测试初始化逻辑，不涉及实际的网络连接
    # 在实际测试中，可能需要mock网络请求
    
    # 测试初始化状态检查
    with pytest.raises(Exception):  # 这里应该抛出ConfigurationError
        client._ensure_initialized()


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__]) 
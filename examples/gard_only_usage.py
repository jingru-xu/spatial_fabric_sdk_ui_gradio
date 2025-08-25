"""
Spatial Fabric SDK - 仅使用Gard功能示例

这个示例展示如何只使用Gard相关的功能，不涉及Handle管理
"""

import asyncio
from spatial_fabric_sdk import SpatialFabricClient, SpatialData, SpatialMetadata, SearchFilter


async def gard_only_example():
    """仅使用Gard功能的示例"""
    
    print("=== Gard 功能示例 ===\n")
    
    # 初始化客户端
    client = SpatialFabricClient(
        gard_base_url="https://your-gard-service.com",
        handle_prefix="86.1009.24"
    )
    
    # 异步初始化
    await client.initialize()
    print("✅ Gard客户端初始化成功！")
    
    # 1. 创建空间数据
    print("\n1. 创建空间数据")
    metadata = SpatialMetadata(
        name="华北地层数据",
        description="关于华北地区古生代地层的详细记录",
        tags=["geology", "paleozoic", "stratigraphy"],
        type="GEOMETRY",
        is_spatial=True,
        is_temporal=True
    )
    
    spatial_data = SpatialData(
        metadata=metadata,
        spatial_info={
            "bounds": {"min_lat": 35.0, "max_lat": 45.0, "min_lon": 110.0, "max_lon": 120.0},
            "crs": "EPSG:4326"
        },
        temporal_info={
            "start_time": "2020-01-01T00:00:00Z",
            "end_time": "2020-12-31T23:59:59Z"
        }
    )
    
    try:
        created_data = await client.create_spatial_data(spatial_data)
        print(f"✅ 空间数据创建成功！ID: {created_data.id}")
        print(f"   名称: {created_data.metadata.name}")
        print(f"   描述: {created_data.metadata.description}")
        print(f"   标签: {created_data.metadata.tags}")
    except Exception as e:
        print(f"❌ 创建失败: {e}")
        return
    
    # 2. 获取空间数据
    print("\n2. 获取空间数据")
    try:
        retrieved_data = await client.get_spatial_data(created_data.id)
        if retrieved_data:
            print(f"✅ 获取成功！")
            print(f"   名称: {retrieved_data.metadata.name}")
            print(f"   描述: {retrieved_data.metadata.description}")
        else:
            print("❌ 未找到数据")
    except Exception as e:
        print(f"❌ 获取失败: {e}")
    
    # 3. 按标签搜索
    print("\n3. 按标签搜索")
    try:
        results = await client.search_by_tags(["geology"])
        print(f"✅ 按标签 'geology' 搜索到 {len(results)} 条结果")
        
        if results:
            print(f"   第一条结果名称: {results[0].metadata.name}")
    except Exception as e:
        print(f"❌ 标签搜索失败: {e}")
    
    # 4. 使用过滤器搜索
    print("\n4. 使用过滤器搜索")
    try:
        search_filter = SearchFilter(
            tags=["stratigraphy"],
            keywords=["地层"],
            data_type="GEOMETRY"
        )
        
        search_results = await client.search_spatial_data(search_filter, page=1, page_size=5)
        print(f"✅ 复杂搜索找到 {len(search_results.records)} 条结果")
        print(f"   总页数: {search_results.total_count}")
        print(f"   当前页: {search_results.page}")
        print(f"   每页大小: {search_results.page_size}")
        print(f"   是否有下一页: {search_results.has_next}")
        
    except Exception as e:
        print(f"❌ 过滤器搜索失败: {e}")
    
    # 5. 更新空间数据
    print("\n5. 更新空间数据")
    try:
        # 更新描述和标签
        retrieved_data.metadata.description = "这是更新后的华北地层数据描述，包含更多详细信息。"
        retrieved_data.metadata.tags.append("updated")
        
        updated_data = await client.update_spatial_data(created_data.id, retrieved_data)
        print(f"✅ 数据更新成功！")
        print(f"   新描述: {updated_data.metadata.description}")
        print(f"   新标签: {updated_data.metadata.tags}")
        
    except Exception as e:
        print(f"❌ 更新失败: {e}")
    
    # 6. 验证更新
    print("\n6. 验证更新")
    try:
        verify_data = await client.get_spatial_data(created_data.id)
        if verify_data:
            print(f"✅ 验证成功！")
            print(f"   描述: {verify_data.metadata.description}")
            print(f"   标签: {verify_data.metadata.tags}")
        else:
            print("❌ 验证失败：未找到数据")
    except Exception as e:
        print(f"❌ 验证失败: {e}")
    
    # 7. 删除空间数据
    print("\n7. 删除空间数据")
    try:
        success = await client.delete_spatial_data(created_data.id)
        if success:
            print(f"✅ 数据删除成功！")
        else:
            print("❌ 数据删除失败")
    except Exception as e:
        print(f"❌ 删除失败: {e}")
    
    # 8. 验证删除
    print("\n8. 验证删除")
    try:
        deleted_data = await client.get_spatial_data(created_data.id)
        if deleted_data is None:
            print("✅ 验证成功：数据确实已被删除")
        else:
            print("❌ 验证失败：数据仍然存在")
    except Exception as e:
        print(f"✅ 验证成功：数据已删除（抛出异常: {e}）")
    
    print("\n=== Gard 功能示例完成 ===")


if __name__ == "__main__":
    asyncio.run(gard_only_example()) 
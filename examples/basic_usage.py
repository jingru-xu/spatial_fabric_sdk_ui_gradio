"""
Spatial Fabric SDK 基本使用示例
"""

import asyncio
from spatial_fabric_sdk import SpatialFabricClient, SpatialData, SpatialMetadata, SearchFilter


async def main():
    """主函数示例"""
    
    # 1. 初始化客户端
    print("正在初始化 Spatial Fabric 客户端...")
    client = SpatialFabricClient(
        gard_base_url="https://your-gard-service.com",
        handle_prefix="86.1009.24"
    )
    
    # 异步初始化
    await client.initialize()
    print("客户端初始化成功！")
    
    # 2. 创建空间数据元数据
    print("\n创建空间数据元数据...")
    metadata = SpatialMetadata(
        name="华北地层数据",
        description="关于华北地区古生代地层的详细记录",
        tags=["geology", "paleozoic", "stratigraphy", "north-china"],
        type="GEOMETRY",
        is_spatial=True,
        is_temporal=True
    )
    
    # 3. 创建空间数据对象
    spatial_data = SpatialData(
        metadata=metadata,
        spatial_info={
            "bounds": {"min_lat": 35.0, "max_lat": 45.0, "min_lon": 110.0, "max_lon": 120.0},
            "crs": "EPSG:4326"
        },
        temporal_info={
            "start_time": "2020-01-01T00:00:00Z",
            "end_time": "2020-12-31T23:59:59Z"
        },
        data_url="https://example.com/data/north-china-strata.geojson"
    )
    
    # 4. 注册Handle并创建空间数据
    print("注册Handle并创建空间数据...")
    handle_id = "86.1009.24/strata.north-china"
    target_url = "https://example.com/data/north-china-strata.geojson"
    
    try:
        created_data = await client.register_and_create(
            handle_id=handle_id,
            target_url=target_url,
            spatial_data=spatial_data
        )
        print(f"成功创建空间数据！ID: {created_data.id}")
        print(f"Handle ID: {created_data.handle_id}")
    except Exception as e:
        print(f"创建失败: {e}")
        return
    
    # 5. 根据ID获取空间数据
    print("\n根据ID获取空间数据...")
    try:
        retrieved_data = await client.get_spatial_data(created_data.id)
        if retrieved_data:
            print(f"获取成功！名称: {retrieved_data.metadata.name}")
            print(f"描述: {retrieved_data.metadata.description}")
            print(f"标签: {retrieved_data.metadata.tags}")
        else:
            print("未找到数据")
    except Exception as e:
        print(f"获取失败: {e}")
    
    # 6. 搜索空间数据
    print("\n搜索空间数据...")
    try:
        # 按标签搜索
        geology_results = await client.search_by_tags(["geology"])
        print(f"按标签 'geology' 搜索到 {len(geology_results)} 条结果")
        
        if geology_results:
            print(f"第一条结果名称: {geology_results[0].metadata.name}")
        
        # 使用过滤器搜索
        search_filter = SearchFilter(
            tags=["stratigraphy"],
            keywords=["地层"],
            data_type="GEOMETRY"
        )
        
        search_results = await client.search_spatial_data(search_filter, page=1, page_size=5)
        print(f"复杂搜索找到 {len(search_results.records)} 条结果")
        
    except Exception as e:
        print(f"搜索失败: {e}")
    
    # 7. 更新空间数据
    print("\n更新空间数据...")
    try:
        # 更新描述
        retrieved_data.metadata.description = "这是更新后的华北地层数据描述，包含更多详细信息。"
        retrieved_data.metadata.tags.append("updated")
        
        updated_data = await client.update_spatial_data(created_data.id, retrieved_data)
        print(f"数据更新成功！新描述: {updated_data.metadata.description}")
        print(f"新标签: {updated_data.metadata.tags}")
        
    except Exception as e:
        print(f"更新失败: {e}")
    
    # 8. 解析Handle
    print("\n解析Handle...")
    try:
        handle_info = await client.parse_spatial_handle(handle_id)
        print(f"Handle解析结果: {handle_info}")
    except Exception as e:
        print(f"解析Handle失败: {e}")
    
    # 9. 搜索Handle
    print("\n搜索Handle...")
    try:
        handle_results = await client.search_handles(
            fields=["name"],
            values=["地层"],
            operators=["like"]
        )
        print(f"Handle搜索找到 {len(handle_results)} 条结果")
    except Exception as e:
        print(f"搜索Handle失败: {e}")
    
    # 10. 删除空间数据（可选）
    print("\n是否删除测试数据？(y/n): ", end="")
    # 在实际使用中，这里可以添加用户输入逻辑
    # 为了演示，我们跳过删除步骤
    print("跳过删除步骤")
    
    print("\n示例执行完成！")


if __name__ == "__main__":
    # 运行异步主函数
    asyncio.run(main()) 
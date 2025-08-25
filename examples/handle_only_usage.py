"""
Spatial Fabric SDK - 仅使用Handle功能示例

这个示例展示如何只使用Handle相关的功能，不涉及Gard数据管理
"""

import asyncio
from spatial_fabric_sdk import SpatialFabricClient, SpatialMetadata


async def handle_only_example():
    """仅使用Handle功能的示例"""
    
    print("=== Handle 功能示例 ===\n")
    
    # 初始化客户端（不需要Gard服务）
    client = SpatialFabricClient(
        gard_base_url="https://dummy-gard-service.com",  # 虚拟URL
        handle_prefix="86.1009.24"
    )
    
    # 1. 注册Handle
    print("1. 注册Handle")
    handle_id = "86.1009.24/book.demo2"
    target_url = "https://example.com"
    
    metadata = SpatialMetadata(
        name="《测试书2》",
        description="这是一本测试用的书籍",
        tags=["book", "test", "demo"],
        type="DOCUMENT",
        is_spatial=False,
        is_temporal=False
    )
    
    try:
        result = await client.register_spatial_handle(handle_id, target_url, metadata)
        print(f"✅ Handle注册成功: {result}")
    except Exception as e:
        print(f"❌ Handle注册失败: {e}")
    
    # 2. 解析Handle
    print("\n2. 解析Handle")
    try:
        result = await client.parse_spatial_handle(handle_id)
        print(f"✅ Handle解析成功: {result}")
    except Exception as e:
        print(f"❌ Handle解析失败: {e}")
    
    # 3. 搜索Handle
    print("\n3. 搜索Handle")
    try:
        results = await client.search_handles(
            fields=["name"],
            values=["测试"],
            operators=["like"]
        )
        print(f"✅ Handle搜索成功，找到 {len(results)} 条结果")
        for i, result in enumerate(results):
            print(f"   结果 {i+1}: {result}")
    except Exception as e:
        print(f"❌ Handle搜索失败: {e}")
    
    print("\n=== Handle 功能示例完成 ===")


if __name__ == "__main__":
    asyncio.run(handle_only_example()) 
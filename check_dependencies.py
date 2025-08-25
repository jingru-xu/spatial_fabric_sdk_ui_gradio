#!/usr/bin/env python3
"""
Spatial Fabric SDK 依赖检查工具
"""

def check_dependencies():
    """检查所有依赖是否正确安装"""
    print("🔍 检查 Spatial Fabric SDK 依赖...")
    print("=" * 50)
    
    # 检查 handle_sdk
    try:
        from handle_sdk import register_handle, parse_handle
        print("✅ handle_sdk - 已安装")
        print(f"   - register_handle: {'可用' if callable(register_handle) else '不可用'}")
        print(f"   - parse_handle: {'可用' if callable(parse_handle) else '不可用'}")
        
        # 检查是否有 search_handles 函数
        try:
            from handle_sdk import search_handles
            print(f"   - search_handles: {'可用' if callable(search_handles) else '不可用'}")
        except ImportError:
            print("   - search_handles: 不可用 (函数不存在)")
            
    except ImportError:
        print("❌ handle_sdk - 未安装")
        print("   请安装: pip install handle_sdk-2.0.0-py3-none-any.whl")
    
    print()
    
    # 检查 pygard
    try:
        from pygard import GardClient, Gard, GardFilter
        print("✅ pygard - 已安装")
        print(f"   - GardClient: {'可用' if callable(GardClient) else '不可用'}")
        print(f"   - Gard: {'可用' if callable(Gard) else '不可用'}")
        print(f"   - GardFilter: {'可用' if callable(GardFilter) else '不可用'}")
    except ImportError:
        print("❌ pygard - 未安装")
        print("   请安装: pip install pygard-0.1.2-py3-none-any.whl")
    
    print()
    
    # 检查 spatial_fabric_sdk
    try:
        from spatial_fabric_sdk import SpatialFabricClient, SpatialData, SpatialMetadata
        print("✅ spatial_fabric_sdk - 已安装")
        print(f"   - SpatialFabricClient: {'可用' if callable(SpatialFabricClient) else '不可用'}")
        print(f"   - SpatialData: {'可用' if callable(SpatialData) else '不可用'}")
        print(f"   - SpatialMetadata: {'可用' if callable(SpatialMetadata) else '不可用'}")
    except ImportError:
        print("❌ spatial_fabric_sdk - 未安装")
        print("   请安装: pip install spatial_fabric_sdk-1.0.0-py3-none-any.whl")
    
    print()
    print("=" * 50)
    
    # 总结
    print("📋 安装建议:")
    print("1. 先安装底层SDK:")
    print("   pip install handle_sdk-2.0.0-py3-none-any.whl")
    print("   pip install pygard-0.1.2-py3-none-any.whl")
    print("2. 再安装封装SDK:")
    print("   pip install spatial_fabric_sdk-1.0.0-py3-none-any.whl")
    print("3. 或者一次性安装:")
    print("   pip install handle_sdk-2.0.0-py3-none-any.whl pygard-0.1.2-py3-none-any.whl spatial_fabric_sdk-1.0.0-py3-none-any.whl")

if __name__ == "__main__":
    check_dependencies() 
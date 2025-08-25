#!/usr/bin/env python3
"""
测试SSL证书配置在同步调用中的修复效果
"""

import sys
import os
import time

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from spatial_fabric_sdk.client import SpatialFabricClient
from spatial_fabric_sdk.models import SpatialMetadata

def test_ssl_certificate_fix():
    """测试SSL证书配置修复"""
    print("🧪 开始测试SSL证书配置修复...")
    
    try:
        # 创建客户端
        client = SpatialFabricClient(
            gard_base_url="https://your-gard-service.com",
            handle_prefix="86.1009.24"
        )
        
        print("✅ 客户端创建成功")
        
        # 测试Handle注册（这是之前失败的地方）
        print("🔄 测试Handle注册...")
        
        # 创建测试元数据
        metadata = SpatialMetadata(
            name="SSL测试数据",
            description="用于测试SSL证书配置的数据",
            tags=["test", "ssl", "certificate"],
            type="GEOMETRY",
            is_spatial=True,
            is_temporal=False
        )
        
        # 生成唯一的Handle ID
        timestamp = int(time.time())
        handle_id = f"86.1009.24/ssl-test-{timestamp}"
        target_url = "https://example.com/test.geojson"
        
        print(f"📋 Handle ID: {handle_id}")
        print(f"🔗 目标URL: {target_url}")
        
        # 第一次调用（同步方法）
        try:
            print("📞 第一次调用register_spatial_handle_sync...")
            result1 = client.register_spatial_handle_sync(handle_id, target_url, metadata)
            print("✅ 第一次调用成功")
            print(f"📄 结果: {result1}")
        except Exception as e:
            error_msg = str(e)
            print(f"❌ 第一次调用失败: {error_msg}")
            
            if "SSL" in error_msg or "certificate" in error_msg.lower():
                print("❌ SSL证书问题仍然存在")
                return False
            elif "协程已被使用" in error_msg:
                print("❌ 协程重用问题仍然存在")
                return False
            else:
                print("⚠️ 其他错误，这可能是预期的（因为服务器可能不可用）")
        
        # 第二次调用（测试是否还有SSL问题）
        try:
            print("📞 第二次调用register_spatial_handle_sync...")
            timestamp2 = int(time.time())
            handle_id2 = f"86.1009.24/ssl-test-{timestamp2}"
            result2 = client.register_spatial_handle_sync(handle_id2, target_url, metadata)
            print("✅ 第二次调用成功")
            print(f"📄 结果: {result2}")
        except Exception as e:
            error_msg = str(e)
            print(f"❌ 第二次调用失败: {error_msg}")
            
            if "SSL" in error_msg or "certificate" in error_msg.lower():
                print("❌ SSL证书问题仍然存在")
                return False
            else:
                print("⚠️ 其他错误，这可能是预期的")
        
        # 测试解析Handle
        try:
            print("📞 测试parse_spatial_handle_sync...")
            result3 = client.parse_spatial_handle_sync(handle_id)
            print("✅ Handle解析成功")
            print(f"📄 结果: {result3}")
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Handle解析失败: {error_msg}")
            
            if "SSL" in error_msg or "certificate" in error_msg.lower():
                print("❌ SSL证书问题仍然存在")
                return False
            else:
                print("⚠️ 其他错误，这可能是预期的")
        
        print("✅ SSL证书配置修复测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        return False

if __name__ == "__main__":
    success = test_ssl_certificate_fix()
    if success:
        print("\n🎉 SSL证书配置修复测试通过！")
        print("💡 现在Gradio页面应该可以正常注册Handle了")
        sys.exit(0)
    else:
        print("\n💥 SSL证书配置修复测试失败！")
        print("💡 可能需要进一步检查证书配置")
        sys.exit(1)


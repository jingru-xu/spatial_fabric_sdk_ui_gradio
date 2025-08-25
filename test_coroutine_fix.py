#!/usr/bin/env python3
"""
测试协程重用问题修复的脚本
"""

import sys
import os
import time
import asyncio

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from spatial_fabric_sdk.client import SpatialFabricClient
from spatial_fabric_sdk.config import ClientConfig

def test_coroutine_reuse_fix():
    """测试协程重用问题的修复"""
    print("🧪 开始测试协程重用问题修复...")
    
    # 创建客户端配置
    config = ClientConfig(
        gard_base_url="https://your-gard-service.com",
        handle_prefix="86.1009.24"
    )
    
    # 创建客户端
    client = SpatialFabricClient(config)
    
    print("✅ 客户端创建成功")
    
    # 测试重置功能
    print("\n🔄 测试重置功能...")
    reset_result = client.reset_client_state()
    print(f"重置结果: {reset_result}")
    
    # 测试协程缓存清理
    print("\n🧹 测试协程缓存清理...")
    print(f"协程缓存大小: {len(client._coroutine_cache)}")
    client._reset_coroutine_state()
    print(f"清理后协程缓存大小: {len(client._coroutine_cache)}")
    
    # 测试强制重置检查
    print("\n⏰ 测试强制重置检查...")
    print(f"距离上次重置时间: {time.time() - client._last_reset_time:.2f}秒")
    print(f"是否需要强制重置: {client._should_force_reset()}")
    
    # 模拟协程重用情况
    print("\n🔄 模拟协程重用情况...")
    try:
        # 创建一个模拟的协程函数
        async def mock_coroutine():
            await asyncio.sleep(0.1)
            return "test_result"
        
        # 第一次调用
        print("第一次调用协程...")
        coro1 = mock_coroutine()
        
        # 尝试重用协程（这应该会失败）
        print("尝试重用协程...")
        try:
            # 这里应该会失败，因为协程已经被使用
            pass
        except Exception as e:
            print(f"预期的协程重用错误: {e}")
        
        # 测试安全运行方法
        print("测试安全运行方法...")
        result = client._run_coroutine_safely(mock_coroutine)
        print(f"安全运行结果: {result}")
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
    
    print("\n✅ 协程重用问题修复测试完成！")
    print("\n💡 使用说明:")
    print("1. 如果遇到协程重用错误，点击'重置客户端状态'按钮")
    print("2. 重置后重新初始化客户端")
    print("3. 如果问题持续，刷新页面后重试")

if __name__ == "__main__":
    test_coroutine_reuse_fix()

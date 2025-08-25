#!/usr/bin/env python3
"""
Spatial Fabric SDK Gradio UI 启动脚本
专门用于Gradio启动，支持公网链接
"""

import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from spatial_fabric_sdk.gradio_ui import gradio_ui

def main():
    """主函数"""
    print("🚀 正在启动 Spatial Fabric SDK Gradio界面...")
    print("🌐 界面将自动生成公网链接，方便远程访问")
    print("💡 提示：要停止界面，请按 Ctrl+C")
    
    gradio_ui()

if __name__ == "__main__":
    main()

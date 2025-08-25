#!/usr/bin/env python3
"""
Spatial Fabric SDK Gradio UI 启动脚本
支持公网链接访问
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from spatial_fabric_sdk import gradio_ui
    print("🚀 正在启动 Spatial Fabric SDK Gradio界面...")
    print("🌐 界面将自动生成公网链接，方便远程访问")
    print("💡 提示：要停止界面，请按 Ctrl+C")
    
    gradio_ui()
    
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("🔧 请确保已正确安装Spatial Fabric SDK")
    print("💡 运行: pip install -e .")
    
except Exception as e:
    print(f"❌ 启动失败: {e}")
    print("🔧 请检查依赖是否正确安装")
    print("💡 运行: pip install gradio pandas")

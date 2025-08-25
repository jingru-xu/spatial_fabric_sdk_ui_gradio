from setuptools import setup, find_packages

setup(
    name="spatial-fabric-sdk",
    version="1.0.0",
    description="统一的空间数据管理SDK，封装了Handle SDK和PyGard SDK",
    long_description="""
    Spatial Fabric SDK 是一个统一的空间数据管理接口。
    
    ⚠️ 重要提示：使用此SDK前，必须先安装以下依赖包：
    1. handle_sdk-2.0.0-py3-none-any.whl
    2. pygard-0.1.2-py3-none-any.whl
    
    安装顺序：
    pip install handle_sdk-2.0.0-py3-none-any.whl
    pip install pygard-0.1.2-py3-none-any.whl
    pip install spatial_fabric_sdk-1.0.0-py3-none-any.whl
    
    🆕 新功能：现在支持交互式界面！
    使用 sf.gradio_ui() 即可启动图形界面，轻松管理空间数据。
    """,
    packages=find_packages(),
    install_requires=[
        # 注意：这些依赖需要用户手动安装对应的wheel包
        # 因为它们是本地wheel包，不是PyPI上的包
        "aiohttp>=3.7.0",  # 降低版本要求，兼容Python 3.7
        "pydantic>=1.8.0",  # Python 3.7兼容版本
        "dataclasses-json>=0.5.0",  # Python 3.7兼容版本
        "typing-extensions>=3.7.0",  # Python 3.7兼容版本
        "gradio>=3.50.0",  # UI界面，兼容性更好的版本
        "pandas>=1.5.0",  # 数据处理
    ],
    python_requires=">=3.7",  # 改为支持Python 3.7
    author="Spatial Fabric Team",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",  # 添加Python 3.7支持
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ]
) 
# Spatial Fabric SDK 用户使用手册

## 🆕 新功能：交互式界面！

现在您可以通过图形界面轻松使用SDK的所有功能，无需编写代码！

### 🚀 快速启动界面

```python
import spatial_fabric_sdk as sf

# 启动交互式界面
sf.gradio_ui()
```

或者直接运行启动脚本：
```bash
python run_gradio_ui.py
```

### 🎯 界面功能特性

- **🌍 现代化Web界面**: 基于Gradio，美观易用
- **📱 响应式设计**: 支持桌面端和移动端
- **⚡ 直观操作**: 通过表单和按钮完成所有操作
- **📊 实时反馈**: 操作结果立即显示，支持数据表格
- **🔍 完整功能**: 涵盖所有SDK功能
- **🌐 公网访问**: 支持公网链接，方便远程访问

### 📋 界面主要页面

1. **🏠 概览**: 系统状态、快速操作入口
2. **🔗 Handle管理**: 注册、解析、搜索Handle标识符
3. **📊 空间数据管理**: 创建、读取、更新、删除空间数据
4. **🔍 搜索功能**: 标签搜索、高级搜索
5. **📋 数据查看**: 数据列表、详细信息

---

## 🚀 快速安装

### ⚠️ 重要提示：必须先安装底层SDK

```bash
# 1. 安装Handle SDK
pip install handle_sdk-2.0.0-py3-none-any.whl

# 2. 安装PyGard SDK  
pip install pygard-0.1.2-py3-none-any.whl

# 3. 安装Spatial Fabric SDK（包含UI功能）
pip install -e .

# 4. 安装UI依赖
pip install gradio pandas
```

### 或者一次性安装
```bash
pip install handle_sdk-2.0.0-py3-none-any.whl pygard-0.1.2-py3-none-any.whl
pip install -e .
pip install gradio pandas
```

### 为什么需要这些包？
- **`handle_sdk`** - 提供Handle标识符管理功能
- **`pygard`** - 提供空间数据管理功能  
- **`spatial_fabric_sdk`** - 统一封装层，调用上述两个SDK
- **`gradio`** - 提供Web界面框架
- **`pandas`** - 提供数据处理和表格展示

### 🔍 检查依赖是否正确安装
```bash
# 运行依赖检查工具
python check_dependencies.py
```

这个工具会检查所有依赖是否正确安装，并给出详细的安装建议。

## 📚 基本使用

### 🖥️ 使用交互式界面（推荐新手）

```python
import spatial_fabric_sdk as sf

# 启动界面
sf.gradio_ui()
```

界面启动后：
1. **配置服务**: 在配置区域输入Gard服务和Handle系统配置
2. **初始化客户端**: 点击"初始化客户端"按钮
3. **开始使用**: 通过标签页选择功能，填写表单执行操作

### 💻 使用编程接口（适合开发者）

```python
from spatial_fabric_sdk import SpatialFabricClient, SpatialData, SpatialMetadata
```

### 2. 初始化客户端
```python
# 创建客户端
client = SpatialFabricClient(
    gard_base_url="https://your-gard-service.com",  # Gard服务地址
    handle_prefix="86.1009.24"                      # Handle前缀
)

# 初始化
await client.initialize()
```

---

## 🔗 Handle 操作

### 注册Handle
```python
# 创建元数据
metadata = SpatialMetadata(
    name="华北地层数据",
    description="关于华北地区古生代地层的详细记录",
    tags=["geology", "paleozoic", "stratigraphy"]
)

# 注册Handle
result = await client.register_spatial_handle(
    handle_id="86.1009.24/strata.north-china",
    target_url="https://example.com/data.geojson",
    metadata=metadata
)
```

### 解析Handle
```python
# 解析Handle
handle_info = await client.parse_spatial_handle("86.1009.24/strata.north-china")
print(f"Handle信息: {handle_info}")
```

---

## 📊 空间数据操作

### 创建空间数据
```python
# 创建元数据
metadata = SpatialMetadata(
    name="华北地层数据",
    description="关于华北地区古生代地层的详细记录",
    tags=["geology", "paleozoic", "stratigraphy"]
)

# 创建空间数据
spatial_data = SpatialData(
    metadata=metadata,
    spatial_info={
        "bounds": {"min_lat": 35.0, "max_lat": 45.0, "min_lon": 110.0, "max_lon": 120.0},
        "crs": "EPSG:4326"
    }
)

# 保存到系统
created_data = await client.create_spatial_data(spatial_data)
print(f"数据创建成功！ID: {created_data.id}")
```

### 获取空间数据
```python
# 根据ID获取数据
data = await client.get_spatial_data("data_001")
if data:
    print(f"数据名称: {data.metadata.name}")
    print(f"数据描述: {data.metadata.description}")
```

### 更新空间数据
```python
# 更新数据
existing_data = await client.get_spatial_data("data_001")
if existing_data:
    existing_data.metadata.description = "这是更新后的描述"
    updated_data = await client.update_spatial_data("data_001", existing_data)
    print("数据更新成功！")
```

### 删除空间数据
```python
# 删除数据
success = await client.delete_spatial_data("data_001")
if success:
    print("数据删除成功！")
```

---

## 🔍 搜索功能

### 按标签搜索
```python
# 搜索地质相关数据
results = await client.search_by_tags(["geology", "stratigraphy"])
print(f"找到 {len(results)} 条数据")

for data in results:
    print(f"- {data.metadata.name}: {data.metadata.description}")
```

### 复杂搜索
```python
from spatial_fabric_sdk import SearchFilter

# 创建搜索过滤器
search_filter = SearchFilter(
    tags=["geology"],
    keywords=["地层"],
    spatial_bounds={"min_lat": 35.0, "max_lat": 45.0}
)

# 执行搜索
search_results = await client.search_spatial_data(search_filter, page=1, page_size=10)
print(f"找到 {len(search_results.records)} 条数据")
```

---

## ⚡ 便捷方法

### 一次性注册Handle并创建数据
```python
# 一次性完成Handle注册和数据创建
created_data = await client.register_and_create(
    handle_id="86.1009.24/strata.north-china",
    target_url="https://example.com/data.geojson",
    spatial_data=spatial_data
)

print(f"Handle和数据创建成功！")
print(f"数据ID: {created_data.id}")
print(f"Handle ID: {created_data.handle_id}")
```

---

## 📋 数据模型说明

### SpatialMetadata（元数据）
```python
metadata = SpatialMetadata(
    name="数据名称",           # 必填
    description="数据描述",     # 可选
    tags=["标签1", "标签2"],   # 可选
    type="GEOMETRY",          # 可选，默认"GEOMETRY"
    is_spatial=True,          # 可选，默认True
    is_temporal=False         # 可选，默认False
)
```

### SpatialData（空间数据）
```python
spatial_data = SpatialData(
    metadata=metadata,        # 必填：元数据
    spatial_info={...},       # 可选：空间信息
    temporal_info={...},      # 可选：时间信息
    data_url="数据URL"        # 可选：数据文件地址
)
```

---

## ⚠️ 注意事项

1. **异步操作**：所有方法都是异步的，需要使用 `await`
2. **初始化**：使用前必须先调用 `await client.initialize()`
3. **错误处理**：建议使用 try-catch 包装所有操作
4. **依赖要求**：需要先安装 `handle-sdk` 和 `pygard`

---

## 🎯 完整示例

```python
import asyncio
from spatial_fabric_sdk import SpatialFabricClient, SpatialData, SpatialMetadata

async def main():
    # 初始化客户端
    client = SpatialFabricClient(
        gard_base_url="https://your-gard-service.com",
        handle_prefix="86.1009.24"
    )
    await client.initialize()
    
    # 创建空间数据
    metadata = SpatialMetadata(
        name="华北地层数据",
        description="关于华北地区古生代地层的详细记录",
        tags=["geology", "paleozoic", "stratigraphy"]
    )
    
    spatial_data = SpatialData(metadata=metadata)
    
    # 注册Handle并创建数据
    created_data = await client.register_and_create(
        handle_id="86.1009.24/strata.north-china",
        target_url="https://example.com/data.geojson",
        spatial_data=spatial_data
    )
    
    print(f"创建成功！ID: {created_data.id}")

# 运行
asyncio.run(main())
```

---

## 📞 获取帮助

- **示例代码**：查看 `examples/` 目录
- **演示脚本**：运行 `python demo.py`
- **API参考**：查看 `API_QUICK_REFERENCE.md`
- **项目文档**：查看 `README.md` 
# Spatial Fabric SDK

一个统一的空间数据管理SDK，封装了Handle SDK和PyGard SDK，提供简洁易用的空间数据管理接口。

## 🆕 新功能：交互式界面！

现在您可以通过图形界面轻松使用SDK的所有功能！

### 🌐 Gradio界面
支持公网链接，方便远程访问：

```python
import spatial_fabric_sdk as sf

# 启动Gradio界面
sf.gradio_ui()
```

或者直接运行启动脚本：
```bash
python run_gradio_ui.py
```

## 功能特性

### 🎯 统一接口
- 通过一个SDK管理Handle和空间数据
- 一致的数据模型和API设计
- 支持同步和异步操作

### 🔗 Handle管理
- **注册Handle**: 为空间数据创建唯一标识符
- **解析Handle**: 根据Handle ID获取数据信息
- **搜索Handle**: 按条件搜索已注册的Handle

### 📊 空间数据管理
- **创建数据**: 创建新的空间数据记录
- **获取数据**: 根据ID获取空间数据
- **更新数据**: 更新现有空间数据
- **删除数据**: 删除空间数据记录
- **搜索数据**: 支持标签、关键词、空间范围等搜索条件

### 🌍 空间特性
- 支持空间坐标系统
- 支持时间范围查询
- 灵活的元数据管理
- 可扩展的标签系统

### 🖥️ 交互式界面
- **Gradio界面**: 基于Gradio的现代化Web界面，支持公网链接
- **直观操作**: 通过表单和按钮轻松完成各种操作
- **实时反馈**: 操作结果实时显示，支持数据表格展示
- **响应式设计**: 支持不同屏幕尺寸，移动端友好
- **公网访问**: 自动生成公网链接，方便远程访问

## 安装

### 前置要求
确保已安装以下SDK：
- `handle_sdk-2.0.0-py3-none-any.whl`
- `pygard-0.1.2-py3-none-any.whl`

### 安装依赖
```bash
# 安装底层SDK
pip install handle_sdk-2.0.0-py3-none-any.whl pygard-0.1.2-py3-none-any.whl

# 安装Spatial Fabric SDK（包含UI功能）
pip install -e .
```

### 安装UI依赖
```bash
# Gradio界面依赖
pip install gradio pandas
```

## 快速开始

### 🖥️ 使用交互式界面

#### 🌐 Gradio界面
```python
import spatial_fabric_sdk as sf

# 启动Gradio界面（支持公网链接）
sf.gradio_ui()
```

或者直接运行：
```bash
python run_gradio_ui.py
```

界面启动后：
1. 在配置区域输入Gard服务和Handle系统信息
2. 点击"初始化客户端"
3. 开始使用各项功能！
4. 界面会自动生成公网链接，方便远程访问

### 💻 使用编程接口

```python
import asyncio
from spatial_fabric_sdk import SpatialFabricClient, SpatialData, SpatialMetadata

async def main():
    # 初始化客户端
    client = SpatialFabricClient(
        gard_base_url="https://your-gard-service.com",
        handle_prefix="86.1009.24"
    )
    
    # 异步初始化
    await client.initialize()
    
    # 创建空间数据
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
        }
    )
    
    # 注册Handle并创建数据
    created_data = await client.register_and_create(
        handle_id="86.1009.24/strata.north-china",
        target_url="https://example.com/data/north-china-strata.geojson",
        spatial_data=spatial_data
    )
    
    print(f"创建成功！ID: {created_data.id}")

# 运行
asyncio.run(main())
```

## 🖥️ 界面功能详解

### Gradio界面特性
- **公网链接**: 自动生成公网链接，支持远程访问
- **现代化设计**: 使用Gradio的现代化UI组件
- **响应式布局**: 自适应不同屏幕尺寸
- **实时交互**: 所有操作都有实时反馈

### 主要功能页面

1. **⚙️ 系统配置**: 配置Gard服务和Handle系统
2. **🔗 Handle管理**: 注册、解析、搜索Handle
3. **📊 空间数据管理**: 创建、读取、更新、删除空间数据
4. **🔍 搜索功能**: 标签搜索和高级搜索
5. **📋 数据查看**: 数据列表和详细信息

### 操作流程

1. **配置服务**: 在配置区域输入服务地址和配置
2. **初始化客户端**: 点击初始化按钮
3. **选择功能**: 通过标签页选择要使用的功能
4. **填写表单**: 在相应页面填写必要信息
5. **执行操作**: 点击按钮执行操作
6. **查看结果**: 在界面上查看操作结果
7. **公网访问**: 界面会自动显示公网链接，方便远程访问

## API 参考

### 核心类

#### `SpatialFabricClient`
主要的客户端类，提供所有功能接口。

**初始化参数:**
- `gard_base_url`: Gard服务的基础URL
- `handle_prefix`: Handle系统的前缀（可选）
- `handle_config`: Handle系统的配置（可选）

**主要方法:**
- `initialize()`: 异步初始化客户端
- `register_spatial_handle()`: 注册空间数据Handle
- `parse_spatial_handle()`: 解析Handle
- `search_handles()`: 搜索Handle
- `create_spatial_data()`: 创建空间数据
- `get_spatial_data()`: 获取空间数据
- `update_spatial_data()`: 更新空间数据
- `delete_spatial_data()`: 删除空间数据
- `search_spatial_data()`: 搜索空间数据
- `search_by_tags()`: 按标签搜索

#### `SpatialData`
空间数据记录类。

**属性:**
- `id`: 数据ID
- `handle_id`: Handle ID
- `metadata`: 元数据对象
- `spatial_info`: 空间信息
- `temporal_info`: 时间信息
- `data_url`: 数据URL
- `file_path`: 文件路径
- `created_at`: 创建时间
- `updated_at`: 更新时间

#### `SpatialMetadata`
空间数据元数据类。

**属性:**
- `name`: 数据名称
- `description`: 数据描述
- `tags`: 标签列表
- `type`: 数据类型
- `is_spatial`: 是否包含空间信息
- `is_temporal`: 是否包含时间信息
- `created_at`: 创建时间
- `updated_at`: 更新时间
- `custom_fields`: 自定义字段

#### `SearchFilter`
搜索过滤器类。

**属性:**
- `tags`: 标签列表
- `keywords`: 关键词列表
- `spatial_bounds`: 空间边界
- `temporal_range`: 时间范围
- `data_type`: 数据类型
- `custom_filters`: 自定义过滤器

### 异常类

- `SpatialFabricError`: 基础异常类
- `HandleError`: Handle相关操作异常
- `GardError`: Gard相关操作异常
- `ConfigurationError`: 配置错误异常
- `ValidationError`: 数据验证错误异常
- `ConnectionError`: 连接错误异常

## 配置

SDK支持通过配置文件进行配置：

```yaml
# config/config.yaml
gard:
  base_url: "https://your-gard-service.com"
  timeout: 30
  retry_count: 3

handle:
  prefix: "86.1009.24"
  server_url: "https://your-handle-server.com"
  authentication:
    enabled: false
    username: ""
    password: ""
```

## 示例

查看 `examples/` 目录中的完整示例：

- `basic_usage.py`: 基本使用示例
- `handle_only_usage.py`: 仅使用Handle功能
- `gard_only_usage.py`: 仅使用Gard功能

## 错误处理

SDK使用异常机制进行错误处理：

```python
try:
    result = await client.create_spatial_data(spatial_data)
except GardError as e:
    print(f"Gard操作失败: {e}")
except HandleError as e:
    print(f"Handle操作失败: {e}")
except SpatialFabricError as e:
    print(f"SDK操作失败: {e}")
```

## 异步支持

SDK完全支持异步操作，使用Python的`async/await`语法：

```python
async def process_data():
    client = SpatialFabricClient("https://your-service.com")
    await client.initialize()
    
    # 异步操作
    data = await client.get_spatial_data("data-id")
    return data

# 运行异步函数
result = asyncio.run(process_data())
```

## 贡献

欢迎提交Issue和Pull Request来改进SDK！

## 许可证

本项目采用MIT许可证。

## 联系方式

如有问题或建议，请通过以下方式联系：

- 提交GitHub Issue
- 发送邮件至项目维护者

---

**注意**: 使用前请确保已正确配置Handle系统和Gard服务。

**🎉 新功能**: 现在您可以通过 `sf.gradio_ui()` 启动Gradio界面，支持公网链接，轻松管理空间数据！ 
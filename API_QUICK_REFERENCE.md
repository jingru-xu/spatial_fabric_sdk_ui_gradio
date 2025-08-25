# Spatial Fabric SDK API 速查表

## 🚀 快速开始

```python
from spatial_fabric_sdk import SpatialFabricClient, SpatialData, SpatialMetadata

# 初始化客户端
client = SpatialFabricClient(
    gard_base_url="https://your-gard-service.com",
    handle_prefix="86.1009.24"
)
await client.initialize()
```

---

## 🔗 Handle 操作

| 方法 | 调用方式 | 说明 |
|------|----------|------|
| **注册Handle** | `await client.register_spatial_handle(handle_id, target_url, metadata)` | 为空间数据创建唯一标识符 |
| **解析Handle** | `await client.parse_spatial_handle(handle_id)` | 根据Handle ID获取数据信息 |
| **搜索Handle** | `await client.search_handles(fields, values, operators)` | 按条件搜索已注册的Handle |

**示例：**
```python
# 注册Handle
result = await client.register_spatial_handle(
    handle_id="86.1009.24/strata.north-china",
    target_url="https://example.com/data.geojson",
    metadata=metadata
)
```

---

## 📊 空间数据操作

| 方法 | 调用方式 | 说明 |
|------|----------|------|
| **创建数据** | `await client.create_spatial_data(spatial_data)` | 创建新的空间数据记录 |
| **获取数据** | `await client.get_spatial_data(data_id)` | 根据ID获取空间数据 |
| **更新数据** | `await client.update_spatial_data(data_id, spatial_data)` | 更新现有空间数据 |
| **删除数据** | `await client.delete_spatial_data(data_id)` | 删除空间数据记录 |

**示例：**
```python
# 创建空间数据
metadata = SpatialMetadata(
    name="华北地层数据",
    description="关于华北地区古生代地层的详细记录",
    tags=["geology", "paleozoic", "stratigraphy"]
)

spatial_data = SpatialData(metadata=metadata)
created_data = await client.create_spatial_data(spatial_data)
```

---

## 🔍 搜索功能

| 方法 | 调用方式 | 说明 |
|------|----------|------|
| **复杂搜索** | `await client.search_spatial_data(search_filter, page, page_size)` | 支持多种条件的搜索 |
| **标签搜索** | `await client.search_by_tags(tags)` | 按标签快速搜索 |

**示例：**
```python
# 按标签搜索
results = await client.search_by_tags(["geology", "stratigraphy"])

# 复杂搜索
search_filter = SearchFilter(
    tags=["geology"],
    keywords=["地层"],
    spatial_bounds={"min_lat": 35.0, "max_lat": 45.0}
)
search_results = await client.search_spatial_data(search_filter)
```

---

## ⚡ 便捷方法

| 方法 | 调用方式 | 说明 |
|------|----------|------|
| **注册+创建** | `await client.register_and_create(handle_id, target_url, spatial_data)` | 一次性完成Handle注册和数据创建 |
| **Handle查询** | `await client.get_by_handle(handle_id)` | 根据Handle ID获取空间数据 |

**示例：**
```python
# 一次性完成Handle注册和数据创建
created_data = await client.register_and_create(
    handle_id="86.1009.24/strata.north-china",
    target_url="https://example.com/data.geojson",
    spatial_data=spatial_data
)
```

---

## 📋 数据模型

### **SpatialMetadata** - 元数据
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

### **SpatialData** - 空间数据
```python
spatial_data = SpatialData(
    metadata=metadata,        # 必填：元数据
    id="数据ID",              # 可选：系统自动生成
    handle_id="Handle标识",    # 可选：Handle ID
    spatial_info={...},       # 可选：空间信息
    temporal_info={...},      # 可选：时间信息
    data_url="数据URL"        # 可选：数据文件地址
)
```

### **SearchFilter** - 搜索过滤器
```python
search_filter = SearchFilter(
    tags=["标签1", "标签2"],           # 可选：按标签过滤
    keywords=["关键词1", "关键词2"],    # 可选：按关键词搜索
    spatial_bounds={...},              # 可选：按空间范围过滤
    temporal_range={...},              # 可选：按时间范围过滤
    data_type="数据类型"               # 可选：按数据类型过滤
)
```

---

## ⚠️ 异常处理

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

---

## 💡 使用提示

1. **异步操作**：所有方法都是异步的，需要使用 `await`
2. **初始化**：使用前必须先调用 `await client.initialize()`
3. **错误处理**：建议使用 try-catch 包装所有操作
4. **数据验证**：确保传入的数据格式正确

---

## 📚 更多资源

- **完整示例**：查看 `examples/` 目录
- **演示脚本**：运行 `python demo.py`
- **详细文档**：查看 `README.md`
- **项目总结**：查看 `PROJECT_SUMMARY.md` 
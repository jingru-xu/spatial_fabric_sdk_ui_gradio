# 构建 Wheel 包

## 🚀 快速构建

```bash
# 使用 uv（推荐）
uv build

# 或者使用 pip
pip install build
python -m build
```

## 📦 构建产物

构建成功后会在 `dist/` 目录生成：
- `spatial_fabric_sdk-1.0.0-py3-none-any.whl` - Wheel包
- `spatial-fabric-sdk-1.0.0.tar.gz` - 源码包

## 🔧 安装

```bash
# 安装Wheel包
pip install dist/spatial-fabric-sdk-1.0.0-py3-none-any.whl

# 或者从源码安装
pip install .
```

## 🌐 启动界面

### Gradio界面
支持公网链接，方便远程访问：
```bash
python run_gradio_ui.py
```

## 界面特性

| 特性 | Gradio界面 |
|------|------------|
| 公网链接 | ✅ 支持 |
| 现代化UI | ✅ 优秀 |
| 响应式设计 | ✅ 支持 |
| 启动速度 | ✅ 快速 |
| 推荐度 | ⭐⭐⭐⭐⭐ | 
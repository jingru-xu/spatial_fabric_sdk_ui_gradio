"""
Spatial Fabric SDK 交互式界面模块
基于Gradio提供Web界面，让用户可以通过图形界面使用SDK功能
支持公网链接访问
"""

# 首先应用SSL修复，必须在任何其他导入之前
from .ssl_fix import apply_ssl_fix
from .handle_ssl_fix import apply_comprehensive_handle_ssl_fix
apply_ssl_fix("gradio_ui")

# 专门针对Handle SDK的全面SSL修复
apply_comprehensive_handle_ssl_fix()

# 设置Handle SDK专用的环境变量
import os
os.environ['HANDLE_TLS_INSECURE'] = 'true'  # 禁用Handle SDK的SSL验证
os.environ['PYTHONHTTPSVERIFY'] = '0'       # 禁用Python的HTTPS验证

import gradio as gr
from typing import Optional, Dict, Any, List, Tuple

# 修复Gradio环境中的事件循环问题
try:
    import nest_asyncio
    nest_asyncio.apply()
    print("✅ 已应用nest_asyncio修复事件循环问题")
except ImportError:
    print("⚠️ nest_asyncio未安装，建议安装: pip install nest-asyncio")

# 使用专门的证书管理器
from .certificate_manager import initialize_certificates, print_certificate_status, get_certificate_status

# 初始化证书管理器
print("🔧 正在初始化证书管理器...")
cert_success = initialize_certificates()
if cert_success:
    print("✅ 证书管理器初始化成功")
    print_certificate_status()
else:
    print("⚠️ 证书管理器初始化失败，将使用不验证SSL模式")

from .client import SpatialFabricClient
from .models import SpatialData, SpatialMetadata, SearchFilter, SearchResult


class SpatialFabricGradioUI:
    """Spatial Fabric SDK Gradio交互式界面类"""
    
    def __init__(self):
        self.client: Optional[SpatialFabricClient] = None
        self.initialized = False
        self.DEFAULT_GARD_URL = "https://your-gard-service.com"
        self.DEFAULT_HANDLE_PREFIX = "86.1009.24"
        self.DEFAULT_PORT_START = 7860
        self.DEFAULT_PORT_MAX = 7870
        self.gard_url = self.DEFAULT_GARD_URL
        self.handle_prefix = self.DEFAULT_HANDLE_PREFIX
        
        # 内部状态：确保只应用一次的修复
        self._nest_asyncio_applied: bool = True  # 顶部已尝试应用
    
    # ---------------------- 内部辅助方法（不改变核心业务逻辑） ----------------------
    # 统一错误消息常量
    _ERR_NOT_INITIALIZED = "客户端未初始化，请先初始化客户端"
    _ERR_ENTER_ID = "请输入数据ID"
    _ERR_ENTER_HANDLE = "请输入Handle ID"
    _ERR_ENTER_TAGS = "请输入标签"
    _ERR_ENTER_FIELD_VALUE = "请输入搜索字段和值"

    def _apply_handle_ssl_env(self) -> None:
        """为Handle相关操作应用SSL修复和必要环境变量。"""
        try:
            from .handle_ssl_fix import apply_comprehensive_handle_ssl_fix
            apply_comprehensive_handle_ssl_fix()
        except Exception as _:
            pass
        try:
            os.environ['HANDLE_TLS_INSECURE'] = 'true'
            os.environ['PYTHONHTTPSVERIFY'] = '0'
        except Exception as _:
            pass
    
    def _ensure_initialized(self) -> Optional[Dict[str, Any]]:
        """统一的初始化校验，未初始化则返回错误结构。"""
        if not self.initialized or not self.client:
            return {"error": self._ERR_NOT_INITIALIZED}
        return None
    
    def _apply_nest_asyncio_once(self) -> None:
        """在需要时再次尝试应用 nest_asyncio（只做轻量尝试）。"""
        if self._nest_asyncio_applied:
            return
        try:
            import nest_asyncio  # type: ignore
            nest_asyncio.apply()
            self._nest_asyncio_applied = True
        except Exception:
            # 忽略不可用场景
            pass

    def _error(self, message: str) -> Dict[str, str]:
        """统一的错误返回结构。"""
        return {"error": message}

    def _split_tags(self, raw: str) -> List[str]:
        """将逗号分隔的标签字符串规范化为列表。"""
        if not raw:
            return []
        return [tag.strip() for tag in raw.split(",") if tag.strip()]

    def _split_csv(self, raw: str) -> List[str]:
        """通用的逗号分隔字符串拆分。"""
        if not raw:
            return []
        return [v.strip() for v in raw.split(",") if v.strip()]

    def _require_nonempty(self, value: Optional[str], message: str) -> Optional[Dict[str, str]]:
        """当字符串为空或None时返回统一错误结构。"""
        if value is None or (isinstance(value, str) and value.strip() == ""):
            return self._error(message)
        return None

    def _build_metadata(self, name: str, description: str, tags: str, data_type: str, is_spatial: bool, is_temporal: bool) -> SpatialMetadata:
        """构建统一的 SpatialMetadata。"""
        return SpatialMetadata(
            name=name,
            description=description,
            tags=self._split_tags(tags),
            type=data_type,
            is_spatial=is_spatial,
            is_temporal=is_temporal
        )
        
    def create_interface(self):
        """创建Gradio界面"""
        with gr.Blocks(
            title="Spatial Fabric SDK",
            theme=gr.themes.Soft(),
            css="""
            .gradio-container {
                max-width: 1200px !important;
            }
            """
        ) as interface:
            
            gr.Markdown("# 🌍 Spatial Fabric SDK 交互式界面")
            gr.Markdown("统一的空间数据管理SDK - 通过图形界面轻松管理空间数据")
            
            # 状态显示
            with gr.Row():
                status_text = gr.Textbox(
                    label="系统状态",
                    value="⚠️ 客户端未初始化",
                    interactive=False
                )
            
            # 配置区域
            with gr.Accordion("⚙️ 系统配置", open=True):
                with gr.Row():
                    gard_url_input = gr.Textbox(
                        label="Gard服务地址",
                        value=self.gard_url,
                        placeholder="https://your-gard-service.com"
                    )
                    handle_prefix_input = gr.Textbox(
                        label="Handle前缀",
                        value=self.handle_prefix,
                        placeholder="86.1009.24"
                    )
                
                with gr.Row():
                    init_btn = gr.Button("🚀 初始化客户端")
                    reset_btn = gr.Button("🔄 重置客户端状态", variant="secondary")
                    init_output = gr.Textbox(label="初始化结果", interactive=False)
            
            # 功能标签页
            with gr.Tabs():
                # Handle管理标签页
                with gr.Tab("🔗 Handle管理"):
                    self._create_handle_management_tab()
                
                # 空间数据管理标签页
                with gr.Tab("📊 空间数据管理"):
                    self._create_spatial_data_tab()
                
                # 搜索功能标签页
                with gr.Tab("🔍 搜索功能"):
                    self._create_search_tab()
                
                # 数据查看标签页
                with gr.Tab("📋 数据查看"):
                    self._create_data_view_tab()
            
            # 绑定初始化事件
            init_btn.click(
                fn=self._initialize_client,
                inputs=[gard_url_input, handle_prefix_input],
                outputs=[init_output, status_text]
            )
            
            # 绑定重置事件
            reset_btn.click(
                fn=self._reset_client,
                inputs=[],
                outputs=[init_output, status_text]
            )
            
        return interface
    
    def _create_handle_management_tab(self):
        """创建Handle管理标签页"""
        with gr.Tabs():
            # 注册Handle
            with gr.Tab("📝 注册Handle"):
                with gr.Row():
                    with gr.Column():
                        handle_id_input = gr.Textbox(label="Handle ID", placeholder="86.1009.24/example.data")
                        target_url_input = gr.Textbox(label="目标URL", placeholder="https://example.com/data.json")
                        name_input = gr.Textbox(label="名称", placeholder="数据名称")
                        description_input = gr.Textbox(label="描述", placeholder="数据描述", lines=3)
                    
                    with gr.Column():
                        tags_input = gr.Textbox(label="标签（用逗号分隔）", placeholder="tag1,tag2,tag3")
                        data_type_input = gr.Dropdown(
                            choices=["GEOMETRY", "RASTER", "VECTOR", "OTHER"],
                            label="数据类型",
                            value="GEOMETRY"
                        )
                        is_spatial_input = gr.Checkbox(label="包含空间信息", value=True)
                        is_temporal_input = gr.Checkbox(label="包含时间信息", value=False)
                
                register_btn = gr.Button("🚀 注册Handle")
                register_output = gr.JSON(label="注册结果")
                
                register_btn.click(
                    fn=self._register_handle,
                    inputs=[
                        handle_id_input, target_url_input, name_input, description_input,
                        tags_input, data_type_input, is_spatial_input, is_temporal_input
                    ],
                    outputs=register_output
                )
            
            # 解析Handle
            with gr.Tab("🔍 解析Handle"):
                parse_handle_id = gr.Textbox(label="输入Handle ID", placeholder="86.1009.24/example.data")
                parse_btn = gr.Button("🔍 解析")
                parse_output = gr.JSON(label="解析结果")
                
                parse_btn.click(
                    fn=self._parse_handle,
                    inputs=parse_handle_id,
                    outputs=parse_output
                )
            
            # 搜索Handle
            with gr.Tab("🔎 搜索Handle"):
                with gr.Row():
                    search_field = gr.Dropdown(
                        choices=["name", "description", "tags", "type"],
                        label="搜索字段",
                        value="name"
                    )
                    search_value = gr.Textbox(label="搜索值")
                    operator = gr.Dropdown(
                        choices=["equals", "contains", "starts_with", "ends_with"],
                        label="操作符",
                        value="contains"
                    )
                
                search_btn = gr.Button("🔍 搜索")
                search_output = gr.JSON(label="搜索结果")
                
                search_btn.click(
                    fn=self._search_handles,
                    inputs=[search_field, search_value, operator],
                    outputs=search_output
                )
    
    def _create_spatial_data_tab(self):
        """创建空间数据管理标签页"""
        with gr.Tabs():
            # 创建数据
            with gr.Tab("➕ 创建数据"):
                with gr.Row():
                    with gr.Column():
                        create_name = gr.Textbox(label="数据名称", placeholder="华北地层数据")
                        create_description = gr.Textbox(label="数据描述", placeholder="关于华北地区古生代地层的详细记录", lines=3)
                        create_tags = gr.Textbox(label="标签（用逗号分隔）", placeholder="geology,paleozoic,stratigraphy")
                        create_type = gr.Dropdown(
                            choices=["GEOMETRY", "RASTER", "VECTOR", "OTHER"],
                            label="数据类型",
                            value="GEOMETRY"
                        )
                    
                    with gr.Column():
                        min_lat = gr.Number(label="最小纬度", value=35.0)
                        max_lat = gr.Number(label="最大纬度", value=45.0)
                        min_lon = gr.Number(label="最小经度", value=110.0)
                        max_lon = gr.Number(label="最大经度", value=120.0)
                        crs = gr.Dropdown(
                            choices=["EPSG:4326", "EPSG:3857", "EPSG:900913"],
                            label="坐标系统",
                            value="EPSG:4326"
                        )
                        data_url = gr.Textbox(label="数据URL", placeholder="https://example.com/data.geojson")
                
                create_btn = gr.Button("🚀 创建数据")
                create_output = gr.JSON(label="创建结果")
                
                create_btn.click(
                    fn=self._create_spatial_data,
                    inputs=[
                        create_name, create_description, create_tags, create_type,
                        min_lat, max_lat, min_lon, max_lon, crs, data_url
                    ],
                    outputs=create_output
                )
            
            # 读取数据
            with gr.Tab("📖 读取数据"):
                read_id = gr.Textbox(label="输入数据ID", placeholder="data_001")
                read_btn = gr.Button("📖 读取")
                read_output = gr.JSON(label="读取结果")
                
                read_btn.click(
                    fn=self._read_spatial_data,
                    inputs=read_id,
                    outputs=read_output
                )
            
            # 更新数据
            with gr.Tab("✏️ 更新数据"):
                update_id = gr.Textbox(label="输入要更新的数据ID", placeholder="data_001")
                update_btn = gr.Button("🔍 查找数据")
                update_output = gr.JSON(label="更新结果")
                
                update_btn.click(
                    fn=self._find_data_for_update,
                    inputs=update_id,
                    outputs=update_output
                )
            
            # 删除数据
            with gr.Tab("🗑️ 删除数据"):
                delete_id = gr.Textbox(label="输入要删除的数据ID", placeholder="data_001")
                delete_btn = gr.Button("🗑️ 删除")
                delete_output = gr.JSON(label="删除结果")
                
                delete_btn.click(
                    fn=self._delete_spatial_data,
                    inputs=delete_id,
                    outputs=delete_output
                )
    
    def _create_search_tab(self):
        """创建搜索功能标签页"""
        with gr.Tabs():
            # 标签搜索
            with gr.Tab("🏷️ 标签搜索"):
                tag_search_input = gr.Textbox(label="输入标签（用逗号分隔）", placeholder="geology,stratigraphy")
                tag_search_btn = gr.Button("🔍 搜索")
                tag_search_output = gr.JSON(label="搜索结果")
                
                tag_search_btn.click(
                    fn=self._search_by_tags,
                    inputs=tag_search_input,
                    outputs=tag_search_output
                )
            
            # 高级搜索
            with gr.Tab("🔎 高级搜索"):
                with gr.Row():
                    with gr.Column():
                        adv_tags = gr.Textbox(label="标签（用逗号分隔）", placeholder="geology,paleozoic")
                        adv_keywords = gr.Textbox(label="关键词（用逗号分隔）", placeholder="地层,古生代")
                        adv_type = gr.Dropdown(
                            choices=["全部", "GEOMETRY", "RASTER", "VECTOR", "OTHER"],
                            label="数据类型",
                            value="全部"
                        )
                    
                    with gr.Column():
                        adv_min_lat = gr.Number(label="最小纬度")
                        adv_max_lat = gr.Number(label="最大纬度")
                        adv_min_lon = gr.Number(label="最小经度")
                        adv_max_lon = gr.Number(label="最大经度")
                
                adv_search_btn = gr.Button("🔍 执行搜索")
                adv_search_output = gr.JSON(label="搜索结果")
                
                adv_search_btn.click(
                    fn=self._advanced_search,
                    inputs=[adv_tags, adv_keywords, adv_type, adv_min_lat, adv_max_lat, adv_min_lon, adv_max_lon],
                    outputs=adv_search_output
                )
    
    def _create_data_view_tab(self):
        """创建数据查看标签页"""
        gr.Markdown("📋 数据查看功能正在开发中...")
    
    def _initialize_client(self, gard_url: str, handle_prefix: str) -> Tuple[str, str]:
        """初始化客户端"""
        try:
            # 在初始化客户端前，重新应用证书设置
            from .certificate_manager import initialize_certificates, get_certificate_status
            from .handle_ssl_fix import apply_comprehensive_handle_ssl_fix
            import os
            
            print(f"🔧 当前工作目录: {os.getcwd()}")
            
            # 重新初始化证书（确保在Gradio环境下正确设置）
            cert_success = initialize_certificates()
            cert_status = get_certificate_status()
            
            # 专门应用Handle SDK全面SSL修复
            apply_comprehensive_handle_ssl_fix()
            
            # 设置Handle SDK专用环境变量
            os.environ['HANDLE_TLS_INSECURE'] = 'true'
            os.environ['PYTHONHTTPSVERIFY'] = '0'
            
            cert_info = f"证书状态: {'✅ 已配置' if cert_success else '⚠️ 未配置'}"
            if cert_status['cert_files_found'] > 0:
                cert_info += f" (找到 {cert_status['cert_files_found']} 个证书文件)"
            cert_info += " | Handle SDK SSL修复已应用"
            
            # 创建客户端
            self.client = SpatialFabricClient(
                gard_base_url=gard_url,
                handle_prefix=handle_prefix
            )
            
            # 尝试同步初始化
            try:
                self.client.initialize_sync()
                self.initialized = True
                self.gard_url = gard_url
                self.handle_prefix = handle_prefix
                
                return (
                    f"✅ 客户端初始化成功！\n"
                    f"🌐 Gard服务: {gard_url}\n"
                    f"🔗 Handle前缀: {handle_prefix}\n"
                    f"🔒 {cert_info}",
                    "✅ 客户端已初始化"
                )
            except Exception as init_error:
                # 如果初始化失败，检查是否是事件循环问题
                error_msg = str(init_error)
                if "Event loop is closed" in error_msg or "loop" in error_msg.lower():
                    # 尝试修复事件循环问题
                    try:
                        self._apply_nest_asyncio_once()
                        
                        # 重新尝试初始化
                        self.client.initialize_sync()
                        self.initialized = True
                        self.gard_url = gard_url
                        self.handle_prefix = handle_prefix
                        
                        return (
                            f"✅ 客户端初始化成功（已修复事件循环问题）！\n"
                            f"🌐 Gard服务: {gard_url}\n"
                            f"🔗 Handle前缀: {handle_prefix}\n"
                            f"🔒 {cert_info}",
                            "✅ 客户端已初始化"
                        )
                    except Exception as retry_error:
                        return (
                            f"❌ 初始化失败（事件循环问题）: {str(retry_error)}\n"
                            f"💡 建议安装: pip install nest-asyncio\n"
                            f"🔒 {cert_info}",
                            "❌ 客户端初始化失败"
                        )
                else:
                    # 其他类型的错误
                    return f"❌ 初始化失败: {error_msg}\n🔒 {cert_info}", "❌ 客户端初始化失败"
            
        except Exception as e:
            self.initialized = False
            return f"❌ 创建客户端失败: {str(e)}", "❌ 客户端初始化失败"
    
    def _reset_client(self) -> Tuple[str, str]:
        """重置客户端状态，解决协程重用问题"""
        try:
            if self.client:
                # 调用客户端的重置方法
                reset_success = self.client.reset_client_state()
                
                if reset_success:
                    self.initialized = False
                    return (
                        "✅ 客户端状态重置成功！\n"
                        "🔄 协程状态已清理\n"
                        "🧹 事件循环已重置\n"
                        "💡 现在可以重新初始化客户端",
                        "🔄 客户端状态已重置"
                    )
                else:
                    return (
                        "⚠️ 客户端状态重置部分成功\n"
                        "💡 建议刷新页面后重新初始化",
                        "⚠️ 客户端状态重置部分成功"
                    )
            else:
                return (
                    "ℹ️ 没有需要重置的客户端\n"
                    "💡 可以直接进行初始化",
                    "ℹ️ 没有需要重置的客户端"
                )
        except Exception as e:
            return (
                f"❌ 重置客户端状态失败: {str(e)}\n"
                "💡 建议刷新页面后重试",
                "❌ 重置客户端状态失败"
            )
    
    def _register_handle(self, handle_id: str, target_url: str, name: str, description: str, tags: str, data_type: str, is_spatial: bool, is_temporal: bool) -> Dict[str, Any]:
        """注册Handle"""
        try:
            not_ready = self._ensure_initialized()
            if not_ready:
                return not_ready
            
            # 在注册前重新应用Handle SDK SSL修复
            try:
                self._apply_handle_ssl_env()
                print(f"🔧 已重新应用Handle SDK全面SSL修复")
            except Exception as ssl_error:
                print(f"⚠️ SSL修复应用失败: {ssl_error}")
            
            # 创建元数据
            metadata = SpatialMetadata(
                name=name,
                description=description,
                tags=[tag.strip() for tag in tags.split(",") if tag.strip()],
                type=data_type,
                is_spatial=is_spatial,
                is_temporal=is_temporal
            )
            
            print(f"🚀 开始注册Handle: {handle_id}")
            print(f"📋 目标URL: {target_url}")
            print(f"🏷️ 元数据: {metadata.name} - {metadata.description}")
            
            # 同步调用
            result = self.client.register_handle_sync(handle_id, target_url, metadata)
            
            print(f"✅ Handle注册成功: {handle_id}")
            return {"success": True, "result": result}
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Handle注册失败: {error_msg}")
            
            # 分析错误类型并提供具体建议
            if "SSL" in error_msg or "certificate" in error_msg.lower():
                return {
                    "error": f"SSL证书验证失败: {error_msg}",
                    "suggestion": "请检查证书配置或联系管理员"
                }
            elif "connection" in error_msg.lower():
                return {
                    "error": f"网络连接失败: {error_msg}",
                    "suggestion": "请检查网络连接和服务器状态"
                }
            elif "timeout" in error_msg.lower():
                return {
                    "error": f"请求超时: {error_msg}",
                    "suggestion": "请检查网络连接或稍后重试"
                }
            elif "Register/registerService" in error_msg:
                return {
                    "error": f"注册服务端点错误: {error_msg}",
                    "suggestion": "注册服务可能配置了更严格的SSL要求"
                }
            else:
                return {"error": f"注册失败: {error_msg}"}
    
    def _parse_handle(self, handle_id: str) -> Dict[str, Any]:
        """解析Handle"""
        try:
            not_ready = self._ensure_initialized()
            if not_ready:
                return not_ready
            
            if not handle_id:
                return self._error(self._ERR_ENTER_HANDLE)
            
            # 同步调用
            result = self.client.resolve_handle_sync(handle_id)
            
            return {"success": True, "result": result}
            
        except Exception as e:
            return {"error": f"解析失败: {str(e)}"}
    
    def _search_handles(self, field: str, value: str, operator: str) -> Dict[str, Any]:
        """搜索Handle"""
        try:
            not_ready = self._ensure_initialized()
            if not_ready:
                return not_ready
            
            if not field or not value:
                return self._error(self._ERR_ENTER_FIELD_VALUE)
            
            # 同步调用（新API：基于filters）
            filters = {field: value}
            result = self.client.search_handles_by_filters_sync(filters)
            
            return {"success": True, "count": len(result), "results": result}
            
        except Exception as e:
            error_msg = str(e)
            if "search_handles" in error_msg:
                error_msg += " (handle_sdk可能不支持此方法)"
            elif "connection" in error_msg.lower():
                error_msg += " (请检查网络连接)"
            return {"error": f"搜索失败: {error_msg}"}
    
    def _create_spatial_data(self, name: str, description: str, tags: str, data_type: str, min_lat: float, max_lat: float, min_lon: float, max_lon: float, crs: str, data_url: str) -> Dict[str, Any]:
        """创建空间数据"""
        try:
            not_ready = self._ensure_initialized()
            if not_ready:
                return not_ready
            
            # 创建元数据
            metadata = self._build_metadata(
                name=name,
                description=description,
                tags=tags,
                data_type=data_type,
                is_spatial=True,
                is_temporal=False
            )
            
            # 创建空间数据
            spatial_data = SpatialData(
                metadata=metadata,
                spatial_info={
                    "bounds": {"min_lat": min_lat, "max_lat": max_lat, "min_lon": min_lon, "max_lon": max_lon},
                    "crs": crs
                },
                data_url=data_url if data_url else None
            )
            
            # 尝试同步调用
            try:
                result = self.client.create_spatial_data_sync(spatial_data)
                
                return {
                    "success": True,
                    "id": result.id,
                    "name": result.metadata.name,
                    "description": result.metadata.description,
                    "tags": result.metadata.tags,
                    "created_at": result.created_at.isoformat() if result.created_at else None
                }
            except Exception as sync_error:
                # 检查是否是事件循环问题
                error_msg = str(sync_error)
                if "Event loop is closed" in error_msg or "loop" in error_msg.lower():
                    # 尝试修复事件循环问题
                    try:
                        self._apply_nest_asyncio_once()
                        
                        # 重新尝试创建 - 使用不同的方法避免协程重用
                        try:
                            # 重新初始化客户端以确保状态正确
                            self.client.initialize_sync()
                            result = self.client.create_spatial_data_sync(spatial_data)
                            
                            return {
                                "success": True,
                                "id": result.id,
                                "name": result.metadata.name,
                                "description": result.metadata.description,
                                "tags": result.metadata.tags,
                                "created_at": result.created_at.isoformat() if result.created_at else None
                            }
                        except Exception as retry_error:
                            return {
                                "error": f"创建失败（重试后仍然失败）: {str(retry_error)}\n"
                                       f"💡 建议检查网络连接和服务器状态"
                            }
                    except Exception as nest_error:
                        return {
                            "error": f"创建失败（事件循环问题）: {str(sync_error)}\n"
                                   f"💡 建议安装: pip install nest-asyncio\n"
                                   f"嵌套错误: {str(nest_error)}"
                        }
                elif "协程已被使用" in error_msg:
                    # 协程重用错误，自动尝试重置客户端状态
                    try:
                        if self.client:
                            reset_success = self.client.reset_client_state()
                            if reset_success:
                                self.initialized = False
                                return {
                                    "error": f"协程重用错误: {error_msg}\n"
                                           f"🔄 已自动重置客户端状态\n"
                                           f"💡 请重新初始化客户端后重试"
                                }
                    except:
                        pass
                    
                    return {
                        "error": f"协程重用错误: {error_msg}\n"
                               f"💡 请点击'重置客户端状态'按钮，然后重新初始化客户端"
                    }
                else:
                    # 其他类型的错误
                    return {"error": f"创建失败: {error_msg}"}
            
        except Exception as e:
            return {"error": f"创建失败: {str(e)}"}
    
    def _read_spatial_data(self, data_id: str) -> Dict[str, Any]:
        """读取空间数据"""
        try:
            not_ready = self._ensure_initialized()
            if not_ready:
                return not_ready
            
            if not data_id:
                return self._error(self._ERR_ENTER_ID)
            
            # 同步调用
            result = self.client.get_spatial_data_sync(data_id)
            
            if result:
                return {
                    "success": True,
                    "id": result.id,
                    "name": result.metadata.name,
                    "description": result.metadata.description,
                    "tags": result.metadata.tags,
                    "spatial_info": result.spatial_info,
                    "temporal_info": result.temporal_info,
                    "created_at": result.created_at.isoformat() if result.created_at else None
                }
            else:
                return {"error": "未找到指定ID的数据"}
            
        except Exception as e:
            return {"error": f"读取失败: {str(e)}"}
    
    def _find_data_for_update(self, data_id: str) -> Dict[str, Any]:
        """查找要更新的数据"""
        try:
            not_ready = self._ensure_initialized()
            if not_ready:
                return not_ready
            
            if not data_id:
                return self._error(self._ERR_ENTER_ID)
            
            # 同步调用
            result = self.client.get_spatial_data_sync(data_id)
            
            if result:
                return {
                    "success": True,
                    "id": result.id,
                    "name": result.metadata.name,
                    "description": result.metadata.description,
                    "tags": result.metadata.tags,
                    "spatial_info": result.spatial_info,
                    "temporal_info": result.temporal_info,
                    "created_at": result.created_at.isoformat() if result.created_at else None
                }
            else:
                return {"error": "未找到指定ID的数据"}
            
        except Exception as e:
            return {"error": f"查找失败: {str(e)}"}
    
    def _update_spatial_data(self, data_id: str, name: str, description: str, tags: str, data_type: str, min_lat: float, max_lat: float, min_lon: float, max_lon: float, crs: str, data_url: str) -> Dict[str, Any]:
        """更新空间数据"""
        try:
            not_ready = self._ensure_initialized()
            if not_ready:
                return not_ready
            
            if not data_id:
                return self._error(self._ERR_ENTER_ID)
            
            # 创建更新的元数据
            metadata = self._build_metadata(
                name=name,
                description=description,
                tags=tags,
                data_type=data_type,
                is_spatial=True,
                is_temporal=False
            )
            
            # 创建更新的空间数据
            spatial_data = SpatialData(
                metadata=metadata,
                spatial_info={
                    "bounds": {"min_lat": min_lat, "max_lat": max_lat, "min_lon": min_lon, "max_lon": max_lon},
                    "crs": crs
                },
                data_url=data_url if data_url else None
            )
            
            # 同步调用
            result = self.client.update_spatial_data_sync(data_id, spatial_data)
            
            return {
                "success": True,
                "id": result.id,
                "name": result.metadata.name,
                "description": result.metadata.description,
                "tags": result.metadata.tags,
                "updated_at": result.updated_at.isoformat() if result.updated_at else None
            }
            
        except Exception as e:
            return {"error": f"更新失败: {str(e)}"}
    
    def _delete_spatial_data(self, data_id: str) -> Dict[str, Any]:
        """删除空间数据"""
        try:
            not_ready = self._ensure_initialized()
            if not_ready:
                return not_ready
            
            if not data_id:
                return self._error("请输入数据ID")
            
            # 同步调用
            result = self.client.delete_spatial_data_sync(data_id)
            
            return {"success": True, "message": f"数据 {data_id} 已成功删除"}
            
        except Exception as e:
            return {"error": f"删除失败: {str(e)}"}
    
    def _search_by_tags(self, tags: str) -> Dict[str, Any]:
        """根据标签搜索数据"""
        try:
            not_ready = self._ensure_initialized()
            if not_ready:
                return not_ready
            
            if not tags:
                return self._error(self._ERR_ENTER_TAGS)
            
            tag_list = self._split_tags(tags)
            
            # 同步调用
            result = self.client.search_by_tags_sync(tag_list)
            
            return {"success": True, "count": len(result), "results": result}
            
        except Exception as e:
            error_msg = str(e)
            if "search_by_tags" in error_msg:
                error_msg += " (pygard可能不支持此方法)"
            elif "connection" in error_msg.lower():
                error_msg += " (请检查网络连接和Gard服务状态)"
            return {"error": f"搜索失败: {error_msg}"}
    
    def _advanced_search(self, tags: str, keywords: str, data_type: str, min_lat, max_lat, min_lon, max_lon):
        """高级搜索"""
        try:
            not_ready = self._ensure_initialized()
            if not_ready:
                return not_ready
            
            # 构建搜索条件
            search_criteria = {}
            
            if tags:
                search_criteria["tags"] = self._split_tags(tags)
            
            if keywords:
                search_criteria["keywords"] = self._split_csv(keywords)
            
            if data_type and data_type != "全部":
                search_criteria["type"] = data_type
            
            if min_lat is not None and max_lat is not None and min_lon is not None and max_lon is not None:
                search_criteria["spatial_bounds"] = {
                    "min_lat": min_lat,
                    "max_lat": max_lat,
                    "min_lon": min_lon,
                    "max_lon": max_lon
                }
            
            # 同步调用
            result = self.client.advanced_search_sync(search_criteria)
            
            return {"success": True, "count": len(result), "results": result}
            
        except Exception as e:
            return {"error": f"高级搜索失败: {str(e)}"}
    
    def launch(self, server_name="0.0.0.0", server_port=None, share=True):
        """启动Gradio界面"""
        interface = self.create_interface()
        
        # 如果没有指定端口，尝试从7860开始找可用端口
        if server_port is None:
            import socket
            server_port = self.DEFAULT_PORT_START
            while server_port < self.DEFAULT_PORT_MAX:  # 尝试7860-7869端口
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.bind(('localhost', server_port))
                        break  # 找到可用端口
                except OSError:
                    server_port += 1
            else:
                server_port = 0  # 让Gradio自动分配端口
        
        print(f"🌐 使用端口: {server_port}")
        return interface.launch(
            server_name=server_name,
            server_port=server_port,
            share=share,
            show_error=True
        )


def gradio_ui():
    """启动Spatial Fabric SDK Gradio界面"""
    print("🚀 正在启动 Spatial Fabric SDK Gradio界面...")
    
    ui_instance = SpatialFabricGradioUI()
    
    # 启动界面
    ui_instance.launch(
        server_name="0.0.0.0",  # 允许外部访问
        server_port=None,       # 自动选择可用端口
        share=True              # 生成公网链接
    )


if __name__ == "__main__":
    gradio_ui()

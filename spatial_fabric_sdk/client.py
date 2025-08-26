"""
Spatial Fabric SDK 主客户端
"""

import asyncio
from typing import Dict, Any, Optional, List, Union
from dataclasses import asdict
from datetime import datetime
import time # Added for time-based reset

# 首先应用SSL修复，必须在handle_sdk导入之前
from .ssl_fix import apply_ssl_fix, apply_handle_sdk_ssl_fix
apply_ssl_fix("client")

# 专门针对handle_sdk的SSL修复
apply_handle_sdk_ssl_fix()

# 导入封装的SDK，添加错误处理
try:
    from handle_sdk import register_handle, parse_handle
    HANDLE_SDK_AVAILABLE = True
    print("✅ Handle SDK 导入成功")
        
except ImportError:
    HANDLE_SDK_AVAILABLE = False
    print("⚠️  警告: handle_sdk 未安装，Handle相关功能将不可用")
    print("   请先安装: pip install handle_sdk-2.0.0-py3-none-any.whl")

try:
    from pygard import GardClient, Gard, GardFilter
    PYGARD_SDK_AVAILABLE = True
except ImportError:
    PYGARD_SDK_AVAILABLE = False
    print("⚠️  警告: pygard 未安装，空间数据管理功能将不可用")
    print("   请先安装: pip install pygard-0.1.2-py3-none-any.whl")

from .models import SpatialData, SpatialMetadata, SearchFilter, SearchResult
from .exceptions import HandleError, GardError, SpatialFabricError, ConfigurationError
from .config import ClientConfig # Added for ClientConfig


class SpatialFabricClient:
    """
    空间数据管理统一客户端
    
    封装了Handle SDK和PyGard SDK，提供统一的空间数据管理接口
    """
    
    def __init__(self, config: Optional[ClientConfig] = None, 
                 gard_base_url: Optional[str] = None,
                 handle_prefix: Optional[str] = None,
                 **kwargs):
        """
        初始化空间数据客户端
        
        Args:
            config: ClientConfig对象，如果提供则忽略其他参数
            gard_base_url: Gard服务的基础URL
            handle_prefix: Handle前缀
            **kwargs: 其他配置参数，会传递给ClientConfig
        """
        if config is not None:
            self.config = config
        else:
            # 从参数创建配置
            config_kwargs = {}
            if gard_base_url is not None:
                config_kwargs['gard_base_url'] = gard_base_url
            if handle_prefix is not None:
                config_kwargs['handle_prefix'] = handle_prefix
            config_kwargs.update(kwargs)
            self.config = ClientConfig(**config_kwargs)
            
        self._gard_client = None
        self._initialized = False
        self._coroutine_cache = {}  # 添加协程缓存跟踪
        self._last_reset_time = time.time()  # 添加重置时间跟踪
        self._reset_threshold = 60  # 60秒后强制重置

    # -------------------- 内部辅助：解析 Handle 返回中的首选访问 URL --------------------
    @staticmethod
    def _extract_preferred_access_url(parsed_handle: Dict[str, Any]) -> Optional[str]:
        """从handle解析结果中提取首选访问URL（若包含storage_descriptor）。"""
        try:
            sd = parsed_handle.get('storage_descriptor') or parsed_handle.get('metadata', {}).get('storage_descriptor')
            if not sd:
                return None
            preferred_type = sd.get('preferred')
            locations = sd.get('storage') or []
            if preferred_type:
                for loc in locations:
                    if loc.get('type') == preferred_type and loc.get('url'):
                        return loc['url']
            # 退化策略：返回第一个有url的
            for loc in locations:
                if loc.get('url'):
                    return loc['url']
        except Exception:
            return None
        return None
        
    async def initialize(self):
        """异步初始化客户端"""
        if self._initialized:
            return
            
        try:
            # 检查pygard是否可用
            if not PYGARD_SDK_AVAILABLE:
                raise ConfigurationError("pygard 未安装，无法初始化客户端。请先安装: pip install pygard-0.1.2-py3-none-any.whl")
            
            # 初始化Gard客户端，使用正确的配置
            from pygard.config import GardConfig
            
            # 创建配置，确保base_url正确
            gard_config = GardConfig(
                base_url=self.config.gard_base_url,
                timeout=30,
                connection_pool_size=10
            )
            
            self._gard_client = GardClient(config=gard_config)
            
            # 启动连接管理器
            await self._gard_client.start()
            
            self._initialized = True
        except Exception as e:
            raise ConfigurationError(f"初始化Gard客户端失败: {e}")
    
    def initialize_sync(self):
        """同步初始化客户端"""
        if self._initialized:
            return
            
        try:
            # 检查pygard是否可用
            if not PYGARD_SDK_AVAILABLE:
                raise ConfigurationError("pygard 未安装，无法初始化客户端。请先安装: pip install pygard-0.1.2-py3-none-any.whl")
            
            # 初始化Gard客户端，使用正确的配置
            from pygard.config import GardConfig
            
            # 创建配置，确保base_url正确
            gard_config = GardConfig(
                base_url=self.config.gard_base_url,
                timeout=30,
                connection_pool_size=10
            )
            
            self._gard_client = GardClient(config=gard_config)
            
            # 同步启动连接管理器
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self._gard_client.start())
                self._initialized = True
            except Exception as e:
                # 如果创建新循环失败，尝试使用现有循环
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_closed():
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                    loop.run_until_complete(self._gard_client.start())
                    self._initialized = True
                except Exception as e2:
                    # 最后的尝试：使用nest_asyncio
                    try:
                        import nest_asyncio
                        nest_asyncio.apply()
                        loop = asyncio.get_event_loop()
                        loop.run_until_complete(self._gard_client.start())
                        self._initialized = True
                    except Exception as e3:
                        raise ConfigurationError(f"初始化Gard客户端失败: {e3}")
                finally:
                    try:
                        if 'loop' in locals() and not loop.is_closed():
                            loop.close()
                    except:
                        pass
                        
        except Exception as e:
            raise ConfigurationError(f"初始化Gard客户端失败: {e}")
    
    def _ensure_initialized(self):
        """确保客户端已初始化"""
        if not self._initialized:
            raise ConfigurationError("客户端尚未初始化，请先调用 initialize() 方法")
    
    def reset_client_state(self):
        """手动重置客户端状态，解决协程重用问题"""
        try:
            # 重置协程状态
            self._reset_coroutine_state()
            
            # 重新初始化客户端
            if self._gard_client:
                try:
                    # 尝试关闭现有客户端
                    if hasattr(self._gard_client, 'close'):
                        import asyncio
                        try:
                            loop = asyncio.get_event_loop()
                            if loop.is_running():
                                # 如果事件循环正在运行，创建任务来关闭
                                loop.create_task(self._gard_client.close())
                            else:
                                loop.run_until_complete(self._gard_client.close())
                        except:
                            pass
                except:
                    pass
                
                self._gard_client = None
                self._initialized = False
            
            # 强制清理事件循环
            try:
                import asyncio
                import gc
                
                # 清理所有待处理的任务
                try:
                    loop = asyncio.get_event_loop()
                    if not loop.is_closed():
                        for task in asyncio.all_tasks(loop):
                            if not task.done():
                                task.cancel()
                except:
                    pass
                
                # 强制垃圾回收
                gc.collect()
                
            except:
                pass
                
            return True
        except Exception as e:
            print(f"重置客户端状态时出现警告: {e}")
            return False
    
    def _reset_coroutine_state(self):
        """重置协程状态，清理缓存"""
        self._coroutine_cache.clear()
        self._last_reset_time = time.time()
        
        # 强制清理事件循环
        try:
            import asyncio
            import gc
            
            # 清理所有待处理的任务
            try:
                loop = asyncio.get_event_loop()
                if not loop.is_closed():
                    for task in asyncio.all_tasks(loop):
                        if not task.done():
                            task.cancel()
            except:
                pass
            
            # 强制垃圾回收
            gc.collect()
            
        except:
            pass
    
    def _should_force_reset(self):
        """检查是否需要强制重置"""
        return time.time() - self._last_reset_time > self._reset_threshold
    
    def _run_async(self, coro):
        """运行异步协程的辅助方法"""
        # 检查是否需要强制重置
        if self._should_force_reset():
            self._reset_coroutine_state()
        
        try:
            # 检查当前线程是否已有事件循环
            try:
                loop = asyncio.get_running_loop()
                # 如果事件循环正在运行，使用线程池
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(self._run_in_new_loop, coro)
                    return future.result(timeout=30)
            except RuntimeError:
                # 如果没有运行的事件循环，创建新的
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    return loop.run_until_complete(coro)
                except Exception as e:
                    # 如果创建新循环失败，尝试使用默认循环
                    try:
                        loop = asyncio.get_event_loop()
                        if loop.is_closed():
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                        return loop.run_until_complete(coro)
                    except Exception as e2:
                        # 最后的尝试：在完全新的环境中运行
                        return self._run_in_completely_new_environment(coro)
                finally:
                    try:
                        if 'loop' in locals() and not loop.is_closed():
                            loop.close()
                    except:
                        pass
        except Exception as e:
            # 如果是协程重用错误，强制重置状态
            if "cannot reuse already awaited coroutine" in str(e):
                self._reset_coroutine_state()
                raise RuntimeError("协程已被使用，已重置状态。请重新调用相应的方法。")
            raise e
    
    def _run_coroutine_safely(self, coro_func, *args, **kwargs):
        """安全运行协程函数，确保每次调用都创建新的协程对象"""
        # 检查是否需要强制重置
        if self._should_force_reset():
            self._reset_coroutine_state()
        
        # 创建协程的唯一标识
        coro_id = f"{coro_func.__name__}_{id(args)}_{id(kwargs)}"
        
        try:
            # 创建新的协程对象
            coro = coro_func(*args, **kwargs)
            
            # 检查协程是否已经被使用过
            if coro_id in self._coroutine_cache:
                # 协程已被使用过，强制重置
                self._reset_coroutine_state()
                raise RuntimeError("检测到协程重用，已重置状态。请重新调用相应的方法。")
            
            # 标记协程为已使用
            self._coroutine_cache[coro_id] = True
            
            return self._run_async_safe(coro)
        except RuntimeError as e:
            if "协程已被使用" in str(e) or "cannot reuse already awaited coroutine" in str(e):
                # 协程重用错误，强制重置并重新创建协程对象
                self._reset_coroutine_state()
                coro = coro_func(*args, **kwargs)
                return self._run_async_safe(coro)
            else:
                raise e
        finally:
            # 清理协程缓存
            if coro_id in self._coroutine_cache:
                del self._coroutine_cache[coro_id]
    
    def _run_async_recreate(self, coro):
        """重新创建协程并运行"""
        try:
            # 获取协程的函数名和参数
            if hasattr(coro, 'cr_code'):
                # 这是一个协程对象，我们需要重新创建它
                # 由于无法直接获取协程的参数，我们返回一个错误
                raise RuntimeError("协程已被使用，无法重新运行。请重新调用相应的方法。")
            else:
                raise RuntimeError("无效的协程对象")
        except Exception as e:
            raise RuntimeError(f"重新创建协程失败: {e}")
    
    def _run_async_safe(self, coro):
        """安全运行协程，处理协程重用问题"""
        try:
            return self._run_async(coro)
        except RuntimeError as e:
            if "协程已被使用" in str(e) or "cannot reuse already awaited coroutine" in str(e):
                # 协程已被使用，尝试重新创建协程
                try:
                    # 获取协程的函数和参数
                    if hasattr(coro, 'cr_code'):
                        # 这是一个协程对象，我们需要重新创建它
                        # 由于无法直接获取协程的参数，我们返回一个错误
                        raise RuntimeError("协程已被使用，无法重新运行。请重新调用相应的方法。")
                    else:
                        raise RuntimeError("无效的协程对象")
                except Exception as recreate_error:
                    raise RuntimeError("协程已被使用，无法重新运行。请重新调用相应的方法。")
            else:
                raise e
    
    def _run_in_new_loop(self, coro):
        """在新线程中运行事件循环"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop.run_until_complete(coro)
        except Exception as e:
            # 如果失败，尝试使用默认循环
            try:
                loop = asyncio.get_event_loop()
                if loop.is_closed():
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                return loop.run_until_complete(coro)
            except Exception as e2:
                # 最后的尝试
                return self._run_in_completely_new_environment(coro)
        finally:
            try:
                if 'loop' in locals() and not loop.is_closed():
                    loop.close()
            except:
                pass
    
    def _run_in_completely_new_environment(self, coro):
        """在完全新的环境中运行协程"""
        import asyncio
        import nest_asyncio
        
        try:
            # 尝试应用nest_asyncio来允许嵌套事件循环
            nest_asyncio.apply()
        except ImportError:
            pass
        
        try:
            # 创建新的事件循环
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop.run_until_complete(coro)
        except Exception as e:
            # 如果还是失败，尝试同步方式
            raise RuntimeError(f"无法运行异步操作: {e}")
        finally:
            try:
                if 'loop' in locals() and not loop.is_closed():
                    loop.close()
            except:
                pass
    
    async def close(self):
        """关闭客户端，清理资源"""
        if self._gard_client and hasattr(self._gard_client, 'close'):
            try:
                await self._gard_client.close()
            except Exception as e:
                print(f"⚠️ 关闭Gard客户端时出现警告: {e}")
        
        self._initialized = False
    
    def __del__(self):
        """析构函数，确保资源被清理"""
        if hasattr(self, '_gard_client') and self._gard_client:
            try:
                # 尝试同步关闭，避免析构时的异步问题
                if hasattr(self._gard_client, '_session') and self._gard_client._session:
                    import asyncio
                    try:
                        loop = asyncio.get_event_loop()
                        if loop.is_running():
                            # 如果事件循环正在运行，创建任务来关闭
                            loop.create_task(self._gard_client.close())
                    except:
                        pass
            except:
                pass

    def _ensure_ssl_certificates(self):
        """确保SSL证书配置已应用"""
        try:
            from .certificate_manager import initialize_certificates, get_certificate_status
            
            # 检查证书状态，如果未初始化则重新初始化
            cert_status = get_certificate_status()
            if not cert_status.get('initialized', False):
                print("🔧 重新应用SSL证书配置...")
                initialize_certificates()
        except Exception as e:
            print(f"⚠️ SSL证书配置检查失败: {e}")

    # ==================== Handle 相关操作 ====================
    
    async def register_spatial_handle(self, 
                                   handle_id: str, 
                                   target_url: str, 
                                   metadata: Union[SpatialMetadata, Dict[str, Any]]) -> Dict[str, Any]:
        """
        注册空间数据Handle
        
        Args:
            handle_id: Handle ID
            target_url: 目标URL
            metadata: 元数据
            
        Returns:
            注册结果
        """
        if not HANDLE_SDK_AVAILABLE:
            raise HandleError("handle_sdk 未安装，无法使用Handle注册功能。请先安装: pip install handle_sdk-2.0.0-py3-none-any.whl")
        
        try:
            # 转换元数据格式
            if isinstance(metadata, SpatialMetadata):
                handle_metadata = {
                    'name': metadata.name,
                    'description': metadata.description,
                    'tags': metadata.tags,
                    'type': metadata.type,
                    'is_spatial': metadata.is_spatial,
                    'is_temporal': metadata.is_temporal,
                    'created_at': metadata.created_at.isoformat() if metadata.created_at else None,
                    **metadata.custom_fields
                }
                # 注入非敏感的存储描述到Handle元数据（如存在）
                if getattr(metadata, 'storage_descriptor', None) is not None:
                    try:
                        handle_metadata['storage_descriptor'] = asdict(metadata.storage_descriptor)
                    except Exception:
                        # 兜底：若序列化失败则忽略
                        pass
            else:
                handle_metadata = metadata
            
            # 调用Handle SDK
            result = register_handle(handle_id, target_url, handle_metadata)
            return result
            
        except Exception as e:
            raise HandleError(f"注册Handle失败: {e}")
    
    def register_spatial_handle_sync(self, 
                                    handle_id: str, 
                                    target_url: str, 
                                    metadata: Union[SpatialMetadata, Dict[str, Any]]) -> Dict[str, Any]:
        """同步版本的注册空间数据Handle"""
        if not HANDLE_SDK_AVAILABLE:
            raise HandleError("handle_sdk 未安装，无法使用Handle注册功能。请先安装: pip install handle_sdk-2.0.0-py3-none-any.whl")
        
        try:
            # 确保SSL证书配置已应用
            self._ensure_ssl_certificates()
            
            # 转换元数据格式
            if isinstance(metadata, SpatialMetadata):
                handle_metadata = {
                    'name': metadata.name,
                    'description': metadata.description,
                    'tags': metadata.tags,
                    'type': metadata.type,
                    'is_spatial': metadata.is_spatial,
                    'is_temporal': metadata.is_temporal,
                    'created_at': metadata.created_at.isoformat() if metadata.created_at else None,
                    **metadata.custom_fields
                }
                if getattr(metadata, 'storage_descriptor', None) is not None:
                    try:
                        handle_metadata['storage_descriptor'] = asdict(metadata.storage_descriptor)
                    except Exception:
                        pass
            else:
                handle_metadata = metadata
            
            # 直接调用Handle SDK（它是同步的）
            result = register_handle(handle_id, target_url, handle_metadata)
            return result
            
        except Exception as e:
            raise HandleError(f"注册Handle失败: {e}")
    
    async def parse_spatial_handle(self, handle_id: str) -> Dict[str, Any]:
        """
        解析空间数据Handle
        
        Args:
            handle_id: Handle ID
            
        Returns:
            解析结果
        """
        if not HANDLE_SDK_AVAILABLE:
            raise HandleError("handle_sdk 未安装，无法使用Handle解析功能。请先安装: pip install handle_sdk-2.0.0-py3-none-any.whl")
        
        try:
            result = parse_handle(handle_id)
            # 增强：补充首选访问URL（若可用）
            preferred = self._extract_preferred_access_url(result)
            if preferred and 'preferred_access_url' not in result:
                result['preferred_access_url'] = preferred
            return result
        except Exception as e:
            raise HandleError(f"解析Handle失败: {e}")
    
    def parse_spatial_handle_sync(self, handle_id: str) -> Dict[str, Any]:
        """同步版本的解析空间数据Handle"""
        if not HANDLE_SDK_AVAILABLE:
            raise HandleError("handle_sdk 未安装，无法使用Handle解析功能。请先安装: pip install handle_sdk-2.0.0-py3-none-any.whl")
        
        try:
            # 确保SSL证书配置已应用
            self._ensure_ssl_certificates()
            result = parse_handle(handle_id)
            preferred = self._extract_preferred_access_url(result)
            if preferred and 'preferred_access_url' not in result:
                result['preferred_access_url'] = preferred
            return result
        except Exception as e:
            raise HandleError(f"解析Handle失败: {e}")
    
    async def search_handles(self, 
                           fields: List[str], 
                           values: List[str], 
                           operators: List[str]) -> List[Dict[str, Any]]:
        """
        搜索Handle
        
        Args:
            fields: 搜索字段
            values: 搜索值
            operators: 搜索操作符
            
        Returns:
            搜索结果列表
        """
        if not HANDLE_SDK_AVAILABLE:
            raise HandleError("handle_sdk 未安装，无法使用搜索Handle功能。请先安装: pip install handle_sdk-2.0.0-py3-none-any.whl")
        
        try:
            # 确保SSL证书配置已应用
            self._ensure_ssl_certificates()
            
            # 尝试导入search_handles函数
            try:
                from handle_sdk import search_handles
                if not callable(search_handles):
                    print("⚠️  注意: handle_sdk 中的 search_handles 不是可调用函数，返回空结果")
                    return []
            except (ImportError, AttributeError):
                # 如果handle_sdk中没有search_handles函数，返回空结果
                print("⚠️  注意: handle_sdk 中没有 search_handles 函数，返回空结果")
                return []
            
            result = search_handles(fields, values, operators)
            return result
        except Exception as e:
            raise HandleError(f"搜索Handle失败: {e}")
    
    def search_handles_sync(self, 
                           fields: List[str], 
                           values: List[str], 
                           operators: List[str]) -> List[Dict[str, Any]]:
        """同步版本的搜索Handle"""
        return self._run_coroutine_safely(self.search_handles, fields, values, operators)
    
    # ==================== Gard 相关操作 ====================
    
    async def create_spatial_data(self, spatial_data: SpatialData) -> SpatialData:
        """
        创建空间数据记录
        
        Args:
            spatial_data: 空间数据对象
            
        Returns:
            创建后的空间数据对象
        """
        if not PYGARD_SDK_AVAILABLE:
            raise GardError("pygard 未安装，无法使用空间数据管理功能。请先安装: pip install pygard-0.1.2-py3-none-any.whl")
        
        self._ensure_initialized()
        
        try:
            # 转换为Gard格式
            gard_record = Gard(
                name=spatial_data.metadata.name,
                description=spatial_data.metadata.description,
                tags=spatial_data.metadata.tags,
                type=spatial_data.metadata.type,
                is_spatial=spatial_data.metadata.is_spatial,
                is_temporal=spatial_data.metadata.is_temporal
            )
            
            # 调用Gard SDK创建
            created_gard = await self._gard_client.create_gard(gard_record)
            
            # 更新返回的数据
            spatial_data.id = created_gard.did
            spatial_data.created_at = datetime.now()
            spatial_data.updated_at = datetime.now()
            
            return spatial_data
            
        except Exception as e:
            raise GardError(f"创建空间数据失败: {e}")
    
    def create_spatial_data_sync(self, spatial_data: SpatialData) -> SpatialData:
        """同步版本的创建空间数据记录"""
        return self._run_coroutine_safely(self.create_spatial_data, spatial_data)
    
    async def get_spatial_data(self, data_id: str) -> Optional[SpatialData]:
        """
        根据ID获取空间数据
        
        Args:
            data_id: 数据ID
            
        Returns:
            空间数据对象，如果不存在则返回None
        """
        self._ensure_initialized()
        
        try:
            gard_record = await self._gard_client.get_gard(data_id)
            if not gard_record:
                return None
            
            # 转换为SpatialData格式
            spatial_data = SpatialData(
                id=gard_record.did,
                metadata=SpatialMetadata(
                    name=gard_record.name,
                    description=getattr(gard_record, 'description', None),
                    tags=getattr(gard_record, 'tags', []),
                    type=getattr(gard_record, 'type', 'GEOMETRY'),
                    is_spatial=getattr(gard_record, 'is_spatial', True),
                    is_temporal=getattr(gard_record, 'is_temporal', False)
                )
            )
            
            return spatial_data
            
        except Exception as e:
            raise GardError(f"获取空间数据失败: {e}")
    
    def get_spatial_data_sync(self, data_id: str) -> Optional[SpatialData]:
        """同步版本的根据ID获取空间数据"""
        return self._run_coroutine_safely(self.get_spatial_data, data_id)
    
    async def update_spatial_data(self, data_id: str, spatial_data: SpatialData) -> SpatialData:
        """
        更新空间数据
        
        Args:
            data_id: 数据ID
            spatial_data: 更新的空间数据
            
        Returns:
            更新后的空间数据对象
        """
        self._ensure_initialized()
        
        try:
            # 先获取现有数据
            existing_data = await self.get_spatial_data(data_id)
            if not existing_data:
                raise GardError(f"数据ID {data_id} 不存在")
            
            # 转换为Gard格式
            gard_record = Gard(
                name=spatial_data.metadata.name,
                description=spatial_data.metadata.description,
                tags=spatial_data.metadata.tags,
                type=spatial_data.metadata.type,
                is_spatial=spatial_data.metadata.is_spatial,
                is_temporal=spatial_data.metadata.is_temporal
            )
            
            # 调用Gard SDK更新
            updated_gard = await self._gard_client.update_gard(data_id, gard_record)
            
            # 更新返回的数据
            spatial_data.id = data_id
            spatial_data.updated_at = datetime.now()
            
            return spatial_data
            
        except Exception as e:
            raise GardError(f"更新空间数据失败: {e}")
    
    def update_spatial_data_sync(self, data_id: str, spatial_data: SpatialData) -> SpatialData:
        """同步版本的更新空间数据"""
        return self._run_coroutine_safely(self.update_spatial_data, data_id, spatial_data)
    
    async def delete_spatial_data(self, data_id: str) -> bool:
        """
        删除空间数据
        
        Args:
            data_id: 数据ID
            
        Returns:
            是否删除成功
        """
        self._ensure_initialized()
        
        try:
            await self._gard_client.delete_gard(data_id)
            return True
        except Exception as e:
            raise GardError(f"删除空间数据失败: {e}")
    
    def delete_spatial_data_sync(self, data_id: str) -> bool:
        """同步版本的删除空间数据"""
        return self._run_coroutine_safely(self.delete_spatial_data, data_id)
    
    async def search_spatial_data(self, 
                                search_filter: SearchFilter,
                                page: int = 1,
                                page_size: int = 10) -> SearchResult:
        """
        搜索空间数据
        
        Args:
            search_filter: 搜索过滤器
            page: 页码
            page_size: 每页大小
            
        Returns:
            搜索结果
        """
        self._ensure_initialized()
        
        try:
            # 构建GardFilter
            gard_filter = GardFilter()
            
            if search_filter.tags:
                gard_filter.tags = search_filter.tags
            
            if search_filter.keywords:
                # 这里需要根据实际的GardFilter实现来设置关键词
                pass
            
            # 调用Gard SDK搜索
            search_results = await self._gard_client.search_gards(gard_filter, page=page, size=page_size)
            
            # 转换为SearchResult格式
            records = []
            for gard_record in search_results.records:
                spatial_data = SpatialData(
                    id=gard_record.did,
                    metadata=SpatialMetadata(
                        name=gard_record.name,
                        description=getattr(gard_record, 'description', None),
                        tags=getattr(gard_record, 'tags', []),
                        type=getattr(gard_record, 'type', 'GEOMETRY'),
                        is_spatial=getattr(gard_record, 'is_spatial', True),
                        is_temporal=getattr(gard_record, 'is_temporal', False)
                    )
                )
                records.append(spatial_data)
            
            return SearchResult(
                records=records,
                total_count=len(records),  # 这里需要根据实际返回结果获取总数
                page=page,
                page_size=page_size,
                has_next=len(records) == page_size,
                has_previous=page > 1
            )
            
        except Exception as e:
            raise GardError(f"搜索空间数据失败: {e}")
    
    def search_spatial_data_sync(self, 
                                search_filter: SearchFilter,
                                page: int = 1,
                                page_size: int = 10) -> SearchResult:
        """同步版本的搜索空间数据"""
        return self._run_coroutine_safely(self.search_spatial_data, search_filter, page, page_size)
    
    async def search_by_tags(self, tags: List[str]) -> List[SpatialData]:
        """
        根据标签搜索空间数据
        
        Args:
            tags: 标签列表
            
        Returns:
            空间数据列表
        """
        self._ensure_initialized()
        
        try:
            # 检查pygard是否有search_by_tags方法
            if not hasattr(self._gard_client, 'search_by_tags') or not callable(getattr(self._gard_client, 'search_by_tags')):
                print("⚠️  注意: pygard 中没有 search_by_tags 方法，返回空结果")
                return []
            
            search_results = await self._gard_client.search_by_tags(tags)
            
            records = []
            # 检查返回结果的格式
            if hasattr(search_results, 'records'):
                for gard_record in search_results.records:
                    spatial_data = SpatialData(
                        id=getattr(gard_record, 'did', None),
                        metadata=SpatialMetadata(
                            name=getattr(gard_record, 'name', ''),
                            description=getattr(gard_record, 'description', None),
                            tags=getattr(gard_record, 'tags', []),
                            type=getattr(gard_record, 'type', 'GEOMETRY'),
                            is_spatial=getattr(gard_record, 'is_spatial', True),
                            is_temporal=getattr(gard_record, 'is_temporal', False)
                        )
                    )
                    records.append(spatial_data)
            else:
                # 如果返回的是列表格式
                for gard_record in search_results:
                    spatial_data = SpatialData(
                        id=getattr(gard_record, 'did', None),
                        metadata=SpatialMetadata(
                            name=getattr(gard_record, 'name', ''),
                            description=getattr(gard_record, 'description', None),
                            tags=getattr(gard_record, 'tags', []),
                            type=getattr(gard_record, 'type', 'GEOMETRY'),
                            is_spatial=getattr(gard_record, 'is_spatial', True),
                            is_temporal=getattr(gard_record, 'is_temporal', False)
                        )
                    )
                    records.append(spatial_data)
            
            return records
            
        except Exception as e:
            error_msg = f"根据标签搜索失败: {e}"
            if "search_by_tags" in str(e):
                error_msg += " (pygard可能不支持此方法)"
            elif "connection" in str(e).lower():
                error_msg += " (请检查网络连接和Gard服务状态)"
            raise GardError(error_msg)
    
    def search_by_tags_sync(self, tags: List[str]) -> List[SpatialData]:
        """同步版本的根据标签搜索空间数据"""
        return self._run_coroutine_safely(self.search_by_tags, tags)
    
    # ==================== 便捷方法 ====================
    
    async def register_and_create(self, 
                                handle_id: str,
                                target_url: str,
                                spatial_data: SpatialData) -> SpatialData:
        """
        注册Handle并创建空间数据的便捷方法
        
        Args:
            handle_id: Handle ID
            target_url: 目标URL
            spatial_data: 空间数据
            
        Returns:
            创建后的空间数据对象
        """
        # 先注册Handle
        await self.register_spatial_handle(handle_id, target_url, spatial_data.metadata)
        
        # 再创建空间数据
        created_data = await self.create_spatial_data(spatial_data)
        
        # 更新Handle ID
        created_data.handle_id = handle_id
        
        return created_data
    
    def register_and_create_sync(self, 
                               handle_id: str,
                               target_url: str,
                               spatial_data: SpatialData) -> SpatialData:
        """同步版本的注册Handle并创建空间数据的便捷方法"""
        return self._run_coroutine_safely(self.register_and_create, handle_id, target_url, spatial_data)
    
    async def get_by_handle(self, handle_id: str) -> Optional[SpatialData]:
        """
        根据Handle ID获取空间数据
        
        Args:
            handle_id: Handle ID
            
        Returns:
            空间数据对象
        """
        # 先解析Handle
        handle_info = await self.parse_spatial_handle(handle_id)
        
        # 从Handle信息中提取数据ID或URL，然后获取数据
        # 这里需要根据实际的Handle解析结果来实现
        # 暂时返回None
    
    def get_by_handle_sync(self, handle_id: str) -> Optional[SpatialData]:
        """同步版本的根据Handle ID获取空间数据"""
        return self._run_coroutine_safely(self.get_by_handle, handle_id)
    
    def advanced_search(self, search_criteria: Dict[str, Any]) -> List[SpatialData]:
        """
        高级搜索空间数据
        
        Args:
            search_criteria: 搜索条件字典
            
        Returns:
            空间数据列表
        """
        return self._run_coroutine_safely(self.advanced_search_async, search_criteria)
    
    async def advanced_search_async(self, search_criteria: Dict[str, Any]) -> List[SpatialData]:
        """
        异步高级搜索空间数据
        
        Args:
            search_criteria: 搜索条件字典
            
        Returns:
            空间数据列表
        """
        self._ensure_initialized()
        
        try:
            # 构建搜索过滤器
            search_filter = SearchFilter()
            
            if "tags" in search_criteria:
                search_filter.tags = search_criteria["tags"]
            
            if "keywords" in search_criteria:
                search_filter.keywords = search_criteria["keywords"]
            
            if "type" in search_criteria:
                search_filter.data_type = search_criteria["type"]
            
            if "spatial_bounds" in search_criteria:
                search_filter.spatial_bounds = search_criteria["spatial_bounds"]
            
            # 使用现有的搜索方法
            search_result = await self.search_spatial_data(search_filter)
            return search_result.records
            
        except Exception as e:
            raise GardError(f"高级搜索失败: {e}")
    
    def advanced_search_sync(self, search_criteria: Dict[str, Any]) -> List[SpatialData]:
        """同步版本的高级搜索空间数据"""
        return self._run_coroutine_safely(self.advanced_search_async, search_criteria) 
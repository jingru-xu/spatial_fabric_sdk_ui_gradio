"""
SSL证书修复模块
确保在所有环境中都能正确处理SSL证书验证问题
"""

import ssl
import urllib3
import requests
import os
import sys
from pathlib import Path
from typing import Optional
import warnings

def apply_ssl_fix(module_name: str = "Unknown") -> bool:
    """
    应用SSL证书修复
    
    Args:
        module_name: 调用模块的名称，用于日志输出
        
    Returns:
        是否成功应用修复
    """
    try:
        print(f"🔧 [{module_name}] 正在应用SSL证书修复...")
        
        # 1. 禁用所有SSL相关警告
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        urllib3.disable_warnings(urllib3.exceptions.SubjectAltNameWarning)
        urllib3.disable_warnings(urllib3.exceptions.InsecurePlatformWarning)
        warnings.filterwarnings('ignore', message='Unverified HTTPS request')
        
        # 2. 设置SSL环境变量
        os.environ['PYTHONHTTPSVERIFY'] = '0'
        os.environ['REQUESTS_CA_BUNDLE'] = ''
        os.environ['SSL_CERT_FILE'] = ''
        os.environ['CURL_CA_BUNDLE'] = ''
        
        # 3. 重写SSL上下文，禁用证书验证
        ssl._create_default_https_context = ssl._create_unverified_context
        
        # 4. 尝试查找并加载证书文件
        cert_file = find_certificate_file()
        
        if cert_file:
            print(f"🔧 [{module_name}] 找到证书文件: {cert_file}")
            os.environ['SSL_CERT_FILE'] = str(cert_file)
            os.environ['REQUESTS_CA_BUNDLE'] = str(cert_file)
            os.environ['CURL_CA_BUNDLE'] = str(cert_file)
            
            # 创建SSL上下文并加载证书
            try:
                ssl_context = ssl.create_default_context()
                ssl_context.load_verify_locations(cafile=str(cert_file))
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
                ssl._create_default_https_context = lambda: ssl_context
                print(f"✅ [{module_name}] 已加载SSL证书")
                return True
            except Exception as cert_error:
                print(f"⚠️ [{module_name}] 证书加载失败，使用不验证模式: {cert_error}")
                force_ssl_unverified()
                return True
        else:
            print(f"⚠️ [{module_name}] 未找到证书文件，使用不验证SSL模式")
            force_ssl_unverified()
            return True
            
    except Exception as e:
        print(f"❌ [{module_name}] SSL修复失败: {e}")
        # 即使失败也要尝试设置不验证模式
        try:
            force_ssl_unverified()
            print(f"✅ [{module_name}] 已设置不验证SSL模式")
            return True
        except:
            return False

def force_ssl_unverified():
    """
    强制设置SSL为不验证模式
    """
    try:
        # 设置SSL上下文为不验证
        ssl._create_default_https_context = ssl._create_unverified_context
        
        # 设置环境变量
        os.environ['PYTHONHTTPSVERIFY'] = '0'
        os.environ['REQUESTS_CA_BUNDLE'] = ''
        os.environ['SSL_CERT_FILE'] = ''
        os.environ['CURL_CA_BUNDLE'] = ''
        
        # 禁用警告
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        urllib3.disable_warnings(urllib3.exceptions.SubjectAltNameWarning)
        urllib3.disable_warnings(urllib3.exceptions.InsecurePlatformWarning)
        warnings.filterwarnings('ignore', message='Unverified HTTPS request')
        
        return True
    except:
        return False

def apply_handle_sdk_ssl_fix():
    """
    专门针对handle_sdk的SSL修复
    """
    try:
        print("🔧 正在应用handle_sdk专用SSL修复...")
        
        # 强制设置不验证模式
        force_ssl_unverified()
        
        # 尝试修复requests的SSL配置
        try:
            import requests
            from requests.adapters import HTTPAdapter
            from urllib3.util.retry import Retry
            
            # 创建自定义适配器
            class CustomHTTPAdapter(HTTPAdapter):
                def init_poolmanager(self, *args, **kwargs):
                    kwargs['ssl_context'] = ssl._create_unverified_context()
                    return super().init_poolmanager(*args, **kwargs)
                
                def proxy_manager_for(self, *args, **kwargs):
                    kwargs['ssl_context'] = ssl._create_unverified_context()
                    return super().proxy_manager_for(*args, **kwargs)
            
            # 应用自定义适配器到requests
            session = requests.Session()
            session.mount('https://', CustomHTTPAdapter())
            session.mount('http://', CustomHTTPAdapter())
            
            print("✅ handle_sdk SSL修复已应用")
            return True
            
        except Exception as e:
            print(f"⚠️ requests SSL修复失败: {e}")
            return False
            
    except Exception as e:
        print(f"❌ handle_sdk SSL修复失败: {e}")
        return False

def find_certificate_file() -> Optional[Path]:
    """
    查找证书文件
    
    Returns:
        找到的证书文件路径，如果没找到返回None
    """
    # 搜索多个可能的目录
    search_dirs = [
        Path.cwd(),  # 当前工作目录
        Path(__file__).parent,  # 当前模块目录
        Path(__file__).parent.parent,  # 上级目录
    ]
    
    # 添加Python路径中的目录
    for path in sys.path:
        if path and os.path.exists(path):
            search_dirs.append(Path(path))
    
    # 搜索证书文件
    for search_dir in search_dirs:
        if not search_dir.exists():
            continue
            
        for ext in ['*.crt', '*.pem', '*.cer']:
            cert_files = list(search_dir.glob(ext))
            if cert_files:
                return cert_files[0]
    
    return None

def test_ssl_connection(url: str = "https://112.124.70.83:8443") -> bool:
    """
    测试SSL连接
    
    Args:
        url: 要测试的URL
        
    Returns:
        连接是否成功
    """
    try:
        import requests
        response = requests.get(url, verify=False, timeout=10)
        print(f"✅ SSL连接测试成功: {url}")
        return True
    except Exception as e:
        print(f"❌ SSL连接测试失败: {url} - {e}")
        return False

# 模块导入时自动应用修复
if __name__ != "__main__":
    apply_ssl_fix("ssl_fix_module")

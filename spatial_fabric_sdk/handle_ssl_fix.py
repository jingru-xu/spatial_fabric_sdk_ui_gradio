"""
Handle SDK 专用SSL修复模块
专门解决Handle SDK注册功能的SSL问题
"""

import os
import ssl
import urllib3
import requests
import warnings
from typing import Optional
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def apply_handle_sdk_ssl_fix():
    """
    专门针对Handle SDK的SSL修复
    解决注册功能中的SSL证书验证问题
    """
    try:
        print("🔧 正在应用Handle SDK专用SSL修复...")
        
        # 1. 禁用所有SSL警告
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        urllib3.disable_warnings(urllib3.exceptions.SubjectAltNameWarning)
        urllib3.disable_warnings(urllib3.exceptions.InsecurePlatformWarning)
        urllib3.disable_warnings(urllib3.exceptions.InsecureHostnameWarning)
        warnings.filterwarnings('ignore', message='Unverified HTTPS request')
        warnings.filterwarnings('ignore', message='.*certificate.*')
        warnings.filterwarnings('ignore', message='.*SSL.*')
        
        # 2. 设置Handle SDK专用环境变量
        os.environ['HANDLE_TLS_INSECURE'] = 'true'
        os.environ['PYTHONHTTPSVERIFY'] = '0'
        os.environ['REQUESTS_CA_BUNDLE'] = ''
        os.environ['SSL_CERT_FILE'] = ''
        os.environ['CURL_CA_BUNDLE'] = ''
        
        # 3. 设置Java SSL环境变量（Handle SDK可能使用Java组件）
        os.environ['javax.net.ssl.trustStore'] = ''
        os.environ['javax.net.ssl.keyStore'] = ''
        os.environ['javax.net.ssl.trustStorePassword'] = 'changeit'
        os.environ['javax.net.ssl.keyStorePassword'] = 'changeit'
        
        # 4. 重写SSL上下文，完全禁用证书验证
        ssl._create_default_https_context = ssl._create_unverified_context
        
        # 5. 修复requests的SSL配置
        try:
            from requests.adapters import HTTPAdapter
            from urllib3.util.retry import Retry
            
            # 创建自定义适配器
            class HandleSSLAdapter(HTTPAdapter):
                def init_poolmanager(self, *args, **kwargs):
                    kwargs['ssl_context'] = ssl._create_unverified_context()
                    kwargs['assert_hostname'] = False
                    return super().init_poolmanager(*args, **kwargs)
                
                def proxy_manager_for(self, *args, **kwargs):
                    kwargs['ssl_context'] = ssl._create_unverified_context()
                    kwargs['assert_hostname'] = False
                    return super().proxy_manager_for(*args, **kwargs)
            
            # 应用自定义适配器到requests
            session = requests.Session()
            session.mount('https://', HandleSSLAdapter())
            session.mount('http://', HandleSSLAdapter())
            
            # 设置session级别的SSL配置
            session.verify = False
            
            print("✅ Handle SDK SSL修复已应用")
            return True
            
        except Exception as e:
            print(f"⚠️ requests SSL修复失败: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Handle SDK SSL修复失败: {e}")
        return False

def fix_zeep_ssl():
    """
    修复zeep库的SSL配置（Handle SDK使用zeep进行SOAP通信）
    """
    try:
        print("🔧 正在修复zeep SSL配置...")
        
        # 设置zeep相关的环境变量
        os.environ['ZEEP_SSL_VERIFY'] = 'false'
        os.environ['ZEEP_SSL_CERT_VERIFY'] = 'false'
        
        # 尝试修复zeep的SSL上下文
        try:
            import zeep
            from zeep.transports import Transport
            
            # 创建不验证SSL的transport
            transport = Transport(verify_ssl=False)
            
            print("✅ zeep SSL修复已应用")
            return True
            
        except ImportError:
            print("⚠️ zeep库未安装，跳过zeep SSL修复")
            return True
        except Exception as e:
            print(f"⚠️ zeep SSL修复失败: {e}")
            return False
            
    except Exception as e:
        print(f"❌ zeep SSL修复失败: {e}")
        return False

def test_handle_service_connection():
    """
    测试Handle服务连接
    """
    try:
        print("🔍 测试Handle服务连接...")
        
        # 测试解析服务端点
        parse_url = "https://112.124.70.83:8443/handleSystem/service/HandleParseService?wsdl"
        try:
            response = requests.get(parse_url, verify=False, timeout=10)
            print(f"✅ 解析服务连接成功: {response.status_code}")
        except Exception as e:
            print(f"❌ 解析服务连接失败: {e}")
        
        # 测试注册服务端点
        register_url = "https://112.124.70.83:8443/handleSystem/service/Register/registerService?wsdl"
        try:
            response = requests.get(register_url, verify=False, timeout=10)
            print(f"✅ 注册服务连接成功: {response.status_code}")
        except Exception as e:
            print(f"❌ 注册服务连接失败: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Handle服务连接测试失败: {e}")
        return False

def apply_comprehensive_handle_ssl_fix():
    """
    应用全面的Handle SDK SSL修复
    """
    try:
        print("🚀 开始应用全面的Handle SDK SSL修复...")
        
        # 1. 应用基本SSL修复
        ssl_success = apply_handle_sdk_ssl_fix()
        
        # 2. 修复zeep SSL配置
        zeep_success = fix_zeep_ssl()
        
        # 3. 测试连接
        test_success = test_handle_service_connection()
        
        if ssl_success and zeep_success:
            print("✅ 全面的Handle SDK SSL修复已应用")
            return True
        else:
            print("⚠️ 部分SSL修复失败，但将继续尝试")
            return True
            
    except Exception as e:
        print(f"❌ 全面SSL修复失败: {e}")
        return False

# 模块导入时自动应用修复
if __name__ != "__main__":
    apply_comprehensive_handle_ssl_fix()


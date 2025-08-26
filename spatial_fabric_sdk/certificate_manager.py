"""
SSL证书管理模块
专门处理Gradio环境下的SSL证书问题
"""

import os
import ssl
import urllib3
import requests
from pathlib import Path
from typing import Optional, List, Dict, Any
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 默认常量
DEFAULT_SEARCH_PATHS: List[str] = [
    ".",  # 当前目录
    "certs",
    "certificates",
    "ssl",
    "../certs",
    "../certificates",
    os.path.expanduser("~/certs"),
    os.path.expanduser("~/certificates"),
    "/home/mw/project",
    os.path.join(os.getcwd(), ".."),
]

CERT_EXTENSIONS: List[str] = ["*.crt", "*.pem", "*.cer", "*.p12", "*.jks", "*.keystore"]


class CertificateManager:
    """SSL证书管理器"""
    
    def __init__(self):
        self.cert_paths: List[Path] = []
        self.java_env_vars: Dict[str, str] = {}
        self.ssl_context: Optional[ssl.SSLContext] = None
        self.initialized: bool = False
        
    def find_certificates(self, search_paths: Optional[List[str]] = None) -> List[Path]:
        """查找证书文件"""
        if search_paths is None:
            search_paths = DEFAULT_SEARCH_PATHS
        
        cert_files: List[Path] = []
        
        for search_path in search_paths:
            if not os.path.exists(search_path):
                continue
                
            search_dir = Path(search_path)
            for ext in CERT_EXTENSIONS:
                try:
                    found_files = list(search_dir.glob(ext))
                    cert_files.extend(found_files)
                    if found_files:
                        logger.info(f"在 {search_path} 中找到证书文件: {[f.name for f in found_files]}")
                except Exception as e:
                    logger.warning(f"搜索 {search_path} 中的 {ext} 文件时出错: {e}")
        
        # 去重并保持顺序
        seen: set = set()
        unique_certs: List[Path] = []
        for f in cert_files:
            fp = f.resolve()
            if fp not in seen:
                seen.add(fp)
                unique_certs.append(f)
        logger.info(f"总共找到 {len(unique_certs)} 个证书文件")
        return unique_certs
    
    def setup_java_ssl_environment(self, cert_files: List[Path]) -> Dict[str, str]:
        """设置Java SSL环境变量"""
        java_env = {}
        
        # 查找keystore和truststore文件
        keystore_files = [f for f in cert_files if f.suffix.lower() in ['.p12', '.jks', '.keystore']]
        truststore_files = [f for f in cert_files if 'trust' in f.name.lower() or 'ca' in f.name.lower()]
        
        if keystore_files:
            keystore_path = str(keystore_files[0].absolute())
            java_env['javax.net.ssl.keyStore'] = keystore_path
            java_env['javax.net.ssl.keyStorePassword'] = 'changeit'  # 默认密码
            logger.info(f"设置keystore: {keystore_path}")
        
        if truststore_files:
            truststore_path = str(truststore_files[0].absolute())
            java_env['javax.net.ssl.trustStore'] = truststore_path
            java_env['javax.net.ssl.trustStorePassword'] = 'changeit'  # 默认密码
            logger.info(f"设置truststore: {truststore_path}")
        
        # 如果没有找到专门的truststore，使用第一个证书文件作为truststore
        if not truststore_files and cert_files:
            truststore_path = str(cert_files[0].absolute())
            java_env['javax.net.ssl.trustStore'] = truststore_path
            java_env['javax.net.ssl.trustStorePassword'] = 'changeit'
            logger.info(f"使用证书文件作为truststore: {truststore_path}")
        
        return java_env
    
    def setup_python_ssl_environment(self, cert_files: List[Path]) -> None:
        """设置Python SSL环境变量"""
        # 禁用SSL警告
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        # 设置基本SSL环境变量
        os.environ['PYTHONHTTPSVERIFY'] = '0'
        os.environ['REQUESTS_CA_BUNDLE'] = ''
        os.environ['SSL_CERT_FILE'] = ''
        
        # 如果有证书文件，尝试加载
        if cert_files:
            cert_file = cert_files[0]
            cert_path = str(cert_file.absolute())
            
            os.environ['SSL_CERT_FILE'] = cert_path
            os.environ['REQUESTS_CA_BUNDLE'] = cert_path
            
            try:
                # 创建SSL上下文并加载证书
                ctx: ssl.SSLContext = ssl.create_default_context()
                ctx.load_verify_locations(cafile=cert_path)
                ssl._create_default_https_context = lambda: ctx
                self.ssl_context = ctx
                logger.info(f"✅ 成功加载SSL证书: {cert_path}")
            except Exception as e:
                logger.warning(f"⚠️ 证书加载失败，使用不验证模式: {e}")
                ssl._create_default_https_context = ssl._create_unverified_context
        else:
            # 没有证书文件，使用不验证模式
            logger.warning("⚠️ 未找到证书文件，使用不验证SSL模式")
            ssl._create_default_https_context = ssl._create_unverified_context
    
    def apply_environment_variables(self, java_env: Dict[str, str]) -> None:
        """应用环境变量"""
        for key, value in java_env.items():
            os.environ[key] = value
            logger.info(f"设置环境变量: {key} = {value}")
    
    def initialize(self, search_paths: Optional[List[str]] = None) -> bool:
        """初始化证书管理器"""
        try:
            logger.info("🔧 开始初始化证书管理器...")
            
            # 查找证书文件
            cert_files = self.find_certificates(search_paths)
            self.cert_paths = cert_files
            
            # 设置Java SSL环境
            java_env = self.setup_java_ssl_environment(cert_files)
            self.java_env_vars = java_env
            
            # 应用环境变量
            self.apply_environment_variables(java_env)
            
            # 设置Python SSL环境
            self.setup_python_ssl_environment(cert_files)
            
            self.initialized = True
            logger.info("✅ 证书管理器初始化成功")
            return True
            
        except Exception as e:
            logger.error(f"❌ 证书管理器初始化失败: {e}")
            # 即使失败也要设置不验证模式
            try:
                ssl._create_default_https_context = ssl._create_unverified_context
                logger.info("✅ 已设置不验证SSL模式作为后备")
            except:
                pass
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """获取证书管理器状态"""
        return {
            "initialized": self.initialized,
            "cert_files_found": len(self.cert_paths),
            "cert_paths": [str(p) for p in self.cert_paths],
            "java_env_vars": self.java_env_vars,
            "ssl_context_created": self.ssl_context is not None
        }
    
    def print_status(self) -> None:
        """打印状态信息"""
        status = self.get_status()
        print(f"📋 证书管理器状态:")
        print(f"  初始化状态: {'✅ 已初始化' if status['initialized'] else '❌ 未初始化'}")
        print(f"  找到证书文件: {status['cert_files_found']} 个")
        if status['cert_paths']:
            print(f"  证书路径:")
            for path in status['cert_paths']:
                print(f"    - {path}")
        if status['java_env_vars']:
            print(f"  Java环境变量:")
            for key, value in status['java_env_vars'].items():
                print(f"    - {key} = {value}")
        print(f"  SSL上下文: {'✅ 已创建' if status['ssl_context_created'] else '❌ 未创建'}")


# 全局证书管理器实例
_cert_manager = CertificateManager()


def initialize_certificates(search_paths: Optional[List[str]] = None) -> bool:
    """初始化证书（全局函数）"""
    return _cert_manager.initialize(search_paths)


def get_certificate_status() -> Dict[str, Any]:
    """获取证书状态（全局函数）"""
    return _cert_manager.get_status()


def print_certificate_status() -> None:
    """打印证书状态（全局函数）"""
    _cert_manager.print_status()


def get_cert_manager() -> CertificateManager:
    """获取证书管理器实例"""
    return _cert_manager

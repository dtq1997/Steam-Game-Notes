"""公共工具函数 — SSL 上下文、HTTP 请求封装等

消除原先在 ui.py / ai_generator.py / account_manager.py 中各自重复的
_get_ssl_context() 和 _urlopen() 实现。
"""

import ssl

try:
    import urllib.request
    import urllib.error
    _HAS_URLLIB = True
except ImportError:
    _HAS_URLLIB = False


def get_ssl_context():
    """获取 SSL 上下文，macOS Python 安装后未运行证书脚本时自动 fallback"""
    try:
        ctx = ssl.create_default_context()
        return ctx
    except Exception:
        pass
    ctx = ssl._create_unverified_context()
    return ctx


def urlopen(req, timeout=30):
    """封装 urlopen，自动处理 SSL 证书问题"""
    try:
        return urllib.request.urlopen(req, timeout=timeout)
    except urllib.error.URLError as e:
        if "CERTIFICATE_VERIFY_FAILED" in str(e):
            ctx = ssl._create_unverified_context()
            return urllib.request.urlopen(req, timeout=timeout, context=ctx)
        raise

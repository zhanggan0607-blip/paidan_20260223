"""
CSP 安全中间件
用于 FastAPI 应用，添加 Content-Security-Policy 头值
"""
import logging
import os
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class CSPMiddleware(BaseHTTPMiddleware):
    """
    内容安全策略 (CSP) 中间件，用于防止 XSS、点击劫持等安全威胁
    """
    
    def __init__(
        self,
        app: FastAPI,
        default_src: str = "'self'",
        script_src: str = "'self'",
        style_src: str = "'self'",
        img_src: str = "'self'",
        connect_src: str = "'self'",
        font_src: str = "'self'",
        object_src: str = "'self'",
        report_src: str = "'self'",
    ):
        super().__init__(app)
        self.default_src = default_src
        self.script_src = script_src
        self.style_src = style_src
        self.img_src = img_src
        self.connect_src = connect_src
        self.font_src = font_src
        self.object_src = object_src
        self.report_src = report_src
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        csp = self._build_csp_header(request)
        
        response.headers["Content-Security-Policy"] = csp
        
        return response
    
    def _build_csp_header(self, request: Request) -> str:
        server_host = request.headers.get("host", "")
        
        connect_sources = "'self'"
        if server_host:
            connect_sources += f" https://{server_host} wss://{server_host}"
        
        csp_parts = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://g.alicdn.com",
            "style-src 'self' 'unsafe-inline'",
            "img-src 'self' data: blob: https://sstcp-uploads.oss-cn-shanghai.aliyuncs.com",
            f"connect-src {connect_sources}",
            "font-src 'self' data:",
            "object-src 'none'",
            "frame-ancestors 'self'",
            "base-uri 'self'",
            "form-action 'self'",
        ]
        
        return "; ".join(csp_parts)

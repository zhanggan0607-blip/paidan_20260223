"""
CSP 安全中间件
用于 FastAPI 应用，添加 Content-Security-Policy 头值
使用 nonce 替代 unsafe-inline/unsafe-eval，有效防止 XSS 攻击
"""
import base64
import os
from app.utils.logging_config import get_logger
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = get_logger(__name__)


def _generate_nonce() -> str:
    return base64.b64encode(os.urandom(16)).decode('ascii')


class CSPMiddleware(BaseHTTPMiddleware):
    """
    内容安全策略 (CSP) 中间件，用于防止 XSS、点击劫持等安全威胁
    使用 nonce 机制替代 unsafe-inline/unsafe-eval
    """

    def __init__(
        self,
        app: FastAPI,
        report_only: bool = False,
    ):
        super().__init__(app)
        self.report_only = report_only

    async def dispatch(self, request: Request, call_next):
        nonce = _generate_nonce()
        request.state.csp_nonce = nonce

        response = await call_next(request)

        csp = self._build_csp_header(request, nonce)

        if self.report_only:
            response.headers["Content-Security-Policy-Report-Only"] = csp
        else:
            response.headers["Content-Security-Policy"] = csp

        return response

    def _build_csp_header(self, request: Request, nonce: str) -> str:
        server_host = request.headers.get("host", "")

        connect_sources = "'self'"
        if server_host:
            connect_sources += f" https://{server_host} wss://{server_host}"

        csp_parts = [
            "default-src 'self'",
            f"script-src 'self' 'nonce-{nonce}' https://g.alicdn.com",
            f"style-src 'self' 'nonce-{nonce}'",
            "img-src 'self' data: blob: https://sstcp-uploads.oss-cn-shanghai.aliyuncs.com",
            f"connect-src {connect_sources}",
            "font-src 'self' data: https://at.alicdn.com",
            "object-src 'none'",
            "frame-ancestors 'self'",
            "base-uri 'self'",
            "form-action 'self'",
        ]

        return "; ".join(csp_parts)

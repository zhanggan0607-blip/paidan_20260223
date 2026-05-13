"""
CSRF 防护中间件
为基于 Bearer Token 认证的 API 提供深度防御
检查 Origin/Referer 头，阻止跨站请求伪造
"""
from app.utils.logging_config import get_logger
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.config import get_settings

logger = get_logger(__name__)


class CSRFMiddleware(BaseHTTPMiddleware):
    """
    CSRF 防护中间件

    防护策略：
    1. 对状态变更请求（POST/PUT/DELETE/PATCH）验证 Origin/Referer
    2. 跳过 API Token 认证请求（Bearer Token 本身已提供 CSRF 防护）
    3. 跳过无 Origin 头的请求（移动端/工具类请求）
    4. 白名单路径跳过检查
    """

    SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}
    SKIP_PATHS = {"/api/v1/auth/login", "/api/v1/auth/login-json", "/api/v1/health", "/"}

    def __init__(self, app: FastAPI):
        super().__init__(app)
        settings = get_settings()
        self.allowed_origins = set(settings.cors_origins) if isinstance(settings.cors_origins, list) else {o.strip() for o in settings.cors_origins.split(',')}

    async def dispatch(self, request: Request, call_next):
        if request.method in self.SAFE_METHODS:
            return await call_next(request)

        if request.url.path in self.SKIP_PATHS:
            return await call_next(request)

        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            return await call_next(request)

        origin = request.headers.get("Origin")
        referer = request.headers.get("Referer")

        if not origin and not referer:
            return await call_next(request)

        if origin and not self._is_origin_allowed(origin):
            logger.warning(f"CSRF: Origin not allowed: {origin} for {request.method} {request.url.path}")
            return JSONResponse(
                status_code=403,
                content={"code": 403, "message": "跨站请求被拒绝", "data": None}
            )

        if referer and not self._is_referer_allowed(referer):
            logger.warning(f"CSRF: Referer not allowed: {referer} for {request.method} {request.url.path}")
            return JSONResponse(
                status_code=403,
                content={"code": 403, "message": "跨站请求被拒绝", "data": None}
            )

        return await call_next(request)

    def _is_origin_allowed(self, origin: str) -> bool:
        if "*" in self.allowed_origins:
            return True
        for allowed in self.allowed_origins:
            if origin == allowed or origin.rstrip("/") == allowed.rstrip("/"):
                return True
        return False

    def _is_referer_allowed(self, referer: str) -> bool:
        if "*" in self.allowed_origins:
            return True
        for allowed in self.allowed_origins:
            if referer.startswith(allowed):
                return True
        return False

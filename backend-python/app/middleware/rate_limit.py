import time
from collections import defaultdict
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
    ):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.request_counts: dict[str, dict[str, list[float]]] = defaultdict(
            lambda: {"minute": [], "hour": []}
        )

    def _cleanup_old_requests(self, client_id: str, current_time: float):
        minute_ago = current_time - 60
        hour_ago = current_time - 3600
        
        self.request_counts[client_id]["minute"] = [
            t for t in self.request_counts[client_id]["minute"] if t > minute_ago
        ]
        self.request_counts[client_id]["hour"] = [
            t for t in self.request_counts[client_id]["hour"] if t > hour_ago
        ]

    def _get_client_id(self, request: Request) -> str:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    async def dispatch(self, request: Request, call_next):
        if request.url.path in ["/health", "/", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)

        client_id = self._get_client_id(request)
        current_time = time.time()

        self._cleanup_old_requests(client_id, current_time)

        minute_count = len(self.request_counts[client_id]["minute"])
        hour_count = len(self.request_counts[client_id]["hour"])

        if minute_count >= self.requests_per_minute:
            logger.warning(f"Rate limit exceeded for {client_id}: {minute_count} requests/minute")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "code": 429,
                    "message": "请求过于频繁，请稍后再试",
                    "data": None
                }
            )

        if hour_count >= self.requests_per_hour:
            logger.warning(f"Hourly rate limit exceeded for {client_id}: {hour_count} requests/hour")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "code": 429,
                    "message": "小时请求次数已达上限，请稍后再试",
                    "data": None
                }
            )

        self.request_counts[client_id]["minute"].append(current_time)
        self.request_counts[client_id]["hour"].append(current_time)

        return await call_next(request)

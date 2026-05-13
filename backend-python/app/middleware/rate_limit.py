"""
限流中间件
支持 Redis 共享存储和内存降级，适用于多实例部署
对GET请求使用更宽松的限流策略
对敏感接口（登录、OCR）使用更严格的限流策略
"""
from app.utils.logging_config import get_logger
import threading
import time
from collections import defaultdict

from fastapi import Request, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

logger = get_logger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
        get_requests_per_minute: int = 200,
        get_requests_per_hour: int = 20000,
    ):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.get_requests_per_minute = get_requests_per_minute
        self.get_requests_per_hour = get_requests_per_hour
        self.request_counts: dict[str, dict[str, list[float]]] = defaultdict(
            lambda: {"minute": [], "hour": []}
        )
        self._lock = threading.Lock()
        self._last_cleanup = time.time()
        self._cleanup_interval = 300

    def _get_redis_client(self):
        try:
            from app.services.cache import get_redis_client
            return get_redis_client()
        except (ImportError, ConnectionError, Exception) as e:
            logger.debug(f"Redis客户端获取失败: {e}")
            return None

    def _check_rate_limit_redis(self, client_id: str, is_get: bool = False,
                                 per_minute: int | None = None,
                                 per_hour: int | None = None) -> tuple[bool, bool]:
        redis_client = self._get_redis_client()
        if not redis_client:
            return self._check_rate_limit_memory(client_id, is_get, per_minute, per_hour)

        try:
            current_time = int(time.time())
            minute_key = f"rate_limit:{client_id}:minute:{current_time // 60}"
            hour_key = f"rate_limit:{client_id}:hour:{current_time // 3600}"

            pipe = redis_client.pipeline()
            pipe.incr(minute_key)
            pipe.incr(hour_key)
            pipe.expire(minute_key, 120)
            pipe.expire(hour_key, 7200)
            results = pipe.execute()

            minute_count = results[0]
            hour_count = results[1]

            effective_per_minute = per_minute or (self.get_requests_per_minute if is_get else self.requests_per_minute)
            effective_per_hour = per_hour or (self.get_requests_per_hour if is_get else self.requests_per_hour)

            minute_exceeded = minute_count > effective_per_minute
            hour_exceeded = hour_count > effective_per_hour

            return minute_exceeded, hour_exceeded
        except Exception as e:
            logger.warning(f"Redis限流检查失败，降级到内存: {e}")
            return self._check_rate_limit_memory(client_id, is_get, per_minute, per_hour)

    def _check_rate_limit_memory(self, client_id: str, is_get: bool = False,
                                  per_minute: int | None = None,
                                  per_hour: int | None = None) -> tuple[bool, bool]:
        current_time = time.time()

        with self._lock:
            self._cleanup_inactive_clients(current_time)
            self._cleanup_old_requests(client_id, current_time)

            minute_count = len(self.request_counts[client_id]["minute"])
            hour_count = len(self.request_counts[client_id]["hour"])

            effective_per_minute = per_minute or (self.get_requests_per_minute if is_get else self.requests_per_minute)
            effective_per_hour = per_hour or (self.get_requests_per_hour if is_get else self.requests_per_hour)

            minute_exceeded = minute_count >= effective_per_minute
            hour_exceeded = hour_count >= effective_per_hour

            if not minute_exceeded and not hour_exceeded:
                self.request_counts[client_id]["minute"].append(current_time)
                self.request_counts[client_id]["hour"].append(current_time)

            return minute_exceeded, hour_exceeded

    def _cleanup_old_requests(self, client_id: str, current_time: float):
        minute_ago = current_time - 60
        hour_ago = current_time - 3600

        self.request_counts[client_id]["minute"] = [
            t for t in self.request_counts[client_id]["minute"] if t > minute_ago
        ]
        self.request_counts[client_id]["hour"] = [
            t for t in self.request_counts[client_id]["hour"] if t > hour_ago
        ]

    def _cleanup_inactive_clients(self, current_time: float):
        if current_time - self._last_cleanup < self._cleanup_interval:
            return

        self._last_cleanup = current_time
        hour_ago = current_time - 3600
        inactive_clients = []

        for client_id, counts in self.request_counts.items():
            if not counts["hour"] or max(counts["hour"]) < hour_ago:
                inactive_clients.append(client_id)

        for client_id in inactive_clients:
            del self.request_counts[client_id]

        if inactive_clients:
            logger.debug(f"Cleaned up {len(inactive_clients)} inactive clients from rate limiter")

    def _get_client_id(self, request: Request) -> str:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()
        return request.client.host if request.client else "unknown"

    EXCLUDED_PATHS = {
        "/health",
        "/",
        "/api/v1/health",
        "/api/v1/online/heartbeat",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/api/docs",
        "/api/redoc",
        "/api/openapi.json",
        "/metrics",
    }

    STRICT_RATE_LIMIT_PATHS = {
        "/api/v1/auth/login": (5, 20),
        "/api/v1/auth/login-json": (5, 20),
        "/api/v1/ocr/idcard": (3, 30),
    }

    async def dispatch(self, request: Request, call_next):
        if request.url.path in self.EXCLUDED_PATHS:
            return await call_next(request)

        if request.method == "OPTIONS":
            return await call_next(request)

        client_id = self._get_client_id(request)
        is_get = request.method == "GET"

        strict_limits = self.STRICT_RATE_LIMIT_PATHS.get(request.url.path)
        if strict_limits:
            per_minute, per_hour = strict_limits
            minute_exceeded, hour_exceeded = self._check_rate_limit_redis(
                client_id, is_get, per_minute=per_minute, per_hour=per_hour
            )
        else:
            minute_exceeded, hour_exceeded = self._check_rate_limit_redis(client_id, is_get)

        if minute_exceeded:
            logger.warning(f"Rate limit exceeded for {client_id}: requests/minute")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "code": 429,
                    "message": "请求过于频繁，请稍后再试",
                    "data": None
                }
            )

        if hour_exceeded:
            logger.warning(f"Hourly rate limit exceeded for {client_id}: requests/hour")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "code": 429,
                    "message": "小时请求次数已达上限，请稍后再试",
                    "data": None
                }
            )

        return await call_next(request)

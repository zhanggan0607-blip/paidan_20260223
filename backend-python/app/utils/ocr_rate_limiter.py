import time
from collections import defaultdict
from functools import wraps
from typing import Callable, Any
import logging

logger = logging.getLogger(__name__)

class OCRRateLimiter:
    def __init__(
        self,
        max_requests_per_minute: int = 10,
        max_requests_per_day: int = 100,
        max_requests_per_user_per_day: int = 50
    ):
        self.max_requests_per_minute = max_requests_per_minute
        self.max_requests_per_day = max_requests_per_day
        self.max_requests_per_user_per_day = max_requests_per_user_per_day
        
        self.minute_requests: list[float] = []
        self.day_requests: list[float] = []
        self.user_day_requests: dict[int, list[float]] = defaultdict(list)
        
        self.last_cleanup = time.time()
    
    def _cleanup(self):
        current_time = time.time()
        
        if current_time - self.last_cleanup < 60:
            return
        
        minute_ago = current_time - 60
        day_ago = current_time - 86400
        
        self.minute_requests = [t for t in self.minute_requests if t > minute_ago]
        self.day_requests = [t for t in self.day_requests if t > day_ago]
        
        for user_id in list(self.user_day_requests.keys()):
            self.user_day_requests[user_id] = [
                t for t in self.user_day_requests[user_id] if t > day_ago
            ]
            if not self.user_day_requests[user_id]:
                del self.user_day_requests[user_id]
        
        self.last_cleanup = current_time
    
    def check_rate_limit(self, user_id: int | None = None) -> tuple[bool, str]:
        self._cleanup()
        current_time = time.time()
        
        if len(self.minute_requests) >= self.max_requests_per_minute:
            return False, f"系统繁忙，每分钟最多{self.max_requests_per_minute}次OCR请求"
        
        if len(self.day_requests) >= self.max_requests_per_day:
            return False, f"今日OCR请求次数已达上限({self.max_requests_per_day}次)"
        
        if user_id is not None:
            user_count = len(self.user_day_requests.get(user_id, []))
            if user_count >= self.max_requests_per_user_per_day:
                return False, f"您今日的OCR请求次数已达上限({self.max_requests_per_user_per_day}次)"
        
        return True, ""
    
    def record_request(self, user_id: int | None = None):
        current_time = time.time()
        
        self.minute_requests.append(current_time)
        self.day_requests.append(current_time)
        
        if user_id is not None:
            self.user_day_requests[user_id].append(current_time)
    
    def get_status(self) -> dict:
        self._cleanup()
        return {
            "minute_requests": len(self.minute_requests),
            "minute_limit": self.max_requests_per_minute,
            "day_requests": len(self.day_requests),
            "day_limit": self.max_requests_per_day,
            "active_users": len(self.user_day_requests)
        }


_ocr_rate_limiter: OCRRateLimiter | None = None


def get_ocr_rate_limiter() -> OCRRateLimiter:
    global _ocr_rate_limiter
    if _ocr_rate_limiter is None:
        _ocr_rate_limiter = OCRRateLimiter()
    return _ocr_rate_limiter


def with_ocr_rate_limit(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        limiter = get_ocr_rate_limiter()
        
        user_id = kwargs.get('user_id')
        if user_id is None:
            for arg in args:
                if hasattr(arg, 'user_id'):
                    user_id = arg.user_id
                    break
        
        allowed, message = limiter.check_rate_limit(user_id)
        if not allowed:
            from app.schemas.common import ApiResponse
            return ApiResponse(
                code=429,
                message=message,
                data={"rateLimited": True}
            )
        
        result = await func(*args, **kwargs)
        
        limiter.record_request(user_id)
        
        return result
    
    return wrapper


def check_ocr_rate_limit(user_id: int | None = None) -> tuple[bool, str]:
    limiter = get_ocr_rate_limiter()
    return limiter.check_rate_limit(user_id)


def record_ocr_request(user_id: int | None = None):
    limiter = get_ocr_rate_limiter()
    limiter.record_request(user_id)
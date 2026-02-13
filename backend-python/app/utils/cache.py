import time
import hashlib
import json
from functools import wraps
from typing import Optional, Callable, Any
from fastapi import Request
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)


class CacheItem:
    def __init__(self, data: Any, expires_at: float):
        self.data = data
        self.expires_at = expires_at
        self.created_at = time.time()


class SimpleCache:
    _instance: Optional['SimpleCache'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._cache: dict[str, CacheItem] = {}
        return cls._instance
    
    def get(self, key: str) -> Optional[Any]:
        item = self._cache.get(key)
        if item is None:
            return None
        if time.time() > item.expires_at:
            del self._cache[key]
            return None
        return item.data
    
    def set(self, key: str, data: Any, ttl: int = 300):
        expires_at = time.time() + ttl
        self._cache[key] = CacheItem(data, expires_at)
    
    def delete(self, key: str):
        if key in self._cache:
            del self._cache[key]
    
    def clear(self):
        self._cache.clear()
    
    def cleanup_expired(self):
        current_time = time.time()
        expired_keys = [
            key for key, item in self._cache.items()
            if current_time > item.expires_at
        ]
        for key in expired_keys:
            del self._cache[key]


cache = SimpleCache()


def generate_cache_key(request: Request, extra: Optional[str] = None) -> str:
    key_parts = [
        request.method,
        request.url.path,
        str(dict(sorted(request.query_params.items()))),
        extra or ""
    ]
    key_string = "|".join(key_parts)
    return hashlib.md5(key_string.encode()).hexdigest()


def cached_response(ttl: int = 300, key_prefix: Optional[str] = None):
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if request is None:
                return await func(*args, **kwargs)
            
            cache_key = generate_cache_key(request, key_prefix)
            
            cached_data = cache.get(cache_key)
            if cached_data is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return JSONResponse(
                    content=cached_data,
                    headers={"X-Cache": "HIT"}
                )
            
            result = await func(*args, **kwargs)
            
            if isinstance(result, dict):
                cache.set(cache_key, result, ttl)
                logger.debug(f"Cache set for {cache_key}, TTL={ttl}s")
            
            return result
        return wrapper
    return decorator

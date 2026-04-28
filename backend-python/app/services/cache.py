"""
缓存服务模块
提供Redis缓存功能，支持字典数据、项目信息等高频数据的缓存
"""
import json
import logging
from datetime import timedelta
from functools import wraps
from typing import Any, Callable, TypeVar

from app.config import get_settings

logger = logging.getLogger(__name__)

T = TypeVar('T')

_settings = get_settings()
REDIS_ENABLED = _settings.redis_enabled
REDIS_URL = _settings.redis_url
DEFAULT_CACHE_TTL = _settings.redis_cache_ttl

_redis_client = None


def get_redis_client():
    """
    获取Redis客户端实例（懒加载）
    如果Redis不可用，返回None
    """
    global _redis_client
    
    if not REDIS_ENABLED:
        return None
    
    if _redis_client is not None:
        return _redis_client
    
    try:
        import redis
        _redis_client = redis.from_url(
            REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
        )
        _redis_client.ping()
        logger.info(f"Redis连接成功: {REDIS_URL}")
        return _redis_client
    except Exception as e:
        logger.warning(f"Redis连接失败，将使用无缓存模式: {e}")
        _redis_client = None
        return None


class CacheService:
    """
    缓存服务类
    提供统一的缓存操作接口
    """
    
    def __init__(self):
        self._client = None
    
    @property
    def client(self):
        if self._client is None:
            self._client = get_redis_client()
        return self._client
    
    @property
    def is_available(self) -> bool:
        return self.client is not None
    
    def get(self, key: str) -> Any | None:
        """
        获取缓存值
        
        Args:
            key: 缓存键
            
        Returns:
            缓存值，不存在或Redis不可用时返回None
        """
        if not self.is_available:
            return None
        
        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.warning(f"缓存读取失败 [{key}]: {e}")
            return None
    
    def set(
        self,
        key: str,
        value: Any,
        ttl: int | None = None
    ) -> bool:
        """
        设置缓存值
        
        Args:
            key: 缓存键
            value: 缓存值
            ttl: 过期时间（秒），默认使用配置的DEFAULT_CACHE_TTL
            
        Returns:
            是否设置成功
        """
        if not self.is_available:
            return False
        
        try:
            ttl = ttl or DEFAULT_CACHE_TTL
            self.client.setex(
                key,
                timedelta(seconds=ttl),
                json.dumps(value, ensure_ascii=False, default=str)
            )
            return True
        except Exception as e:
            logger.warning(f"缓存写入失败 [{key}]: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """
        删除缓存
        
        Args:
            key: 缓存键
            
        Returns:
            是否删除成功
        """
        if not self.is_available:
            return False
        
        try:
            self.client.delete(key)
            return True
        except Exception as e:
            logger.warning(f"缓存删除失败 [{key}]: {e}")
            return False
    
    def delete_pattern(self, pattern: str) -> int:
        """
        删除匹配模式的所有缓存键
        
        Args:
            pattern: 键模式（如 "dict:*"）
            
        Returns:
            删除的键数量
        """
        if not self.is_available:
            return 0
        
        try:
            keys = self.client.keys(pattern)
            if keys:
                return self.client.delete(*keys)
            return 0
        except Exception as e:
            logger.warning(f"批量缓存删除失败 [{pattern}]: {e}")
            return 0
    
    def get_or_set(
        self,
        key: str,
        getter: Callable[[], T],
        ttl: int | None = None
    ) -> T:
        """
        获取缓存，不存在时调用getter获取并缓存
        
        Args:
            key: 缓存键
            getter: 获取数据的函数
            ttl: 过期时间
            
        Returns:
            数据
        """
        cached = self.get(key)
        if cached is not None:
            return cached
        
        value = getter()
        self.set(key, value, ttl)
        return value


def cache_result(
    key_prefix: str,
    ttl: int | None = None,
    key_builder: Callable[..., str] | None = None
):
    """
    缓存装饰器
    
    Args:
        key_prefix: 缓存键前缀
        ttl: 过期时间
        key_builder: 自定义键构建函数
        
    Example:
        @cache_result("user", ttl=300)
        def get_user(user_id: int):
            return db.query(User).get(user_id)
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            cache = CacheService()
            
            if key_builder:
                cache_key = key_builder(*args, **kwargs)
            else:
                key_parts = [key_prefix, func.__name__]
                key_parts.extend(str(arg) for arg in args)
                key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
                cache_key = ":".join(key_parts)
            
            cached = cache.get(cache_key)
            if cached is not None:
                return cached
            
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            return result
        
        return wrapper
    return decorator


cache_service = CacheService()

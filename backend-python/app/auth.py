"""
认证模块
提供JWT Token生成和验证功能

安全说明：
- 所有认证必须通过JWT Token完成
- 密码使用bcrypt加密存储
- access_token有效期30分钟，refresh_token有效期15天
- Token黑名单使用Redis存储（内存降级）
"""
import threading
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
import bcrypt
import uuid

from app.config import get_settings
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)

settings = get_settings()
SECRET_KEY = settings.secret_key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 15

_memory_blacklist: dict[str, float] = {}
_memory_blacklist_lock = threading.Lock()
_MEMORY_BLACKLIST_MAX_SIZE = 10000


def _get_redis_client():
    try:
        from app.services.cache import get_redis_client
        return get_redis_client()
    except (ImportError, ConnectionError, Exception) as e:
        logger.debug(f"Redis客户端获取失败: {e}")
        return None


def add_token_to_blacklist(jti: str, exp_seconds: int) -> bool:
    redis_client = _get_redis_client()
    if redis_client:
        try:
            redis_client.setex(f"token_blacklist:{jti}", exp_seconds, "1")
            logger.info(f"Token已加入Redis黑名单: {jti[:8]}...")
            return True
        except Exception as e:
            logger.warning(f"Redis黑名单写入失败，降级到内存: {e}")

    with _memory_blacklist_lock:
        if len(_memory_blacklist) >= _MEMORY_BLACKLIST_MAX_SIZE:
            sorted_items = sorted(_memory_blacklist.items(), key=lambda x: x[1])
            for k, _ in sorted_items[:len(sorted_items) // 2]:
                del _memory_blacklist[k]
        _memory_blacklist[jti] = datetime.now(timezone.utc).timestamp() + exp_seconds
    logger.info(f"Token已加入内存黑名单: {jti[:8]}...")
    return True


def is_token_blacklisted(jti: str) -> bool:
    if not jti:
        return False

    redis_client = _get_redis_client()
    if redis_client:
        try:
            return redis_client.exists(f"token_blacklist:{jti}") > 0
        except Exception as e:
            logger.debug(f"Redis黑名单检查失败: {e}")

    with _memory_blacklist_lock:
        exp = _memory_blacklist.get(jti)
        if exp is None:
            return False
        if datetime.now(timezone.utc).timestamp() > exp:
            del _memory_blacklist[jti]
            return False
        return True


def clear_memory_blacklist() -> None:
    with _memory_blacklist_lock:
        _memory_blacklist.clear()


def blacklist_all_user_tokens(user_id: int) -> int:
    count = 0
    redis_client = _get_redis_client()
    if redis_client:
        try:
            key = f"user_tokens:{user_id}"
            jti_list = redis_client.smembers(key)
            for jti in jti_list:
                ttl = redis_client.ttl(f"token_blacklist:{jti}")
                if ttl and ttl > 0:
                    add_token_to_blacklist(jti, ttl)
                    count += 1
            redis_client.delete(key)
            logger.info(f"已将用户{user_id}的{count}个Token加入黑名单")
        except Exception as e:
            logger.warning(f"Redis批量黑名单操作失败: {e}")
    return count


def _register_user_token(user_id: int, jti: str, exp_seconds: int) -> None:
    redis_client = _get_redis_client()
    if redis_client:
        try:
            key = f"user_tokens:{user_id}"
            redis_client.sadd(key, jti)
            redis_client.expire(key, exp_seconds)
        except Exception as e:
            logger.debug(f"Redis用户Token注册失败: {e}")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    truncated_password = plain_password[:72].encode('utf-8')
    return bcrypt.checkpw(truncated_password, hashed_password.encode('utf-8'))


def get_password_hash(password: str) -> str:
    truncated_password = password[:72].encode('utf-8')
    return bcrypt.hashpw(truncated_password, bcrypt.gensalt()).decode('utf-8')


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    jti = str(uuid.uuid4())
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access", "jti": jti})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    user_id = data.get("user_id")
    if user_id:
        _register_user_token(user_id, jti, ACCESS_TOKEN_EXPIRE_MINUTES * 60)

    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    jti = str(uuid.uuid4())
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh", "jti": jti})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_refresh_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_type = payload.get("type")
        if token_type != "refresh":
            return None
        jti = payload.get("jti")
        if jti and is_token_blacklisted(jti):
            return None
        return payload
    except JWTError:
        return None


def decode_jwt_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        jti = payload.get("jti")
        if jti and is_token_blacklisted(jti):
            return None
        return payload
    except JWTError:
        return None


async def get_current_user(token: str | None = Depends(oauth2_scheme)) -> dict | None:
    if not token:
        return None
    return decode_jwt_token(token)


async def get_current_user_required(token: str = Depends(oauth2_scheme)) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="未登录或登录已过期，请重新登录",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_exception
    payload = decode_jwt_token(token)
    if payload is None:
        raise credentials_exception
    return payload


async def get_current_admin_user(
    request: Request,
    current_user: dict | None = Depends(get_current_user)
) -> dict:
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未登录或登录已过期",
            headers={"WWW-Authenticate": "Bearer"},
        )

    role = current_user.get('role', '')
    if role not in ['管理员', '部门经理', '主管']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要管理员权限"
        )

    return current_user

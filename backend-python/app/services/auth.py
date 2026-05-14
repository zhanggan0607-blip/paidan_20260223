import secrets
import string
import threading
import time
from datetime import datetime

from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.auth import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
    add_token_to_blacklist,
    blacklist_all_user_tokens,
)
from app.models.online_user import OnlineUser
from app.models.personnel import Personnel
from app.utils.logging_config import logger, log_business_operation


MAX_LOGIN_ATTEMPTS = 5
LOGIN_LOCKOUT_SECONDS = 900
LOGIN_LOCKOUT_ENABLED = True

_login_failures: dict[str, list[float]] = {}
_login_lock = threading.Lock()


def _get_redis_client():
    try:
        from app.services.cache import get_redis_client
        return get_redis_client()
    except (ImportError, ConnectionError, Exception) as e:
        logger.debug(f"Redis客户端获取失败: {e}")
        return None


def get_default_password(user: Personnel) -> str:
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(8))


def check_login_lockout(username: str) -> int | None:
    if not LOGIN_LOCKOUT_ENABLED:
        return None
    redis_client = _get_redis_client()
    if redis_client:
        try:
            now = int(time.time())
            minute_key = f"login_fail:{username}:{now // 60}"
            count = redis_client.get(minute_key)
            current_count = int(count) if count else 0
            lockout_key = f"login_lockout:{username}"
            lockout_until = redis_client.get(lockout_key)
            if lockout_until:
                remaining = int(lockout_until) - now
                if remaining > 0:
                    return remaining
                redis_client.delete(lockout_key)
            total = 0
            for i in range(LOGIN_LOCKOUT_SECONDS // 60 + 2):
                bucket_key = f"login_fail:{username}:{(now // 60) - i}"
                val = redis_client.get(bucket_key)
                if val:
                    total += int(val)
            if total >= MAX_LOGIN_ATTEMPTS:
                lockout_until_val = now + LOGIN_LOCKOUT_SECONDS
                redis_client.setex(lockout_key, LOGIN_LOCKOUT_SECONDS, str(lockout_until_val))
                return LOGIN_LOCKOUT_SECONDS
            return None
        except (ConnectionError, TimeoutError, Exception):
            logger.warning("Redis login lockout check failed, falling back to memory")

    with _login_lock:
        attempts = _login_failures.get(username, [])
        now = time.time()
        attempts = [t for t in attempts if now - t < LOGIN_LOCKOUT_SECONDS]
        _login_failures[username] = attempts
        if len(attempts) >= MAX_LOGIN_ATTEMPTS:
            remaining = int(attempts[0] + LOGIN_LOCKOUT_SECONDS - now)
            return max(remaining, 0)
        return None


def record_login_failure(username: str) -> None:
    if not LOGIN_LOCKOUT_ENABLED:
        return
    redis_client = _get_redis_client()
    if redis_client:
        try:
            now = int(time.time())
            minute_key = f"login_fail:{username}:{now // 60}"
            pipe = redis_client.pipeline()
            pipe.incr(minute_key)
            pipe.expire(minute_key, LOGIN_LOCKOUT_SECONDS + 120)
            pipe.execute()
            return
        except (ConnectionError, TimeoutError, Exception):
            logger.warning("Redis login failure record failed, falling back to memory")

    with _login_lock:
        if username not in _login_failures:
            _login_failures[username] = []
        _login_failures[username].append(time.time())


def clear_login_failures(username: str) -> None:
    redis_client = _get_redis_client()
    if redis_client:
        try:
            now = int(time.time())
            cursor = 0
            while True:
                cursor, keys = redis_client.scan(
                    cursor=cursor,
                    match=f"login_fail:{username}:*",
                    count=100,
                )
                if keys:
                    redis_client.delete(*keys)
                if cursor == 0:
                    break
            redis_client.delete(f"login_lockout:{username}")
            return
        except (ConnectionError, TimeoutError, Exception):
            logger.warning("Redis login failures clear failed, falling back to memory")

    with _login_lock:
        _login_failures.pop(username, None)


def update_last_login(db: Session, user: Personnel) -> None:
    user.last_login_at = datetime.utcnow()
    db.commit()


def record_online_status(db: Session, user: Personnel, device_type: str, ip_address: str) -> None:
    now = datetime.utcnow()
    device_type = device_type if device_type in ["pc", "h5"] else "pc"

    existing = db.query(OnlineUser).filter(
        and_(
            OnlineUser.user_id == user.id,
            OnlineUser.device_type == device_type
        )
    ).first()

    if existing:
        existing.last_activity = now
        existing.login_time = now
        existing.ip_address = ip_address
        existing.is_active = True
    else:
        online_user = OnlineUser(
            user_id=user.id,
            user_name=user.name,
            department=user.department,
            role=user.role,
            login_time=now,
            last_activity=now,
            ip_address=ip_address,
            device_type=device_type,
            is_active=True
        )
        db.add(online_user)


@log_business_operation("用户认证")
def authenticate_user(db: Session, username: str, password: str) -> tuple[Personnel, bool]:
    user = db.query(Personnel).filter(Personnel.name == username).first()
    if not user:
        return None, False

    password_valid = False
    need_password_migration = False

    if user.password_hash:
        password_valid = verify_password(password, user.password_hash)
    else:
        default_password = get_default_password(user)
        if password == default_password:
            password_valid = True
            need_password_migration = True

    if not password_valid:
        return None, False

    if need_password_migration:
        user.password_hash = get_password_hash(password)
        db.commit()

    return user, True


def set_user_offline(db: Session, user_id: int) -> str | None:
    existing = db.query(OnlineUser).filter(
        and_(
            OnlineUser.user_id == user_id,
            OnlineUser.is_active == True
        )
    ).first()

    if existing:
        existing.is_active = False
        db.commit()
        return existing.user_name
    return None


@log_business_operation("修改密码")
def change_user_password(db: Session, user_id: int, old_password: str, new_password: str) -> Personnel:
    user = db.query(Personnel).filter(Personnel.id == user_id).first()
    if not user:
        raise ValueError("用户不存在")

    if user.password_hash:
        if not verify_password(old_password, user.password_hash):
            raise ValueError("旧密码不正确")
    else:
        default_password = get_default_password(user)
        if old_password != default_password:
            raise ValueError("旧密码不正确")

    user.password_hash = get_password_hash(new_password)
    user.must_change_password = False
    db.commit()
    db.refresh(user)
    return user


@log_business_operation("重置密码")
def reset_user_password(db: Session, user_id: int, new_password: str) -> Personnel:
    user = db.query(Personnel).filter(Personnel.id == user_id).first()
    if not user:
        raise ValueError("用户不存在")

    user.password_hash = get_password_hash(new_password)
    user.must_change_password = True
    db.commit()
    db.refresh(user)
    return user


def generate_tokens(user: Personnel) -> dict:
    access_token = create_access_token(
        data={
            "sub": user.name,
            "name": user.name,
            "role": user.role,
            "user_id": user.id
        }
    )
    refresh_token = create_refresh_token(
        data={
            "sub": user.name,
            "name": user.name,
            "role": user.role,
            "user_id": user.id
        }
    )
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "role": user.role,
            "department": user.department,
            "phone": user.phone,
            "must_change_password": user.must_change_password
        }
    }

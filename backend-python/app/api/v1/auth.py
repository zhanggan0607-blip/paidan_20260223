"""
用户认证API接口
包含登录、登出、获取用户信息、修改密码等功能
"""
import threading
import time
from datetime import datetime
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.auth import (
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
    get_current_user_required,
    get_password_hash,
    verify_password,
    add_token_to_blacklist,
    blacklist_all_user_tokens,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from app.database import get_db
from app.dependencies import UserInfo
from app.dependencies import get_current_user_required as get_user_info
from app.models.online_user import OnlineUser
from app.models.personnel import Personnel
from app.schemas.common import ApiResponse
from app.websocket import manager

router = APIRouter(prefix="/auth", tags=["Authentication"])

_login_failures: dict[str, list[float]] = {}
_login_lock = threading.Lock()
MAX_LOGIN_ATTEMPTS = 5
LOGIN_LOCKOUT_SECONDS = 900


def _check_login_lockout(username: str) -> int | None:
    with _login_lock:
        attempts = _login_failures.get(username, [])
        now = time.time()
        attempts = [t for t in attempts if now - t < LOGIN_LOCKOUT_SECONDS]
        _login_failures[username] = attempts
        if len(attempts) >= MAX_LOGIN_ATTEMPTS:
            remaining = int(attempts[0] + LOGIN_LOCKOUT_SECONDS - now)
            return max(remaining, 0)
        return None


def _record_login_failure(username: str) -> None:
    with _login_lock:
        if username not in _login_failures:
            _login_failures[username] = []
        _login_failures[username].append(time.time())


def _clear_login_failures(username: str) -> None:
    with _login_lock:
        _login_failures.pop(username, None)


class LoginRequest(BaseModel):
    username: str
    password: str
    device_type: str = "pc"


class ChangePasswordRequest(BaseModel):
    old_password: str = Field(..., min_length=1, description="旧密码")
    new_password: str = Field(..., min_length=6, description="新密码")


def get_default_password(user: Personnel) -> str:
    """
    获取用户默认密码
    默认密码为手机号后6位，如果没有手机号则为"123456"
    """
    if user.phone and len(user.phone) >= 6:
        return user.phone[-6:]
    return "123456"


def update_last_login(db: Session, user: Personnel):
    """
    更新用户最后登录时间
    """
    user.last_login_at = datetime.utcnow()
    db.commit()


def get_client_ip(request: Request) -> str:
    """获取客户端IP地址"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def record_online_status(db: Session, user: Personnel, device_type: str, ip_address: str):
    """
    记录用户在线状态
    @param db: 数据库会话
    @param user: 用户对象
    @param device_type: 设备类型 (pc/h5)
    @param ip_address: IP地址
    """
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


async def _perform_login(
    db: Session,
    username: str,
    password: str,
    device_type: str,
    request: Request
) -> dict:
    lockout_remaining = _check_login_lockout(username)
    if lockout_remaining is not None:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"登录失败次数过多，请{lockout_remaining}秒后重试",
        )

    user = db.query(Personnel).filter(Personnel.name == username).first()

    if not user:
        _record_login_failure(username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

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
        _record_login_failure(username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    _clear_login_failures(username)

    if need_password_migration:
        user.password_hash = get_password_hash(password)
        db.commit()

    update_last_login(db, user)

    ip_address = get_client_ip(request)
    record_online_status(db, user, device_type, ip_address)
    db.commit()

    await manager.broadcast_online_status(
        user_id=user.id,
        user_name=user.name,
        is_online=True,
        device_type=device_type
    )

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


@router.post("/login", response_model=ApiResponse)
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    result = await _perform_login(
        db=db,
        username=form_data.username,
        password=form_data.password,
        device_type="pc",
        request=request
    )

    return ApiResponse(
        code=200,
        message="登录成功",
        data=result
    )


@router.post("/login-json", response_model=ApiResponse)
async def login_json(
    login_req: LoginRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    result = await _perform_login(
        db=db,
        username=login_req.username,
        password=login_req.password,
        device_type=login_req.device_type,
        request=request
    )

    return ApiResponse(
        code=200,
        message="登录成功",
        data=result
    )


@router.post("/logout", response_model=ApiResponse)
async def logout(
    request: Request,
    current_user: UserInfo = Depends(get_user_info),
    db: Session = Depends(get_db)
):
    user_name = None
    if current_user.is_authenticated and current_user.id:
        existing = db.query(OnlineUser).filter(
            and_(
                OnlineUser.user_id == current_user.id,
                OnlineUser.is_active == True
            )
        ).first()
        
        if existing:
            user_name = existing.user_name
            existing.is_active = False
            db.commit()

        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
            try:
                from jose import jwt as jose_jwt
                from app.config import get_settings
                payload = jose_jwt.decode(token, get_settings().secret_key, algorithms=["HS256"])
                jti = payload.get("jti")
                exp = payload.get("exp", 0)
                if jti and exp:
                    import time
                    remaining = int(exp - time.time())
                    if remaining > 0:
                        add_token_to_blacklist(jti, remaining)
            except Exception:
                pass
    
    if user_name:
        await manager.broadcast_online_status(
            user_id=current_user.id,
            user_name=user_name,
            is_online=False
        )
    
    return ApiResponse(
        code=200,
        message="登出成功",
        data=None
    )


@router.get("/me", response_model=ApiResponse)
async def get_current_user_info(
    current_user: dict = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """
    获取当前登录用户信息
    """
    user_id = current_user.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户信息无效"
        )

    user = db.query(Personnel).filter(Personnel.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    return ApiResponse(
        code=200,
        message="success",
        data={
            "id": user.id,
            "name": user.name,
            "role": user.role,
            "department": user.department,
            "phone": user.phone,
            "must_change_password": user.must_change_password
        }
    )


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., description="刷新令牌")


@router.post("/refresh", response_model=ApiResponse)
async def refresh_token(
    refresh_req: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    刷新Token
    使用refresh_token获取新的access_token和refresh_token
    """
    payload = verify_refresh_token(refresh_req.refresh_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="刷新令牌无效或已过期，请重新登录"
        )

    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户信息无效"
        )

    user = db.query(Personnel).filter(Personnel.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    old_jti = payload.get("jti")
    old_exp = payload.get("exp", 0)
    if old_jti and old_exp:
        import time as _time
        remaining = int(old_exp - _time.time())
        if remaining > 0:
            add_token_to_blacklist(old_jti, remaining)

    access_token = create_access_token(
        data={
            "sub": user.name,
            "name": user.name,
            "role": user.role,
            "user_id": user.id
        }
    )
    new_refresh_token = create_refresh_token(
        data={
            "sub": user.name,
            "name": user.name,
            "role": user.role,
            "user_id": user.id
        }
    )

    return ApiResponse(
        code=200,
        message="Token刷新成功",
        data={
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }
    )


@router.post("/change-password", response_model=ApiResponse)
async def change_password(
    password_req: ChangePasswordRequest,
    current_user: UserInfo = Depends(get_user_info),
    db: Session = Depends(get_db)
):
    """
    修改密码
    需要验证旧密码，设置新密码后自动取消强制修改密码标记
    """
    user = db.query(Personnel).filter(Personnel.id == current_user.id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户不存在"
        )

    if user.password_hash:
        if not verify_password(password_req.old_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="旧密码错误"
            )
    else:
        import hmac
        default_password = get_default_password(user)
        if not hmac.compare_digest(password_req.old_password, default_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="旧密码错误"
            )

    if password_req.old_password == password_req.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="新密码不能与旧密码相同"
        )

    user.password_hash = get_password_hash(password_req.new_password)
    user.must_change_password = False
    db.commit()

    blacklist_all_user_tokens(user.id)

    return ApiResponse(
        code=200,
        message="密码修改成功，请重新登录",
        data=None
    )

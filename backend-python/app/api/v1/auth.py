"""
用户认证API接口
包含登录、登出、获取用户信息、修改密码等功能
"""
import time as _time

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth import (
    verify_refresh_token,
    get_current_user_required,
    add_token_to_blacklist,
    blacklist_all_user_tokens,
    decode_jwt_token,
)
from app.database import get_db
from app.dependencies import UserInfo
from app.dependencies import get_current_user_required as get_user_info
from app.dependencies import get_manager_user
from app.models.personnel import Personnel
from app.schemas.auth import LoginRequest, ChangePasswordRequest, RefreshTokenRequest, ResetPasswordRequest
from app.schemas.common import ApiResponse
from app.services.auth import (
    check_login_lockout,
    record_login_failure,
    clear_login_failures,
    authenticate_user,
    update_last_login,
    record_online_status,
    set_user_offline,
    change_user_password,
    reset_user_password,
    generate_tokens,
)
from app.services.personnel import PersonnelService
from app.utils.logging_config import get_logger
from app.websocket import manager

logger = get_logger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


def get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


async def _perform_login(
    db: Session,
    username: str,
    password: str,
    device_type: str,
    request: Request
) -> dict:
    lockout_remaining = check_login_lockout(username)
    if lockout_remaining is not None:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"登录失败次数过多，请{lockout_remaining}秒后重试",
        )

    user, authenticated = authenticate_user(db, username, password)

    if not authenticated:
        record_login_failure(username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    clear_login_failures(username)
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

    return generate_tokens(user)


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

    return ApiResponse(code=200, message="登录成功", data=result)


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

    return ApiResponse(code=200, message="登录成功", data=result)


@router.post("/logout", response_model=ApiResponse)
async def logout(
    request: Request,
    current_user: UserInfo = Depends(get_user_info),
    db: Session = Depends(get_db)
):
    user_name = None
    if current_user.is_authenticated and current_user.id:
        user_name = set_user_offline(db, current_user.id)

        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
            try:
                payload = decode_jwt_token(token)
                if payload:
                    jti = payload.get("jti")
                    exp = payload.get("exp", 0)
                    if jti and exp:
                        remaining = int(exp - _time.time())
                        if remaining > 0:
                            add_token_to_blacklist(jti, remaining)
            except Exception as e:
                logger.debug(f"登出时Token处理失败: {e}")

    if user_name:
        await manager.broadcast_online_status(
            user_id=current_user.id,
            user_name=user_name,
            is_online=False
        )

    return ApiResponse(code=200, message="登出成功", data=None)


@router.get("/me", response_model=ApiResponse)
async def get_current_user_info(
    current_user: dict = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    user_id = current_user.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户信息无效"
        )

    user = PersonnelService(db).get_by_id(user_id)
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


@router.post("/refresh", response_model=ApiResponse)
async def refresh_token(
    refresh_req: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
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

    user = PersonnelService(db).get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    old_jti = payload.get("jti")
    old_exp = payload.get("exp", 0)
    if old_jti and old_exp:
        remaining = int(old_exp - _time.time())
        if remaining > 0:
            add_token_to_blacklist(old_jti, remaining)

    tokens = generate_tokens(user)
    return ApiResponse(
        code=200,
        message="Token刷新成功",
        data={
            "access_token": tokens["access_token"],
            "refresh_token": tokens["refresh_token"],
            "token_type": "bearer"
        }
    )


@router.post("/change-password", response_model=ApiResponse)
async def change_password(
    password_req: ChangePasswordRequest,
    current_user: UserInfo = Depends(get_user_info),
    db: Session = Depends(get_db)
):
    if password_req.old_password == password_req.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="新密码不能与旧密码相同"
        )

    try:
        change_user_password(db, current_user.id, password_req.old_password, password_req.new_password)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    blacklist_all_user_tokens(current_user.id)

    return ApiResponse(code=200, message="密码修改成功，请重新登录", data=None)


@router.post("/reset-password", response_model=ApiResponse)
async def reset_password(
    reset_req: ResetPasswordRequest,
    admin_user: UserInfo = Depends(get_manager_user),
    db: Session = Depends(get_db)
):
    target_user = db.query(Personnel).filter(Personnel.id == reset_req.user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="目标用户不存在"
        )

    try:
        from app.services.auth import AuthService
        AuthService.reset_user_password(db, reset_req.user_id, reset_req.new_password)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    blacklist_all_user_tokens(reset_req.user_id)

    return ApiResponse(
        code=200,
        message=f"已重置用户 {target_user.name} 的密码",
        data={"user_id": reset_req.user_id, "user_name": target_user.name}
    )

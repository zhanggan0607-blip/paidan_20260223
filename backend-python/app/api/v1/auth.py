"""
用户认证API接口
包含登录、登出、获取用户信息、修改密码等功能
"""
from datetime import datetime
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.auth import (
    create_access_token,
    get_current_user_required,
    get_password_hash,
    verify_password,
)
from app.database import get_db
from app.dependencies import UserInfo
from app.dependencies import get_current_user_required as get_user_info
from app.models.online_user import OnlineUser
from app.models.personnel import Personnel
from app.schemas.common import ApiResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


class LoginRequest(BaseModel):
    username: str
    password: str
    device_type: str = "pc"


class ChangePasswordRequest(BaseModel):
    old_password: str = Field(..., min_length=6, description="旧密码")
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
            OnlineUser.is_active == True
        )
    ).first()
    
    if existing:
        existing.last_activity = now
        existing.login_time = now
        existing.ip_address = ip_address
        existing.device_type = device_type
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


@router.post("/login", response_model=ApiResponse)
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    用户登录接口
    使用OAuth2密码模式，用户名为人员姓名
    支持bcrypt加密密码和明文密码（向后兼容）
    """
    user = db.query(Personnel).filter(Personnel.name == form_data.username).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    password_valid = False
    need_password_migration = False

    if user.password_hash:
        password_valid = verify_password(form_data.password, user.password_hash)
    else:
        default_password = get_default_password(user)
        if form_data.password == default_password:
            password_valid = True
            need_password_migration = True

    if not password_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if need_password_migration:
        user.password_hash = get_password_hash(form_data.password)
        db.commit()

    update_last_login(db, user)
    
    ip_address = get_client_ip(request)
    record_online_status(db, user, "pc", ip_address)
    db.commit()

    access_token = create_access_token(
        data={
            "sub": user.name,
            "name": user.name,
            "role": user.role,
            "user_id": user.id
        }
    )

    return ApiResponse(
        code=200,
        message="登录成功",
        data={
            "access_token": access_token,
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
    )


@router.post("/login-json", response_model=ApiResponse)
def login_json(
    login_req: LoginRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    用户登录接口（JSON格式）
    用户名为人员姓名
    支持device_type参数区分PC端和H5端
    """
    user = db.query(Personnel).filter(Personnel.name == login_req.username).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )

    password_valid = False
    need_password_migration = False

    if user.password_hash:
        password_valid = verify_password(login_req.password, user.password_hash)
    else:
        default_password = get_default_password(user)
        if login_req.password == default_password:
            password_valid = True
            need_password_migration = True

    if not password_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )

    if need_password_migration:
        user.password_hash = get_password_hash(login_req.password)
        db.commit()

    update_last_login(db, user)
    
    ip_address = get_client_ip(request)
    record_online_status(db, user, login_req.device_type, ip_address)
    db.commit()

    access_token = create_access_token(
        data={
            "sub": user.name,
            "name": user.name,
            "role": user.role,
            "user_id": user.id
        }
    )

    return ApiResponse(
        code=200,
        message="登录成功",
        data={
            "access_token": access_token,
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
    )


@router.post("/logout", response_model=ApiResponse)
async def logout(
    current_user: UserInfo = Depends(get_user_info),
    db: Session = Depends(get_db)
):
    """
    用户登出接口
    更新用户在线状态为离线
    """
    if current_user.is_authenticated and current_user.id:
        existing = db.query(OnlineUser).filter(
            and_(
                OnlineUser.user_id == current_user.id,
                OnlineUser.is_active == True
            )
        ).first()
        
        if existing:
            existing.is_active = False
            db.commit()
    
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


@router.post("/refresh", response_model=ApiResponse)
async def refresh_token(
    current_user: dict = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """
    刷新Token
    使用当前有效的Token获取新的Token
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

    access_token = create_access_token(
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
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    if user.password_hash:
        if not verify_password(password_req.old_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="旧密码错误"
            )
    else:
        default_password = get_default_password(user)
        if password_req.old_password != default_password:
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

    return ApiResponse(
        code=200,
        message="密码修改成功",
        data=None
    )

"""
用户认证API接口
包含登录、登出、获取用户信息等功能
"""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import and_
from pydantic import BaseModel
from typing import Optional
from app.database import get_db
from app.schemas.common import ApiResponse
from app.models.personnel import Personnel
from app.models.online_user import OnlineUser
from app.auth import create_access_token, get_current_user, get_current_user_required

router = APIRouter(prefix="/auth", tags=["Authentication"])


class LoginRequest(BaseModel):
    username: str
    password: str
    device_type: str = "pc"


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


class UserCreate(BaseModel):
    username: str
    password: str
    name: str
    role: str = "运维人员"


def get_client_ip(request: Request) -> str:
    """获取客户端IP地址"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def record_user_login(db: Session, user: Personnel, device_type: str, ip_address: str):
    """
    记录用户登录到在线用户表
    """
    existing = db.query(OnlineUser).filter(
        and_(
            OnlineUser.user_id == user.id,
            OnlineUser.is_active == True
        )
    ).first()
    
    now = datetime.utcnow()
    
    if existing:
        existing.last_activity = now
        existing.login_time = now
        existing.ip_address = ip_address
        existing.device_type = device_type
        existing.department = user.department
        existing.role = user.role
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
    
    db.commit()


def clean_inactive_users(db: Session):
    """
    清理不活跃用户
    超过30分钟无活动的用户标记为离线
    """
    timeout_threshold = datetime.utcnow() - timedelta(minutes=30)
    inactive_users = db.query(OnlineUser).filter(
        and_(
            OnlineUser.is_active == True,
            OnlineUser.last_activity < timeout_threshold
        )
    ).all()
    
    for user in inactive_users:
        user.is_active = False
    
    if inactive_users:
        db.commit()


@router.post("/login", response_model=ApiResponse)
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    用户登录接口
    使用OAuth2密码模式，用户名为人员姓名，密码默认为手机号后6位
    """
    user = db.query(Personnel).filter(Personnel.name == form_data.username).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    default_password = (user.phone or "")[-6:] if user.phone else "123456"
    
    if not user.phone:
        default_password = "123456"
    
    if form_data.password != default_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(
        data={
            "sub": user.name,
            "name": user.name,
            "role": user.role,
            "user_id": user.id
        }
    )
    
    client_ip = get_client_ip(request)
    record_user_login(db, user, "pc", client_ip)
    clean_inactive_users(db)
    
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
                "phone": user.phone
            }
        }
    )


@router.post("/login-json", response_model=ApiResponse)
def login_json(
    request: Request,
    login_req: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    用户登录接口（JSON格式）
    用户名为人员姓名，密码默认为手机号后6位
    支持device_type参数区分PC端和H5端
    """
    user = db.query(Personnel).filter(Personnel.name == login_req.username).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    default_password = (user.phone or "")[-6:] if user.phone else "123456"
    
    if not user.phone:
        default_password = "123456"
    
    if login_req.password != default_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    access_token = create_access_token(
        data={
            "sub": user.name,
            "name": user.name,
            "role": user.role,
            "user_id": user.id
        }
    )
    
    client_ip = get_client_ip(request)
    device_type = login_req.device_type if login_req.device_type in ["pc", "h5"] else "pc"
    record_user_login(db, user, device_type, client_ip)
    clean_inactive_users(db)
    
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
                "phone": user.phone
            }
        }
    )


@router.post("/logout", response_model=ApiResponse)
async def logout(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_required)
):
    """
    用户登出接口
    将用户标记为离线
    """
    user_id = current_user.get("user_id")
    
    online_users = db.query(OnlineUser).filter(
        and_(
            OnlineUser.user_id == user_id,
            OnlineUser.is_active == True
        )
    ).all()
    
    for user in online_users:
        user.is_active = False
    
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
            "phone": user.phone
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

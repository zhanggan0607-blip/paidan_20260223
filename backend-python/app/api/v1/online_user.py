"""
在线用户API接口
提供在线用户状态记录和管理功能
"""
import logging
import uuid
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import UserInfo, get_current_user_info
from app.models.online_user import OnlineUser
from app.schemas.common import ApiResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/online", tags=["Online User"])


class OnlineLoginRequest(BaseModel):
    """在线登录请求"""
    device_type: str = "h5"
    user_id: int | None = None
    user_name: str | None = None


class HeartbeatRequest(BaseModel):
    """心跳请求 - 支持从token获取用户信息"""
    device_type: str = "h5"


def get_client_ip(request: Request) -> str:
    """获取客户端IP地址"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


@router.post("/login", response_model=ApiResponse)
def record_login(
    request: Request,
    login_req: OnlineLoginRequest,
    db: Session = Depends(get_db)
):
    """
    记录用户登录
    在用户登录时调用，记录登录状态
    """
    try:
        ip_address = get_client_ip(request)
        device_type = login_req.device_type if login_req.device_type in ["pc", "h5"] else "h5"
        now = datetime.utcnow()

        existing = db.query(OnlineUser).filter(
            and_(
                OnlineUser.user_id == login_req.user_id,
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
                user_id=login_req.user_id,
                user_name=login_req.user_name,
                login_time=now,
                last_activity=now,
                ip_address=ip_address,
                device_type=device_type,
                is_active=True
            )
            db.add(online_user)

        db.commit()
        return ApiResponse(code=200, message="登录记录成功", data=None)

    except Exception as e:
        db.rollback()
        error_id = str(uuid.uuid4())[:8]
        logger.error(f"[{error_id}] 记录登录失败: {str(e)}")
        return ApiResponse(code=500, message=f"记录登录失败，错误ID: {error_id}", data=None)


@router.post("/logout", response_model=ApiResponse)
def record_logout(
    request: Request,
    login_req: OnlineLoginRequest,
    db: Session = Depends(get_db)
):
    """
    记录用户登出
    在用户登出时调用，更新在线状态
    """
    try:
        existing = db.query(OnlineUser).filter(
            and_(
                OnlineUser.user_id == login_req.user_id,
                OnlineUser.is_active == True
            )
        ).first()

        if existing:
            existing.is_active = False
            db.commit()

        return ApiResponse(code=200, message="登出记录成功", data=None)

    except Exception as e:
        db.rollback()
        error_id = str(uuid.uuid4())[:8]
        logger.error(f"[{error_id}] 记录登出失败: {str(e)}")
        return ApiResponse(code=500, message=f"记录登出失败，错误ID: {error_id}", data=None)


@router.post("/heartbeat", response_model=ApiResponse)
async def heartbeat(
    request: Request,
    heartbeat_req: HeartbeatRequest,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_info)
):
    """
    心跳接口
    定期更新用户活动时间
    支持从JWT Token获取用户信息，无需在请求体中传递user_id和user_name
    """
    try:
        if not user_info.is_authenticated:
            return ApiResponse(code=401, message="未登录或登录已过期", data=None)

        ip_address = get_client_ip(request)
        now = datetime.utcnow()
        device_type = heartbeat_req.device_type if heartbeat_req.device_type in ["pc", "h5"] else "h5"

        existing = db.query(OnlineUser).filter(
            and_(
                OnlineUser.user_id == user_info.id,
                OnlineUser.is_active == True
            )
        ).first()

        if existing:
            existing.last_activity = now
            existing.ip_address = ip_address
            existing.device_type = device_type
        else:
            online_user = OnlineUser(
                user_id=user_info.id,
                user_name=user_info.name,
                login_time=now,
                last_activity=now,
                ip_address=ip_address,
                device_type=device_type,
                is_active=True
            )
            db.add(online_user)

        db.commit()
        return ApiResponse(code=200, message="心跳更新成功", data=None)

    except Exception as e:
        db.rollback()
        error_id = str(uuid.uuid4())[:8]
        logger.error(f"[{error_id}] 心跳更新失败: {str(e)}")
        return ApiResponse(code=500, message=f"心跳更新失败，错误ID: {error_id}", data=None)


@router.get("/count", response_model=ApiResponse)
def get_online_count(db: Session = Depends(get_db)):
    """
    获取在线用户数量
    """
    try:
        count = db.query(func.count(OnlineUser.id)).filter(
            OnlineUser.is_active == True
        ).scalar()

        return ApiResponse(code=200, message="获取成功", data={"count": count or 0})

    except Exception as e:
        error_id = str(uuid.uuid4())[:8]
        logger.error(f"[{error_id}] 获取在线用户数失败: {str(e)}")
        return ApiResponse(code=500, message=f"获取失败，错误ID: {error_id}", data=None)


@router.get("/users", response_model=ApiResponse)
def get_online_users(db: Session = Depends(get_db)):
    """
    获取在线用户列表
    """
    try:
        users = db.query(OnlineUser).filter(
            OnlineUser.is_active == True
        ).order_by(OnlineUser.login_time.desc()).all()

        return ApiResponse(
            code=200,
            message="获取成功",
            data=[user.to_dict() for user in users]
        )

    except Exception as e:
        error_id = str(uuid.uuid4())[:8]
        logger.error(f"[{error_id}] 获取在线用户列表失败: {str(e)}")
        return ApiResponse(code=500, message=f"获取失败，错误ID: {error_id}", data=None)


@router.get("/statistics", response_model=ApiResponse)
def get_online_statistics(db: Session = Depends(get_db)):
    """
    获取在线用户统计信息
    """
    try:
        total_online = db.query(func.count(OnlineUser.id)).filter(
            OnlineUser.is_active == True
        ).scalar() or 0

        h5_count = db.query(func.count(OnlineUser.id)).filter(
            and_(
                OnlineUser.is_active == True,
                OnlineUser.device_type == "h5"
            )
        ).scalar() or 0

        pc_count = db.query(func.count(OnlineUser.id)).filter(
            and_(
                OnlineUser.is_active == True,
                OnlineUser.device_type == "pc"
            )
        ).scalar() or 0

        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_logins = db.query(func.count(OnlineUser.id)).filter(
            OnlineUser.login_time >= today_start
        ).scalar() or 0

        return ApiResponse(
            code=200,
            message="获取成功",
            data={
                "total_online": total_online,
                "h5_count": h5_count,
                "pc_count": pc_count,
                "today_logins": today_logins
            }
        )

    except Exception as e:
        error_id = str(uuid.uuid4())[:8]
        logger.error(f"[{error_id}] 获取在线用户统计失败: {str(e)}")
        return ApiResponse(code=500, message=f"获取失败，错误ID: {error_id}", data=None)

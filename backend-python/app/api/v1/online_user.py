"""
在线用户API接口
提供在线用户统计和管理功能
"""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import and_
from pydantic import BaseModel
from typing import Optional, List
from app.database import get_db
from app.schemas.common import ApiResponse
from app.models.online_user import OnlineUser
from app.models.personnel import Personnel
from app.auth import get_current_user_required

router = APIRouter(prefix="/online", tags=["Online Users"])

ONLINE_TIMEOUT_MINUTES = 15


class HeartbeatRequest(BaseModel):
    """心跳请求"""
    device_type: str = "pc"


class OnlineUserResponse(BaseModel):
    """在线用户响应"""
    id: int
    user_id: int
    user_name: str
    department: Optional[str]
    role: Optional[str]
    login_time: str
    last_activity: str
    ip_address: Optional[str]
    device_type: str
    is_active: bool


def get_client_ip(request: Request) -> str:
    """获取客户端IP地址"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def clean_inactive_users(db: Session) -> int:
    """
    清理不活跃用户
    超过ONLINE_TIMEOUT_MINUTES分钟无活动的用户标记为离线
    返回清理的用户数量
    """
    timeout_threshold = datetime.utcnow() - timedelta(minutes=ONLINE_TIMEOUT_MINUTES)
    inactive_users = db.query(OnlineUser).filter(
        and_(
            OnlineUser.is_active == True,
            OnlineUser.last_activity < timeout_threshold
        )
    ).all()
    
    count = 0
    for user in inactive_users:
        user.is_active = False
        count += 1
    
    if count > 0:
        db.commit()
    
    return count


@router.post("/login", response_model=ApiResponse)
async def record_login(
    request: Request,
    device_type: str = "pc",
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_required)
):
    """
    记录用户登录
    在用户登录成功后调用此接口
    """
    user_id = current_user.get("user_id")
    user_name = current_user.get("name")
    
    user_info = db.query(Personnel).filter(Personnel.id == user_id).first()
    
    existing = db.query(OnlineUser).filter(
        and_(
            OnlineUser.user_id == user_id,
            OnlineUser.is_active == True
        )
    ).first()
    
    now = datetime.utcnow()
    client_ip = get_client_ip(request)
    
    if existing:
        existing.last_activity = now
        existing.login_time = now
        existing.ip_address = client_ip
        existing.device_type = device_type
        existing.department = user_info.department if user_info else None
        existing.role = user_info.role if user_info else None
    else:
        online_user = OnlineUser(
            user_id=user_id,
            user_name=user_name,
            department=user_info.department if user_info else None,
            role=user_info.role if user_info else None,
            login_time=now,
            last_activity=now,
            ip_address=client_ip,
            device_type=device_type,
            is_active=True
        )
        db.add(online_user)
    
    db.commit()
    
    clean_inactive_users(db)
    
    return ApiResponse(
        code=200,
        message="登录记录成功",
        data={"user_name": user_name, "device_type": device_type}
    )


@router.post("/heartbeat", response_model=ApiResponse)
async def heartbeat(
    request: Request,
    heartbeat_req: HeartbeatRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_required)
):
    """
    心跳接口
    前端定时调用此接口更新用户活跃状态
    """
    user_id = current_user.get("user_id")
    
    online_user = db.query(OnlineUser).filter(
        and_(
            OnlineUser.user_id == user_id,
            OnlineUser.is_active == True
        )
    ).first()
    
    now = datetime.utcnow()
    client_ip = get_client_ip(request)
    
    if online_user:
        online_user.last_activity = now
        online_user.ip_address = client_ip
        online_user.device_type = heartbeat_req.device_type
        db.commit()
    else:
        user_name = current_user.get("name")
        user_info = db.query(Personnel).filter(Personnel.id == user_id).first()
        
        new_online_user = OnlineUser(
            user_id=user_id,
            user_name=user_name,
            department=user_info.department if user_info else None,
            role=user_info.role if user_info else None,
            login_time=now,
            last_activity=now,
            ip_address=client_ip,
            device_type=heartbeat_req.device_type,
            is_active=True
        )
        db.add(new_online_user)
        db.commit()
    
    clean_inactive_users(db)
    
    return ApiResponse(
        code=200,
        message="心跳更新成功",
        data={"last_activity": now.strftime("%Y-%m-%d %H:%M:%S")}
    )


@router.post("/logout", response_model=ApiResponse)
async def record_logout(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_required)
):
    """
    记录用户登出
    在用户主动登出时调用
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
        message="登出记录成功",
        data=None
    )


@router.get("/users", response_model=ApiResponse)
async def get_online_users(
    device_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_required)
):
    """
    获取在线用户列表
    可通过device_type参数筛选设备类型(pc/h5)
    """
    clean_inactive_users(db)
    
    query = db.query(OnlineUser).filter(OnlineUser.is_active == True)
    
    if device_type:
        query = query.filter(OnlineUser.device_type == device_type)
    
    online_users = query.order_by(OnlineUser.last_activity.desc()).all()
    
    users_list = [user.to_dict() for user in online_users]
    
    return ApiResponse(
        code=200,
        message="success",
        data=users_list
    )


@router.get("/count", response_model=ApiResponse)
async def get_online_count(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_required)
):
    """
    获取在线用户统计
    返回总数和各设备类型的数量
    """
    clean_inactive_users(db)
    
    total = db.query(OnlineUser).filter(OnlineUser.is_active == True).count()
    pc_count = db.query(OnlineUser).filter(
        and_(
            OnlineUser.is_active == True,
            OnlineUser.device_type == "pc"
        )
    ).count()
    h5_count = db.query(OnlineUser).filter(
        and_(
            OnlineUser.is_active == True,
            OnlineUser.device_type == "h5"
        )
    ).count()
    
    return ApiResponse(
        code=200,
        message="success",
        data={
            "total": total,
            "pc_count": pc_count,
            "h5_count": h5_count
        }
    )


@router.get("/statistics", response_model=ApiResponse)
async def get_online_statistics(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_required)
):
    """
    获取在线用户详细统计
    包含用户列表和统计数据
    """
    clean_inactive_users(db)
    
    online_users = db.query(OnlineUser).filter(
        OnlineUser.is_active == True
    ).order_by(OnlineUser.last_activity.desc()).all()
    
    pc_users = [u.to_dict() for u in online_users if u.device_type == "pc"]
    h5_users = [u.to_dict() for u in online_users if u.device_type == "h5"]
    
    return ApiResponse(
        code=200,
        message="success",
        data={
            "total": len(online_users),
            "pc_count": len(pc_users),
            "h5_count": len(h5_users),
            "pc_users": pc_users,
            "h5_users": h5_users
        }
    )

"""
在线用户API接口
提供在线用户统计和管理功能
"""
import asyncio
import json
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import and_
from pydantic import BaseModel
from typing import Optional, List
from app.database import get_db
from app.schemas.common import ApiResponse
from app.models.online_user import OnlineUser
from app.models.personnel import Personnel
from app.auth import get_current_user_required, get_current_user

router = APIRouter(prefix="/online", tags=["Online Users"])

ONLINE_TIMEOUT_MINUTES = 15
RECORD_RETENTION_DAYS = 30


def clean_old_records(db: Session) -> int:
    """
    删除超过指定天数的旧记录
    返回删除的记录数量
    """
    retention_threshold = datetime.utcnow() - timedelta(days=RECORD_RETENTION_DAYS)
    old_records = db.query(OnlineUser).filter(
        OnlineUser.last_activity < retention_threshold
    ).all()
    
    count = len(old_records)
    for record in old_records:
        db.delete(record)
    
    if count > 0:
        db.commit()
    
    return count


class LoginRequest(BaseModel):
    """登录请求"""
    device_type: str = "pc"
    user_id: Optional[int] = None
    user_name: Optional[str] = None


class HeartbeatRequest(BaseModel):
    """心跳请求"""
    device_type: str = "pc"
    user_id: Optional[int] = None
    user_name: Optional[str] = None


class LogoutRequest(BaseModel):
    """登出请求"""
    user_id: Optional[int] = None
    device_type: Optional[str] = None


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
    同时清理超过30天的旧记录
    返回清理的用户数量
    """
    clean_old_records(db)
    
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
    login_req: LoginRequest = None,
    device_type: str = "pc",
    user_id: int = None,
    user_name: str = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_required)
):
    """
    记录用户登录
    在用户登录成功后调用此接口
    支持通过参数指定用户ID和名称（用于PC端切换用户场景）
    """
    if login_req:
        device_type = login_req.device_type
        user_id = login_req.user_id
        user_name = login_req.user_name
    
    if not user_id:
        user_id = current_user.get("user_id")
        user_name = current_user.get("name")
    
    user_info = db.query(Personnel).filter(Personnel.id == user_id).first()
    if user_info:
        user_name = user_info.name
    
    existing = db.query(OnlineUser).filter(
        and_(
            OnlineUser.user_id == user_id,
            OnlineUser.device_type == device_type,
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
    logout_req: LogoutRequest = None,
    user_id: int = None,
    device_type: str = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    记录用户登出
    在用户主动登出时调用
    支持通过参数指定用户ID和设备类型（用于PC端切换用户场景）
    """
    print(f"[DEBUG] logout_req: {logout_req}, user_id: {user_id}, device_type: {device_type}")
    
    if logout_req:
        if logout_req.user_id:
            user_id = logout_req.user_id
        if logout_req.device_type:
            device_type = logout_req.device_type
    
    print(f"[DEBUG] After parsing - user_id: {user_id}, device_type: {device_type}")
    
    if not user_id:
        if current_user:
            user_id = current_user.get("user_id")
        else:
            return ApiResponse(
                code=400,
                message="缺少用户ID参数",
                data=None
            )
    
    query = db.query(OnlineUser).filter(
        and_(
            OnlineUser.user_id == user_id,
            OnlineUser.is_active == True
        )
    )
    
    if device_type:
        query = query.filter(OnlineUser.device_type == device_type)
    
    online_users = query.all()
    
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


@router.get("/stream")
async def online_users_stream(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    SSE流式接口 - 实时推送在线用户数据
    前端通过EventSource连接此接口获取实时更新
    """
    
    async def event_generator():
        last_count = -1
        last_users_hash = ""
        
        while True:
            if await request.is_disconnected():
                break
            
            try:
                clean_inactive_users(db)
                
                online_users = db.query(OnlineUser).filter(
                    OnlineUser.is_active == True
                ).order_by(OnlineUser.last_activity.desc()).all()
                
                pc_users = [u.to_dict() for u in online_users if u.device_type == "pc"]
                h5_users = [u.to_dict() for u in online_users if u.device_type == "h5"]
                
                current_count = len(online_users)
                current_hash = f"{current_count}-{len(pc_users)}-{len(h5_users)}"
                
                for u in online_users[:5]:
                    current_hash += f"-{u.user_id}-{u.last_activity.timestamp() if u.last_activity else 0}"
                
                if current_count != last_count or current_hash != last_users_hash:
                    data = {
                        "total": current_count,
                        "pc_count": len(pc_users),
                        "h5_count": len(h5_users),
                        "pc_users": pc_users,
                        "h5_users": h5_users
                    }
                    
                    yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
                    
                    last_count = current_count
                    last_users_hash = current_hash
                else:
                    yield f": heartbeat\n\n"
                
            except Exception as e:
                print(f"SSE Error: {e}")
                yield f": error\n\n"
            
            await asyncio.sleep(2)
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

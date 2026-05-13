import uuid
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import UserInfo, get_current_user_required, get_manager_user
from app.schemas.common import ApiResponse
from app.schemas.online_user import HeartbeatRequest
from app.services.online_user import OnlineUserService
from app.utils.logging_config import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/online", tags=["Online User"])


def get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


@router.post("/login", response_model=ApiResponse)
def record_login(
    request: Request,
    login_req: HeartbeatRequest,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_required)
):
    service = OnlineUserService(db)
    ip_address = get_client_ip(request)
    device_type = login_req.device_type if login_req.device_type in ["pc", "h5"] else "h5"
    result = service.record_login(user_info.id, user_info.name, ip_address, device_type)
    return ApiResponse(code=result["code"], message=result["message"], data=None)


@router.post("/logout", response_model=ApiResponse)
def record_logout(
    request: Request,
    logout_req: HeartbeatRequest,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_required)
):
    service = OnlineUserService(db)
    result = service.record_logout(user_info.id)
    return ApiResponse(code=result["code"], message=result["message"], data=None)


@router.post("/heartbeat", response_model=ApiResponse)
async def heartbeat(
    request: Request,
    heartbeat_req: HeartbeatRequest,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_required)
):
    service = OnlineUserService(db)
    ip_address = get_client_ip(request)
    device_type = heartbeat_req.device_type if heartbeat_req.device_type in ["pc", "h5"] else "h5"
    result = service.update_heartbeat(user_info.id, user_info.name, ip_address, device_type)
    return ApiResponse(code=result["code"], message=result["message"], data=None)


@router.get("/count", response_model=ApiResponse)
def get_online_count(
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_required)
):
    service = OnlineUserService(db)
    result = service.get_online_count()
    if result["code"] == 200:
        return ApiResponse(code=200, message="获取成功", data=result.get("data", {"count": 0}))
    return ApiResponse(code=result["code"], message=result["message"], data=None)


@router.get("/users", response_model=ApiResponse)
def get_online_users(
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_manager_user)
):
    service = OnlineUserService(db)
    result = service.get_online_users()
    if result["code"] == 200:
        return ApiResponse(code=200, message="获取成功", data=result.get("data", []))
    return ApiResponse(code=result["code"], message=result["message"], data=None)


@router.get("/statistics", response_model=ApiResponse)
def get_online_statistics(
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_manager_user)
):
    service = OnlineUserService(db)
    result = service.get_online_statistics()
    if result["code"] == 200:
        return ApiResponse(code=200, message="获取成功", data=result.get("data", {}))
    return ApiResponse(code=result["code"], message=result["message"], data=None)

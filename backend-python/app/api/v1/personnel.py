
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import UserInfo, get_manager_user
from app.models.online_user import OnlineUser
from app.schemas.common import ApiResponse, PaginatedResponse
from app.schemas.personnel import (
    PersonnelCreate,
    PersonnelUpdate,
)
from app.services.personnel import PersonnelService

router = APIRouter(prefix="/personnel", tags=["Personnel Management"])

ONLINE_TIMEOUT_MINUTES = 5


def _get_online_status_map(db: Session, user_ids: list[int]) -> dict:
    """
    获取用户在线状态映射
    @param db: 数据库会话
    @param user_ids: 用户ID列表
    @return: {user_id: {"is_online": bool, "device_type": str}} 映射
    
    超时机制：如果用户 last_activity 超过 ONLINE_TIMEOUT_MINUTES 分钟没有更新，
    则认为用户已离线，自动更新 is_active 为 False
    """
    timeout_threshold = datetime.utcnow() - timedelta(minutes=ONLINE_TIMEOUT_MINUTES)
    
    online_users = db.query(OnlineUser).filter(
        and_(
            OnlineUser.user_id.in_(user_ids),
            OnlineUser.is_active == True
        )
    ).all()
    
    result = {}
    for ou in online_users:
        if ou.last_activity and ou.last_activity < timeout_threshold:
            ou.is_active = False
            continue
        
        if ou.user_id not in result:
            result[ou.user_id] = {
                "is_online": True,
                "device_type": ou.device_type
            }
        else:
            if ou.device_type == "pc":
                result[ou.user_id]["device_type"] = "pc"
    
    if online_users:
        db.commit()
    
    return result


@router.get("/all/list", response_model=ApiResponse)
def get_all_personnel(
    db: Session = Depends(get_db)
):
    """
    获取所有人员列表（不分页）

    返回系统中所有人员的完整列表，用于下拉选择等场景

    Returns:
        ApiResponse: 包含所有人员列表的响应对象
    """
    service = PersonnelService(db)
    items = service.get_all_unpaginated()
    return ApiResponse.success([item.to_dict() for item in items])


@router.get("", response_model=PaginatedResponse)
def get_personnel_list(
    page: int = Query(0, ge=0, description="Page number, starts from 0"),
    size: int = Query(10, ge=1, le=1000, description="Page size"),
    name: str | None = Query(None, description="Name (fuzzy search)"),
    department: str | None = Query(None, description="Department (fuzzy search)"),
    current_user_role: str | None = Query(None, description="Current user role"),
    current_user_department: str | None = Query(None, description="Current user department"),
    db: Session = Depends(get_db)
):
    """
    分页获取人员列表

    支持按姓名、部门模糊查询，并根据当前用户角色进行权限过滤
    包含用户在线状态和设备类型信息

    Args:
        page: 页码，从0开始
        size: 每页大小，默认10条
        name: 姓名模糊查询条件
        department: 部门模糊查询条件
        current_user_role: 当前用户角色，用于权限控制
        current_user_department: 当前用户部门，用于权限控制

    Returns:
        PaginatedResponse: 分页响应对象，包含人员列表和分页信息
    """
    service = PersonnelService(db)
    items, total = service.get_all(
        page=page, size=size, name=name, department=department,
        current_user_role=current_user_role, current_user_department=current_user_department
    )
    
    user_ids = [item.id for item in items]
    online_status_map = _get_online_status_map(db, user_ids) if user_ids else {}
    
    items_dict = []
    for item in items:
        item_dict = item.to_dict()
        online_info = online_status_map.get(item.id, {"is_online": False, "device_type": None})
        item_dict["is_online"] = online_info["is_online"]
        item_dict["device_type"] = online_info["device_type"]
        items_dict.append(item_dict)
    
    return PaginatedResponse.success(items_dict, total, page, size)


@router.get("/{id}", response_model=ApiResponse)
def get_personnel_by_id(
    id: int,
    db: Session = Depends(get_db)
):
    """
    根据ID获取人员详情

    Args:
        id: 人员ID

    Returns:
        ApiResponse: 包含人员详情的响应对象

    Raises:
        HTTPException: 人员不存在时返回404错误
    """
    service = PersonnelService(db)
    personnel = service.get_by_id(id)
    return ApiResponse.success(personnel.to_dict())


@router.post("", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
def create_personnel(
    dto: PersonnelCreate,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_manager_user)
):
    """
    创建新人员
    需要管理员或部门经理权限

    Args:
        dto: 人员创建数据传输对象

    Returns:
        ApiResponse: 包含创建成功的人员信息的响应对象

    Raises:
        HTTPException: 数据验证失败时返回400错误
    """
    service = PersonnelService(db)
    personnel = service.create(dto)
    return ApiResponse.success(personnel.to_dict(), "Created successfully")


@router.put("/{id}", response_model=ApiResponse)
def update_personnel(
    id: int,
    dto: PersonnelUpdate,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_manager_user)
):
    """
    更新人员信息
    需要管理员或部门经理权限

    Args:
        id: 人员ID
        dto: 人员更新数据传输对象

    Returns:
        ApiResponse: 包含更新后的人员信息的响应对象

    Raises:
        HTTPException: 人员不存在时返回404错误
    """
    service = PersonnelService(db)
    personnel = service.update(id, dto)
    return ApiResponse.success(personnel.to_dict(), "Updated successfully")


@router.delete("/{id}", response_model=ApiResponse)
def delete_personnel(
    id: int,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_manager_user)
):
    """
    删除人员
    需要管理员或部门经理权限

    Args:
        id: 人员ID

    Returns:
        ApiResponse: 删除成功的响应对象

    Raises:
        HTTPException: 人员不存在时返回404错误
    """
    service = PersonnelService(db)
    service.delete(id)
    return ApiResponse.success(None, "Deleted successfully")

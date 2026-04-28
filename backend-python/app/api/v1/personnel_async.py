"""
异步版人员管理 API
演示如何将同步 API 訡块转换为异步模式
"""
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_db
from app.dependencies import UserInfo, get_manager_user
from app.models.online_user import OnlineUser
from app.schemas.common import ApiResponse, PaginatedResponse
from app.schemas.personnel import PersonnelCreate, PersonnelUpdate
from app.services.personnel import PersonnelService

router = APIRouter(prefix="/personnel", tags=["Personnel Management"])

ONLINE_TIMEOUT_MINUTES = 5


async def _get_online_status_map(db: AsyncSession, user_ids: list[int]) -> dict:
    """
    获取用户在线状态映射（异步版本）
    
    Args:
        db: 异步数据库会话
        user_ids: 用户ID列表
    
    Returns:
        {user_id: {"is_online": bool, "device_type": str}} 映射
    """
    timeout_threshold = datetime.utcnow() - timedelta(minutes=ONLINE_TIMEOUT_MINUTES)
    
    result = {}
    
    if not user_ids:
        return result
    
    online_users = await db.execute(
        select(OnlineUser)
        .where(
            and_(
                OnlineUser.user_id.in_(user_ids),
                OnlineUser.is_active == True
            )
        .order_by(OnlineUser.user_id)
    )
    
    online_users_list = online_users.scalars().all()
    
    for ou in online_users_list:
        if ou.last_activity and ou.last_activity < timeout_threshold:
            ou.is_active = False
            await db.commit()
            continue
        
        if ou.user_id not in result:
            result[ou.user_id] = {
                "is_online": True,
                "device_type": ou.device_type
            }
        else:
            if ou.device_type == "pc":
                result[ou.user_id]["device_type"] = "pc"
    
    return result


@router.get("/all/list", response_model=ApiResponse)
async def get_all_personnel(
    db: AsyncSession = Depends(get_async_db)
):
    """
    获取所有人员列表（不分页）- 异步版本
    """
    service = PersonnelService(db)
    items = await service.get_all_unpaginated_async()
    return ApiResponse.success([item.to_dict() for item in items])


@router.get("", response_model=PaginatedResponse)
async def get_personnel_list(
    page: int = Query(0, ge=0, description="Page number, starts from 0"),
    size: int = Query(10, ge=1, le=1000, description="Page size"),
    name: str | None = Query(None, description="Name (fuzzy search)"),
    department: str | None = Query(None, description="Department (fuzzy search)"),
    current_user_role: str | None = Query(None, description="Current user role"),
    current_user_department: str | None = Query(None, description="Current user department"),
    db: AsyncSession = Depends(get_async_db)
):
    """
    分页获取人员列表 - 异步版本
    """
    service = PersonnelService(db)
    items, total = await service.get_all_async(
        page=page,
        size=size,
        name=name,
        department=department,
        current_user_role=current_user_role,
        current_user_department=current_user_department
    )
    
    user_ids = [item.id for item in items]
    online_status_map = await _get_online_status_map(db, user_ids) if user_ids else {}
    
    items_dict = []
    for item in items:
        item_dict = item.to_dict()
        online_info = online_status_map.get(item.id, {"is_online": False, "device_type": None})
        item_dict["is_online"] = online_info["is_online"]
        item_dict["device_type"] = online_info["device_type"]
        items_dict.append(item_dict)
    
    return PaginatedResponse.success(items_dict, total, page, size)


@router.get("/{id}", response_model=ApiResponse)
async def get_personnel_by_id(
    id: int,
    db: AsyncSession = Depends(get_async_db)
):
    """
    根据ID获取人员详情 - 异步版本
    """
    service = PersonnelService(db)
    personnel = await service.get_by_id_async(id)
    return ApiResponse.success(personnel.to_dict())


@router.post("", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
async def create_personnel(
    dto: PersonnelCreate,
    db: AsyncSession = Depends(get_async_db),
    user_info: UserInfo = Depends(get_manager_user)
):
    """
    创建新人员 - 异步版本
    需要管理员或部门经理权限
    """
    service = PersonnelService(db)
    personnel = await service.create_async(dto)
    return ApiResponse.success(personnel.to_dict(), "Created successfully")


@router.put("/{id}", response_model=ApiResponse)
async def update_personnel(
    id: int,
    dto: PersonnelUpdate,
    db: AsyncSession = Depends(get_async_db),
    user_info: UserInfo = Depends(get_manager_user)
):
    """
    更新人员信息 - 异步版本
    需要管理员或部门经理权限
    """
    service = PersonnelService(db)
    personnel = await service.update_async(id, dto)
    return ApiResponse.success(personnel.to_dict(), "Updated successfully")


@router.delete("/{id}", response_model=ApiResponse)
async def delete_personnel(
    id: int,
    db: AsyncSession = Depends(get_async_db),
    user_info: UserInfo = Depends(get_manager_user)
):
    """
    删除人员 - 异步版本
    需要管理员或部门经理权限
    """
    service = PersonnelService(db)
    await service.delete_async(id)
    return ApiResponse.success(None, "Deleted successfully")

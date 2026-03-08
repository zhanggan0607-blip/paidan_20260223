"""
临时维修API
提供临时维修工单的HTTP接口

权限说明：
- 列表查询：运维人员只能看到自己的数据，管理员可以看到所有数据
- 创建工单：所有已认证用户均可创建
- 更新工单：管理员可更新所有工单，运维人员只能更新自己的工单
- 删除工单：需要管理员或部门经理权限
"""
import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import UserInfo, check_data_access, get_current_user_info, get_current_user_required, get_manager_user
from app.schemas.common import ApiResponse
from app.schemas.temporary_repair import (
    TemporaryRepairCreate,
    TemporaryRepairPartialUpdate,
    TemporaryRepairUpdate,
)
from app.services.temporary_repair import TemporaryRepairService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/temporary-repair", tags=["Temporary Repair Management"])


@router.get("/all/list", response_model=ApiResponse)
def get_all_temporary_repairs(
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_info)
):
    """
    获取所有临时维修（不分页）
    普通用户只能看到自己的数据，管理员可以看到所有数据
    """
    service = TemporaryRepairService(db)
    items = service.get_all_unpaginated()

    if not user_info.is_manager and user_info.name:
        items = [item for item in items if item.maintenance_personnel == user_info.name]

    return ApiResponse(
        code=200,
        message="success",
        data=[item.to_dict() for item in items]
    )


@router.get("", response_model=ApiResponse)
def get_temporary_repairs_list(
    page: int = Query(0, ge=0, description="Page number, starts from 0"),
    size: int = Query(10, ge=1, le=1000, description="Page size"),
    project_name: str | None = Query(None, description="Project name (fuzzy search)"),
    repair_id: str | None = Query(None, description="Repair ID (fuzzy search)"),
    status: str | None = Query(None, description="Status"),
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_info)
):
    """
    分页获取临时维修列表
    普通用户只能看到自己的数据，管理员可以看到所有数据
    """
    service = TemporaryRepairService(db)
    maintenance_personnel = user_info.get_maintenance_personnel_filter()

    logger.info(f"[PC端临时维修] user={user_info.name}, is_manager={user_info.is_manager}, filter={maintenance_personnel}")

    items, total = service.get_all(
        page=page, size=size, project_name=project_name, repair_id=repair_id,
        status=status, maintenance_personnel=maintenance_personnel
    )
    items_dict = [item.to_dict() for item in items]
    return ApiResponse(
        code=200,
        message="success",
        data={
            'content': items_dict,
            'totalElements': total,
            'totalPages': (total + size - 1) // size,
            'size': size,
            'number': page,
            'first': page == 0,
            'last': page >= (total + size - 1) // size
        }
    )


@router.get("/{id}", response_model=ApiResponse)
def get_temporary_repair_by_id(
    id: int,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_info)
):
    """
    根据ID获取临时维修详情
    管理员可查看所有工单，运维人员只能查看自己的工单
    """
    service = TemporaryRepairService(db)
    repair = service.get_by_id(id)

    if not check_data_access(user_info, repair.maintenance_personnel):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权查看此工单"
        )

    return ApiResponse(
        code=200,
        message="success",
        data=repair.to_dict()
    )


@router.post("", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
def create_temporary_repair(
    dto: TemporaryRepairCreate,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_required)
):
    """
    创建临时维修
    所有已认证用户均可创建
    """
    service = TemporaryRepairService(db)
    repair = service.create(dto, user_info.id, user_info.name)
    return ApiResponse(
        code=200,
        message="Created successfully",
        data=repair.to_dict()
    )


@router.put("/{id}", response_model=ApiResponse)
def update_temporary_repair(
    id: int,
    dto: TemporaryRepairUpdate,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_info)
):
    """
    更新临时维修
    管理员可更新所有工单，运维人员只能更新自己的工单

    权限说明：
    - 普通员工只能修改工单内容，不能修改状态为"已完成"或"已退回"
    - 状态审批（改为"已完成"或"已退回"）需要管理员或部门经理权限
    """
    service = TemporaryRepairService(db)
    existing = service.get_by_id(id)

    if not check_data_access(user_info, existing.maintenance_personnel):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权修改此工单"
        )

    if dto.status in ['已完成', '已退回'] and not user_info.is_manager:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="工单审批需要管理员或部门经理权限"
        )

    repair = service.update(id, dto, user_info.id, user_info.name)
    return ApiResponse(
        code=200,
        message="Updated successfully",
        data=repair.to_dict()
    )


@router.patch("/{id}", response_model=ApiResponse)
def partial_update_temporary_repair(
    id: int,
    dto: TemporaryRepairPartialUpdate,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_info)
):
    """
    部分更新临时维修
    管理员可更新所有工单，运维人员只能更新自己的工单

    权限说明：
    - 普通员工只能修改工单内容，不能修改状态为"已完成"或"已退回"
    - 状态审批（改为"已完成"或"已退回"）需要管理员或部门经理权限
    """
    service = TemporaryRepairService(db)
    existing = service.get_by_id(id)

    if not check_data_access(user_info, existing.maintenance_personnel):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权修改此工单"
        )

    if dto.status in ['已完成', '已退回'] and not user_info.is_manager:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="工单审批需要管理员或部门经理权限"
        )

    repair = service.partial_update(id, dto, user_info.id, user_info.name)
    return ApiResponse(
        code=200,
        message="Updated successfully",
        data=repair.to_dict()
    )


@router.delete("/{id}", response_model=ApiResponse)
def delete_temporary_repair(
    id: int,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_manager_user)
):
    """
    删除临时维修（软删除）
    需要管理员或部门经理权限
    """
    service = TemporaryRepairService(db)
    service.delete(id, user_info.id, user_info.name)
    return ApiResponse(
        code=200,
        message="Deleted successfully",
        data=None
    )

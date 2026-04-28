"""
定期巡检API
提供定期巡检工单的HTTP接口
"""
import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import UserInfo, check_data_access, get_current_user_info, get_current_user_required, get_manager_user
from app.schemas.common import ApiResponse, PaginatedResponse
from app.schemas.periodic_inspection import (
    PeriodicInspectionApprove,
    PeriodicInspectionCreate,
    PeriodicInspectionPartialUpdate,
    PeriodicInspectionUpdate,
)
from app.services.periodic_inspection import PeriodicInspectionService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/periodic-inspection", tags=["Periodic Inspection Management"])


@router.get("/all/list", response_model=ApiResponse)
def get_all_periodic_inspection(
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_info)
):
    """
    获取所有定期巡检（不分页）
    普通用户只能看到自己的数据，管理员可以看到所有数据
    """
    service = PeriodicInspectionService(db)
    items = service.get_all_unpaginated()

    if not user_info.is_manager and user_info.name:
        items = [item for item in items if item.maintenance_personnel == user_info.name]

    if not items:
        return ApiResponse.success([])

    counts_map = service.get_inspection_counts_batch(items)

    result = []
    for item in items:
        item_dict = item.to_list_dict()
        counts = counts_map.get(item.inspection_id, {'total_count': 0, 'filled_count': 0})
        item_dict['total_count'] = counts['total_count']
        item_dict['filled_count'] = counts['filled_count']
        result.append(item_dict)

    return ApiResponse.success(result)


@router.get("", response_model=PaginatedResponse)
def get_periodic_inspection_list(
    page: int = Query(0, ge=0, description="Page number, starts from 0"),
    size: int = Query(10, ge=1, le=1000, description="Page size"),
    project_name: str | None = Query(None, description="Project name (fuzzy search)"),
    client_name: str | None = Query(None, description="Client name (fuzzy search)"),
    inspection_id: str | None = Query(None, description="Inspection ID (fuzzy search)"),
    status: str | None = Query(None, description="Status"),
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_info)
):
    """
    分页获取定期巡检列表
    普通用户只能看到自己的数据，管理员可以看到所有数据
    """
    service = PeriodicInspectionService(db)
    maintenance_personnel = user_info.get_maintenance_personnel_filter()

    logger.info(f"[PC端定期巡检] user={user_info.name}, is_manager={user_info.is_manager}, filter={maintenance_personnel}")

    items, total = service.get_all(
        page, size, project_name, client_name, inspection_id, status, maintenance_personnel
    )

    if not items:
        return PaginatedResponse.success([], total, page, size)

    counts_map = service.get_inspection_counts_batch(items)

    result = []
    for item in items:
        item_dict = item.to_list_dict()
        counts = counts_map.get(item.inspection_id, {'total_count': 0, 'filled_count': 0})
        item_dict['total_count'] = counts['total_count']
        item_dict['filled_count'] = counts['filled_count']
        result.append(item_dict)

    return PaginatedResponse.success(result, total, page, size)


@router.get("/{id}", response_model=ApiResponse)
def get_periodic_inspection_by_id(
    id: int,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_required)
):
    """
    根据ID获取定期巡检详情
    管理员可查看所有工单，运维人员只能查看自己的工单
    """
    service = PeriodicInspectionService(db)
    inspection = service.get_by_id(id)

    logger.info(f"[定期巡检详情] id={id}, user={user_info.name}, role={user_info.role}, is_manager={user_info.is_manager}, maintenance_personnel={inspection.maintenance_personnel}")

    if not check_data_access(user_info, inspection.maintenance_personnel):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权查看此工单"
        )

    return ApiResponse.success(inspection.to_dict())


@router.post("", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
def create_periodic_inspection(
    dto: PeriodicInspectionCreate,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_manager_user)
):
    """
    创建定期巡检
    需要管理员或部门经理权限
    """
    service = PeriodicInspectionService(db)
    inspection = service.create(dto, user_info.id, user_info.name)
    return ApiResponse.success(inspection.to_dict(), "Created successfully")


@router.put("/{id}", response_model=ApiResponse)
def update_periodic_inspection(
    id: int,
    dto: PeriodicInspectionUpdate,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_manager_user)
):
    """
    更新定期巡检
    需要管理员或部门经理权限
    """
    service = PeriodicInspectionService(db)
    inspection = service.update(id, dto, user_info.id, user_info.name)
    return ApiResponse.success(inspection.to_dict(), "Updated successfully")


@router.patch("/{id}", response_model=ApiResponse)
def partial_update_periodic_inspection(
    id: int,
    dto: PeriodicInspectionPartialUpdate,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_required)
):
    """
    部分更新定期巡检
    管理员可更新所有工单，运维人员只能更新自己的工单

    填写内容不需要管理员权限，但状态审批需要管理员权限
    """
    service = PeriodicInspectionService(db)
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

    if dto.status == '已退回':
        if not dto.reject_reason or len(dto.reject_reason.strip()) < 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="请输入工单退回原因，至少10个字符"
            )
        if len(dto.reject_reason.strip()) > 500:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="退回原因不能超过500个字符"
            )

    inspection = service.partial_update(id, dto, user_info.id, user_info.name)
    return ApiResponse.success(inspection.to_dict(), "Updated successfully")


@router.post("/{id}/submit", response_model=ApiResponse)
def submit_periodic_inspection(
    id: int,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_required)
):
    """
    提交定期巡检工单
    管理员可提交所有工单，运维人员只能提交自己的工单
    """
    service = PeriodicInspectionService(db)
    existing = service.get_by_id(id)

    if not check_data_access(user_info, existing.maintenance_personnel):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权提交此工单"
        )

    inspection = service.partial_update(id, PeriodicInspectionPartialUpdate(status='待确认'), user_info.id, user_info.name)
    return ApiResponse.success(inspection.to_dict(), "提交成功")


@router.post("/{id}/recall", response_model=ApiResponse)
def recall_periodic_inspection(
    id: int,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_required)
):
    """
    撤回定期巡检工单
    仅待确认状态可撤回，撤回后状态变为执行中
    管理员可撤回所有工单，运维人员只能撤回自己的工单
    """
    service = PeriodicInspectionService(db)
    existing = service.get_by_id(id)

    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="工单不存在"
        )

    if existing.status != '待确认':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只有待确认状态的工单才能撤回"
        )

    if not check_data_access(user_info, existing.maintenance_personnel):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权撤回此工单"
        )

    inspection = service.partial_update(id, PeriodicInspectionPartialUpdate(status='执行中'), user_info.id, user_info.name)
    return ApiResponse.success(inspection.to_dict(), "撤回成功")


@router.post("/{id}/approve", response_model=ApiResponse)
def approve_periodic_inspection(
    id: int,
    dto: PeriodicInspectionApprove,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_manager_user)
):
    """
    审批定期巡检工单
    需要管理员或部门经理权限
    """
    service = PeriodicInspectionService(db)
    
    if dto.approved:
        inspection = service.partial_update(id, PeriodicInspectionPartialUpdate(status='已完成'), user_info.id, user_info.name)
        message = "审批通过"
    else:
        if not dto.reject_reason or len(dto.reject_reason.strip()) < 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="请输入工单退回原因，至少10个字符"
            )
        inspection = service.partial_update(
            id, 
            PeriodicInspectionPartialUpdate(status='已退回', reject_reason=dto.reject_reason), 
            user_info.id, 
            user_info.name
        )
        message = "已退回"

    return ApiResponse.success(inspection.to_dict(), message)


@router.delete("/{id}", response_model=ApiResponse)
def delete_periodic_inspection(
    id: int,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_manager_user)
):
    """
    删除定期巡检（软删除）
    需要管理员或部门经理权限
    """
    service = PeriodicInspectionService(db)
    service.delete(id, user_info.id, user_info.name)
    return ApiResponse.success(None, "Deleted successfully")

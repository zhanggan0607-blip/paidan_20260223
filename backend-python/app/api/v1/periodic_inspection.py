"""
定期巡检API
提供定期巡检工单的HTTP接口
"""
from typing import Optional
import logging
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.periodic_inspection import PeriodicInspectionService
from app.schemas.periodic_inspection import (
    PeriodicInspectionCreate,
    PeriodicInspectionUpdate,
    PeriodicInspectionPartialUpdate,
    ApiResponse
)
from app.dependencies import get_current_user_info, UserInfo
from app.schemas.common import PaginatedResponse

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
        item_dict = item.to_dict()
        counts = counts_map.get(item.inspection_id, {'total_count': 0, 'filled_count': 0})
        item_dict['total_count'] = counts['total_count']
        item_dict['filled_count'] = counts['filled_count']
        result.append(item_dict)
    
    return ApiResponse.success(result)


@router.get("", response_model=PaginatedResponse)
def get_periodic_inspection_list(
    page: int = Query(0, ge=0, description="Page number, starts from 0"),
    size: int = Query(10, ge=1, le=1000, description="Page size"),
    project_name: Optional[str] = Query(None, description="Project name (fuzzy search)"),
    client_name: Optional[str] = Query(None, description="Client name (fuzzy search)"),
    inspection_id: Optional[str] = Query(None, description="Inspection ID (fuzzy search)"),
    status: Optional[str] = Query(None, description="Status"),
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
        item_dict = item.to_dict()
        counts = counts_map.get(item.inspection_id, {'total_count': 0, 'filled_count': 0})
        item_dict['total_count'] = counts['total_count']
        item_dict['filled_count'] = counts['filled_count']
        result.append(item_dict)
    
    return PaginatedResponse.success(result, total, page, size)


@router.get("/{id}", response_model=ApiResponse)
def get_periodic_inspection_by_id(
    id: int,
    db: Session = Depends(get_db)
):
    """
    根据ID获取定期巡检详情
    """
    service = PeriodicInspectionService(db)
    inspection = service.get_by_id(id)
    return ApiResponse.success(inspection.to_dict())


@router.post("", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
def create_periodic_inspection(
    dto: PeriodicInspectionCreate,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_info)
):
    """
    创建定期巡检
    """
    service = PeriodicInspectionService(db)
    inspection = service.create(dto, user_info.id, user_info.name)
    return ApiResponse.success(inspection.to_dict(), "Created successfully")


@router.put("/{id}", response_model=ApiResponse)
def update_periodic_inspection(
    id: int,
    dto: PeriodicInspectionUpdate,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_info)
):
    """
    更新定期巡检
    """
    service = PeriodicInspectionService(db)
    inspection = service.update(id, dto, user_info.id, user_info.name)
    return ApiResponse.success(inspection.to_dict(), "Updated successfully")


@router.patch("/{id}", response_model=ApiResponse)
def partial_update_periodic_inspection(
    id: int,
    dto: PeriodicInspectionPartialUpdate,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_info)
):
    """
    部分更新定期巡检
    """
    service = PeriodicInspectionService(db)
    inspection = service.partial_update(id, dto, user_info.id, user_info.name)
    return ApiResponse.success(inspection.to_dict(), "Updated successfully")


@router.delete("/{id}", response_model=ApiResponse)
def delete_periodic_inspection(
    id: int,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_info)
):
    """
    删除定期巡检（软删除）
    """
    service = PeriodicInspectionService(db)
    service.delete(id, user_info.id, user_info.name)
    return ApiResponse.success(None, "Deleted successfully")

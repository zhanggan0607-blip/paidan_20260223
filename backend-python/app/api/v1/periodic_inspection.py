from typing import Optional
import logging
from fastapi import APIRouter, Depends, Query, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.periodic_inspection import PeriodicInspectionService
from app.services.personnel import PersonnelService
from app.schemas.periodic_inspection import (
    PeriodicInspectionCreate,
    PeriodicInspectionUpdate,
    PeriodicInspectionPartialUpdate,
    PeriodicInspectionResponse,
    PaginatedResponse,
    ApiResponse
)
from app.auth import get_current_user, get_current_user_from_headers

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/periodic-inspection", tags=["Periodic Inspection Management"])


def validate_maintenance_personnel(db: Session, personnel_name: str) -> None:
    """校验运维人员必须在personnel表中存在"""
    if personnel_name:
        personnel_service = PersonnelService(db)
        if not personnel_service.validate_personnel_exists(personnel_name):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"运维人员'{personnel_name}'不存在于人员列表中，请先添加该人员"
            )


@router.get("/all/list", response_model=ApiResponse)
def get_all_periodic_inspection(
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user)
):
    service = PeriodicInspectionService(db)
    user_info = current_user or get_current_user_from_headers(request)
    user_name = None
    is_manager = False
    if user_info:
        user_name = user_info.get('sub') or user_info.get('name')
        role = user_info.get('role', '')
        is_manager = role in ['管理员', '部门经理', '主管']
    
    items = service.get_all_unpaginated()
    if not is_manager and user_name:
        items = [item for item in items if item.maintenance_personnel == user_name]
    
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
    request: Request,
    page: int = Query(0, ge=0, description="Page number, starts from 0"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    project_name: Optional[str] = Query(None, description="Project name (fuzzy search)"),
    client_name: Optional[str] = Query(None, description="Client name (fuzzy search)"),
    inspection_id: Optional[str] = Query(None, description="Inspection ID (fuzzy search)"),
    status: Optional[str] = Query(None, description="Status"),
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user)
):
    service = PeriodicInspectionService(db)
    
    user_info = current_user or get_current_user_from_headers(request)
    user_name = None
    is_manager = False
    if user_info:
        user_name = user_info.get('sub') or user_info.get('name')
        role = user_info.get('role', '')
        is_manager = role in ['管理员', '部门经理', '主管']
    
    maintenance_personnel = None if is_manager else user_name
    
    logger.info(f"[PC端定期巡检] user_info={user_info}, user_name={user_name}, is_manager={is_manager}, maintenance_personnel={maintenance_personnel}")
    
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
    service = PeriodicInspectionService(db)
    inspection = service.get_by_id(id)
    return ApiResponse.success(inspection.to_dict())


@router.post("", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
def create_periodic_inspection(
    dto: PeriodicInspectionCreate,
    db: Session = Depends(get_db)
):
    if dto.maintenance_personnel:
        validate_maintenance_personnel(db, dto.maintenance_personnel)
    service = PeriodicInspectionService(db)
    inspection = service.create(dto)
    return ApiResponse.success(inspection.to_dict(), "Created successfully")


@router.put("/{id}", response_model=ApiResponse)
def update_periodic_inspection(
    id: int,
    dto: PeriodicInspectionUpdate,
    db: Session = Depends(get_db)
):
    if dto.maintenance_personnel:
        validate_maintenance_personnel(db, dto.maintenance_personnel)
    service = PeriodicInspectionService(db)
    inspection = service.update(id, dto)
    return ApiResponse.success(inspection.to_dict(), "Updated successfully")


@router.patch("/{id}", response_model=ApiResponse)
def partial_update_periodic_inspection(
    id: int,
    dto: PeriodicInspectionPartialUpdate,
    db: Session = Depends(get_db)
):
    service = PeriodicInspectionService(db)
    inspection = service.partial_update(id, dto)
    return ApiResponse.success(inspection.to_dict(), "Updated successfully")


@router.delete("/{id}", response_model=ApiResponse)
def delete_periodic_inspection(
    id: int,
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user)
):
    from app.models.work_order_operation_log import WorkOrderOperationLog
    service = PeriodicInspectionService(db)
    inspection = service.get_by_id(id)
    inspection_id = inspection.inspection_id
    
    user_id = current_user.get('id') if current_user else None
    operator_name = current_user.get('name', '系统') if current_user else '系统'
    
    log = WorkOrderOperationLog(
        work_order_type='periodic_inspection',
        work_order_id=id,
        work_order_no=inspection_id,
        operator_name=operator_name,
        operator_id=user_id,
        operation_type='delete',
        operation_type_code='delete',
        operation_type_name='删除',
        operation_remark=f'删除定期巡检单 {inspection_id}'
    )
    db.add(log)
    
    service.delete(id, user_id)
    return ApiResponse.success(None, "Deleted successfully")

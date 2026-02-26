from typing import Optional
import logging
from fastapi import APIRouter, Depends, Query, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.temporary_repair import TemporaryRepairService
from app.services.personnel import PersonnelService
from app.schemas.common import ApiResponse, PaginatedResponse
from app.schemas.temporary_repair import TemporaryRepairCreate, TemporaryRepairUpdate, TemporaryRepairPartialUpdate
from app.auth import get_current_user, get_current_user_from_headers

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/temporary-repair", tags=["Temporary Repair Management"])


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
def get_all_temporary_repairs(
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user)
):
    service = TemporaryRepairService(db)
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
    
    return ApiResponse(
        code=200,
        message="success",
        data=[item.to_dict() for item in items]
    )


@router.get("", response_model=ApiResponse)
def get_temporary_repairs_list(
    request: Request,
    page: int = Query(0, ge=0, description="Page number, starts from 0"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    project_name: Optional[str] = Query(None, description="Project name (fuzzy search)"),
    repair_id: Optional[str] = Query(None, description="Repair ID (fuzzy search)"),
    status: Optional[str] = Query(None, description="Status"),
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user)
):
    service = TemporaryRepairService(db)
    user_info = current_user or get_current_user_from_headers(request)
    user_name = None
    is_manager = False
    if user_info:
        user_name = user_info.get('sub') or user_info.get('name')
        role = user_info.get('role', '')
        is_manager = role in ['管理员', '部门经理', '主管']
    
    maintenance_personnel = None if is_manager else user_name
    
    logger.info(f"[PC端临时维修] user_info={user_info}, user_name={user_name}, is_manager={is_manager}, maintenance_personnel={maintenance_personnel}")
    
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
    db: Session = Depends(get_db)
):
    service = TemporaryRepairService(db)
    repair = service.get_by_id(id)
    return ApiResponse(
        code=200,
        message="success",
        data=repair.to_dict()
    )


@router.post("", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
def create_temporary_repair(
    dto: TemporaryRepairCreate,
    db: Session = Depends(get_db)
):
    if dto.maintenance_personnel:
        validate_maintenance_personnel(db, dto.maintenance_personnel)
    service = TemporaryRepairService(db)
    repair = service.create(dto)
    return ApiResponse(
        code=200,
        message="Created successfully",
        data=repair.to_dict()
    )


@router.put("/{id}", response_model=ApiResponse)
def update_temporary_repair(
    id: int,
    dto: TemporaryRepairUpdate,
    db: Session = Depends(get_db)
):
    if dto.maintenance_personnel:
        validate_maintenance_personnel(db, dto.maintenance_personnel)
    service = TemporaryRepairService(db)
    repair = service.update(id, dto)
    return ApiResponse(
        code=200,
        message="Updated successfully",
        data=repair.to_dict()
    )


@router.patch("/{id}", response_model=ApiResponse)
def partial_update_temporary_repair(
    id: int,
    dto: TemporaryRepairPartialUpdate,
    db: Session = Depends(get_db)
):
    if dto.maintenance_personnel:
        validate_maintenance_personnel(db, dto.maintenance_personnel)
    service = TemporaryRepairService(db)
    repair = service.partial_update(id, dto)
    return ApiResponse(
        code=200,
        message="Updated successfully",
        data=repair.to_dict()
    )


@router.delete("/{id}", response_model=ApiResponse)
def delete_temporary_repair(
    id: int,
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user)
):
    from app.models.work_order_operation_log import WorkOrderOperationLog
    service = TemporaryRepairService(db)
    repair = service.get_by_id(id)
    repair_id = repair.repair_id
    
    user_id = current_user.get('id') if current_user else None
    operator_name = current_user.get('name', '系统') if current_user else '系统'
    
    log = WorkOrderOperationLog(
        work_order_type='temporary_repair',
        work_order_id=id,
        work_order_no=repair_id,
        operator_name=operator_name,
        operator_id=user_id,
        operation_type='delete',
        operation_type_code='delete',
        operation_type_name='删除',
        operation_remark=f'删除临时维修单 {repair_id}'
    )
    db.add(log)
    
    service.delete(id, user_id)
    return ApiResponse(
        code=200,
        message="Deleted successfully",
        data=None
    )

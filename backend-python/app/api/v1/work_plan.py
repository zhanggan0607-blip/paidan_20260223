from typing import Optional
from fastapi import APIRouter, Depends, Query, status, Request, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.work_plan import WorkPlanService, WorkPlanCreate, WorkPlanUpdate
from app.services.personnel import PersonnelService
from app.schemas.common import ApiResponse, PaginatedResponse
from app.auth import get_current_user, get_current_user_from_headers


router = APIRouter(prefix="/work-plan", tags=["Work Plan Management"])


def validate_maintenance_personnel(db: Session, personnel_name: str) -> None:
    """校验运维人员必须在personnel表中存在"""
    if personnel_name:
        personnel_service = PersonnelService(db)
        if not personnel_service.validate_personnel_exists(personnel_name):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"运维人员'{personnel_name}'不存在于人员列表中，请先添加该人员"
            )


@router.get("/statistics", response_model=ApiResponse)
def get_statistics(
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user)
):
    service = WorkPlanService(db)
    user_info = current_user or get_current_user_from_headers(request)
    user_name = None
    is_manager = True
    if user_info:
        user_name = user_info.get('sub') or user_info.get('name')
        role = user_info.get('role', '')
        is_manager = role in ['管理员', '部门经理', '主管']
    stats = service.get_statistics(user_name=user_name, is_manager=is_manager)
    return ApiResponse(
        code=200,
        message="success",
        data=stats
    )


@router.get("/all/list", response_model=ApiResponse)
def get_all_work_plans(
    request: Request,
    plan_type: Optional[str] = Query(None, description="工单类型：定期巡检/临时维修/零星用工"),
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user)
):
    service = WorkPlanService(db)
    user_info = current_user or get_current_user_from_headers(request)
    user_name = None
    is_manager = False
    if user_info:
        user_name = user_info.get('sub') or user_info.get('name')
        role = user_info.get('role', '')
        is_manager = role in ['管理员', '部门经理', '主管']
    
    items = service.get_all_unpaginated(plan_type)
    
    if not is_manager and user_name:
        items = [item for item in items if item.maintenance_personnel == user_name]
    
    return ApiResponse(
        code=200,
        message="success",
        data=[item.to_dict() for item in items]
    )


@router.get("", response_model=ApiResponse)
def get_work_plans_list(
    request: Request,
    page: int = Query(0, ge=0, description="Page number, starts from 0"),
    size: int = Query(10, ge=1, le=2000, description="Page size"),
    plan_type: Optional[str] = Query(None, description="工单类型：定期巡检/临时维修/零星用工"),
    project_name: Optional[str] = Query(None, description="Project name (fuzzy search)"),
    client_name: Optional[str] = Query(None, description="Client name (fuzzy search)"),
    status: Optional[str] = Query(None, description="Status"),
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user)
):
    service = WorkPlanService(db)
    user_info = current_user or get_current_user_from_headers(request)
    user_name = None
    is_manager = False
    if user_info:
        user_name = user_info.get('sub') or user_info.get('name')
        role = user_info.get('role', '')
        is_manager = role in ['管理员', '部门经理', '主管']
    
    maintenance_personnel = None if is_manager else user_name
    
    items, total = service.get_all(
        page=page, size=size, plan_type=plan_type, project_name=project_name, 
        client_name=client_name, status=status, maintenance_personnel=maintenance_personnel
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
def get_work_plan_by_id(
    id: int,
    db: Session = Depends(get_db)
):
    service = WorkPlanService(db)
    work_plan = service.get_by_id(id)
    return ApiResponse(
        code=200,
        message="success",
        data=work_plan.to_dict()
    )


@router.post("", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
def create_work_plan(
    dto: dict,
    db: Session = Depends(get_db)
):
    if 'maintenance_personnel' in dto and dto['maintenance_personnel']:
        validate_maintenance_personnel(db, dto['maintenance_personnel'])
    service = WorkPlanService(db)
    work_plan = service.create(WorkPlanCreate(**dto))
    return ApiResponse(
        code=200,
        message="Created successfully",
        data=work_plan.to_dict()
    )


@router.put("/{id}", response_model=ApiResponse)
def update_work_plan(
    id: int,
    dto: dict,
    db: Session = Depends(get_db)
):
    if 'maintenance_personnel' in dto and dto['maintenance_personnel']:
        validate_maintenance_personnel(db, dto['maintenance_personnel'])
    service = WorkPlanService(db)
    work_plan = service.update(id, WorkPlanUpdate(**dto))
    return ApiResponse(
        code=200,
        message="Updated successfully",
        data=work_plan.to_dict()
    )


@router.delete("/{id}", response_model=ApiResponse)
def delete_work_plan(
    id: int,
    db: Session = Depends(get_db)
):
    service = WorkPlanService(db)
    service.delete(id)
    return ApiResponse(
        code=200,
        message="Deleted successfully",
        data=None
    )

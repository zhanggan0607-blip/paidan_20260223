from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.spot_work import SpotWorkService
from app.services.personnel import PersonnelService
from app.schemas.common import ApiResponse, PaginatedResponse
from app.auth import get_current_user, get_current_user_from_headers


router = APIRouter(prefix="/spot-work", tags=["Spot Work Management"])


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
def get_all_spot_works(
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user)
):
    service = SpotWorkService(db)
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
def get_spot_works_list(
    request: Request,
    page: int = Query(0, ge=0, description="Page number, starts from 0"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    project_name: Optional[str] = Query(None, description="Project name (fuzzy search)"),
    client_name: Optional[str] = Query(None, description="Client name (fuzzy search)"),
    status: Optional[str] = Query(None, description="Status"),
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user)
):
    service = SpotWorkService(db)
    user_info = current_user or get_current_user_from_headers(request)
    user_name = None
    is_manager = False
    if user_info:
        user_name = user_info.get('sub') or user_info.get('name')
        role = user_info.get('role', '')
        is_manager = role in ['管理员', '部门经理', '主管']
    
    maintenance_personnel = None if is_manager else user_name
    
    items, total = service.get_all(
        page=page, size=size, project_name=project_name, client_name=client_name, 
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
def get_spot_work_by_id(
    id: int,
    db: Session = Depends(get_db)
):
    service = SpotWorkService(db)
    work = service.get_by_id(id)
    return ApiResponse(
        code=200,
        message="success",
        data=work.to_dict()
    )


@router.post("", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
def create_spot_work(
    dto: dict,
    db: Session = Depends(get_db)
):
    from app.services.spot_work import SpotWorkCreate
    if 'maintenance_personnel' in dto and dto['maintenance_personnel']:
        validate_maintenance_personnel(db, dto['maintenance_personnel'])
    service = SpotWorkService(db)
    work = service.create(SpotWorkCreate(**dto))
    return ApiResponse(
        code=200,
        message="Created successfully",
        data=work.to_dict()
    )


@router.put("/{id}", response_model=ApiResponse)
def update_spot_work(
    id: int,
    dto: dict,
    db: Session = Depends(get_db)
):
    from app.services.spot_work import SpotWorkUpdate
    if 'maintenance_personnel' in dto and dto['maintenance_personnel']:
        validate_maintenance_personnel(db, dto['maintenance_personnel'])
    service = SpotWorkService(db)
    work = service.update(id, SpotWorkUpdate(**dto))
    return ApiResponse(
        code=200,
        message="Updated successfully",
        data=work.to_dict()
    )


@router.delete("/{id}", response_model=ApiResponse)
def delete_spot_work(
    id: int,
    db: Session = Depends(get_db)
):
    service = SpotWorkService(db)
    service.delete(id)
    return ApiResponse(
        code=200,
        message="Deleted successfully",
        data=None
    )

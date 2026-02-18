from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.spot_work import SpotWorkService
from app.services.personnel import PersonnelService
from app.schemas.common import ApiResponse, PaginatedResponse
from app.auth import get_current_user, get_current_user_from_headers
from pydantic import BaseModel


router = APIRouter(prefix="/spot-work", tags=["Spot Work Management"])


class WorkerInfo(BaseModel):
    name: str
    idCardNumber: str
    idCardFront: str
    idCardBack: str


class QuickFillRequest(BaseModel):
    project_id: str
    project_name: str
    plan_start_date: str
    plan_end_date: str
    work_content: Optional[str] = None
    remark: Optional[str] = None


class WorkersRequest(BaseModel):
    project_id: str
    project_name: str
    start_date: str
    end_date: str
    workers: List[WorkerInfo]


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
    work_id: Optional[str] = Query(None, description="Work ID (fuzzy search)"),
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
        page=page, size=size, project_name=project_name, work_id=work_id, 
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


@router.post("/quick-fill", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
def quick_fill_spot_work(
    dto: QuickFillRequest,
    db: Session = Depends(get_db)
):
    """
    快速填报零星用工
    """
    from app.services.spot_work import SpotWorkCreate
    from datetime import datetime
    
    service = SpotWorkService(db)
    
    today = datetime.now().strftime("%Y%m%d")
    work_id = f"YG-{dto.project_id}-{today}"
    
    create_dto = SpotWorkCreate(
        work_id=work_id,
        project_id=dto.project_id,
        project_name=dto.project_name,
        plan_start_date=dto.plan_start_date,
        plan_end_date=dto.plan_end_date,
        client_name='',
        status='未进行',
        remarks=dto.remark
    )
    
    work = service.create(create_dto)
    return ApiResponse(
        code=200,
        message="提交成功",
        data=work.to_dict()
    )


@router.get("/workers", response_model=ApiResponse)
def get_workers(
    project_id: str = Query(..., description="项目编号"),
    start_date: str = Query(..., description="开始日期"),
    end_date: str = Query(..., description="结束日期"),
    db: Session = Depends(get_db)
):
    """
    获取施工人员列表
    """
    return ApiResponse(
        code=200,
        message="success",
        data=[]
    )


@router.post("/workers", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
def save_workers(
    dto: WorkersRequest,
    db: Session = Depends(get_db)
):
    """
    保存施工人员信息
    """
    return ApiResponse(
        code=200,
        message="保存成功",
        data={"count": len(dto.workers)}
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


@router.patch("/{id}", response_model=ApiResponse)
def partial_update_spot_work(
    id: int,
    dto: dict,
    db: Session = Depends(get_db)
):
    from app.schemas.spot_work import SpotWorkPartialUpdate
    if 'maintenance_personnel' in dto and dto['maintenance_personnel']:
        validate_maintenance_personnel(db, dto['maintenance_personnel'])
    service = SpotWorkService(db)
    work = service.partial_update(id, SpotWorkPartialUpdate(**dto))
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

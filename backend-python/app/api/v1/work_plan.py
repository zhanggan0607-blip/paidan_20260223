from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.work_plan import WorkPlanService, WorkPlanCreate, WorkPlanUpdate
from app.schemas.common import ApiResponse, PaginatedResponse
from app.auth import get_current_user


router = APIRouter(prefix="/work-plan", tags=["Work Plan Management"])


@router.get("/statistics", response_model=ApiResponse)
def get_statistics(
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user)
):
    service = WorkPlanService(db)
    user_name = None
    is_manager = True
    if current_user:
        user_name = current_user.get('sub') or current_user.get('name')
        role = current_user.get('role', '')
        is_manager = role in ['管理员', '部门经理', '主管']
    stats = service.get_statistics(user_name=user_name, is_manager=is_manager)
    return ApiResponse(
        code=200,
        message="success",
        data=stats
    )


@router.get("/all/list", response_model=ApiResponse)
def get_all_work_plans(
    plan_type: Optional[str] = Query(None, description="计划类型：定期巡检/临时维修/零星用工"),
    db: Session = Depends(get_db)
):
    service = WorkPlanService(db)
    items = service.get_all_unpaginated(plan_type)
    return ApiResponse(
        code=200,
        message="success",
        data=[item.to_dict() for item in items]
    )


@router.get("", response_model=ApiResponse)
def get_work_plans_list(
    page: int = Query(0, ge=0, description="Page number, starts from 0"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    plan_type: Optional[str] = Query(None, description="计划类型：定期巡检/临时维修/零星用工"),
    project_name: Optional[str] = Query(None, description="Project name (fuzzy search)"),
    client_name: Optional[str] = Query(None, description="Client name (fuzzy search)"),
    status: Optional[str] = Query(None, description="Status"),
    db: Session = Depends(get_db)
):
    service = WorkPlanService(db)
    items, total = service.get_all(
        page=page, size=size, plan_type=plan_type, project_name=project_name, 
        client_name=client_name, status=status
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

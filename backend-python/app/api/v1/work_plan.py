"""
工作计划API
提供工作计划的HTTP接口
"""
import logging

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import UserInfo, get_current_user_info
from app.schemas.common import ApiResponse
from app.services.work_plan import WorkPlanCreate, WorkPlanService, WorkPlanUpdate

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/work-plan", tags=["Work Plan Management"])


@router.get("/statistics", response_model=ApiResponse)
def get_statistics(
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_info)
):
    """
    获取工作计划统计数据
    """
    service = WorkPlanService(db)
    stats = service.get_statistics(user_name=user_info.name, is_manager=user_info.is_manager)
    return ApiResponse(
        code=200,
        message="success",
        data=stats
    )


@router.get("/all/list", response_model=ApiResponse)
def get_all_work_plans(
    plan_type: str | None = Query(None, description="工单类型：定期巡检/临时维修/零星用工"),
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_info)
):
    """
    获取所有工作计划（不分页）
    普通用户只能看到自己的数据，管理员可以看到所有数据
    """
    service = WorkPlanService(db)
    items = service.get_all_unpaginated(plan_type)

    if not user_info.is_manager and user_info.name:
        items = [item for item in items if item.maintenance_personnel == user_info.name]

    return ApiResponse(
        code=200,
        message="success",
        data=[item.to_dict() for item in items]
    )


@router.get("", response_model=ApiResponse)
def get_work_plans_list(
    page: int = Query(0, ge=0, description="Page number, starts from 0"),
    size: int = Query(10, ge=1, le=1000, description="Page size"),
    plan_type: str | None = Query(None, description="工单类型：定期巡检/临时维修/零星用工"),
    project_name: str | None = Query(None, description="Project name (fuzzy search)"),
    client_name: str | None = Query(None, description="Client name (fuzzy search)"),
    status: str | None = Query(None, description="Status"),
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_info)
):
    """
    分页获取工作计划列表
    普通用户只能看到自己的数据，管理员可以看到所有数据
    """
    service = WorkPlanService(db)
    maintenance_personnel = user_info.get_maintenance_personnel_filter()

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
    """
    根据ID获取工作计划详情
    """
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
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_info)
):
    """
    创建工作计划
    """
    service = WorkPlanService(db)
    work_plan = service.create(WorkPlanCreate(**dto), user_info.id, user_info.name)
    return ApiResponse(
        code=200,
        message="Created successfully",
        data=work_plan.to_dict()
    )


@router.put("/{id}", response_model=ApiResponse)
def update_work_plan(
    id: int,
    dto: dict,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_info)
):
    """
    更新工作计划
    """
    service = WorkPlanService(db)
    work_plan = service.update(id, WorkPlanUpdate(**dto), user_info.id, user_info.name)
    return ApiResponse(
        code=200,
        message="Updated successfully",
        data=work_plan.to_dict()
    )


@router.delete("/{id}", response_model=ApiResponse)
def delete_work_plan(
    id: int,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_info)
):
    """
    删除工作计划（软删除）
    """
    service = WorkPlanService(db)
    service.delete(id, user_info.id, user_info.name)
    return ApiResponse(
        code=200,
        message="Deleted successfully",
        data=None
    )

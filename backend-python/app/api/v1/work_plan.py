"""
工作计划API
提供工作计划的HTTP接口
"""
import logging

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import UserInfo, get_current_user_info
from app.schemas.common import ApiResponse, PaginatedResponse
from app.schemas.work_plan import WorkPlanCreate, WorkPlanUpdate
from app.services.work_plan import WorkPlanService

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


@router.get("", response_model=PaginatedResponse)
def get_work_plans_list(
    page: int = Query(0, ge=0, description="Page number, starts from 0"),
    size: int = Query(10, ge=1, le=1000, description="Page size"),
    plan_type: str | None = Query(None, description="工单类型：定期巡检/临时维修/零星用工"),
    project_name: str | None = Query(None, description="Project name (fuzzy search)"),
    client_name: str | None = Query(None, description="Client name (fuzzy search)"),
    status: str | None = Query(None, description="Status"),
    plan_id: str | None = Query(None, description="Plan ID (fuzzy search)"),
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_info)
):
    service = WorkPlanService(db)
    maintenance_personnel = user_info.get_maintenance_personnel_filter()

    items, total = service.get_all(
        page=page, size=size, plan_type=plan_type, project_name=project_name,
        client_name=client_name, status=status, maintenance_personnel=maintenance_personnel,
        plan_id=plan_id
    )
    items_dict = [item.to_dict() for item in items]

    from app.models.periodic_inspection import PeriodicInspection
    from app.models.temporary_repair import TemporaryRepair
    from app.models.spot_work import SpotWork
    from app.models.maintenance_plan import MaintenancePlan

    inspection_ids = [d['plan_id'] for d in items_dict if d.get('plan_type') == '定期巡检']
    repair_ids = [d['plan_id'] for d in items_dict if d.get('plan_type') == '临时维修']
    spotwork_ids = [d['plan_id'] for d in items_dict if d.get('plan_type') == '零星用工']
    maintenance_ids = [d['plan_id'] for d in items_dict if d.get('plan_type') == '定期维保']

    source_map = {}
    if inspection_ids:
        rows = db.query(PeriodicInspection.id, PeriodicInspection.inspection_id).filter(
            PeriodicInspection.inspection_id.in_(inspection_ids),
            PeriodicInspection.is_deleted == False
        ).all()
        for r in rows:
            source_map[('inspection', r.inspection_id)] = r.id
    if repair_ids:
        rows = db.query(TemporaryRepair.id, TemporaryRepair.repair_id).filter(
            TemporaryRepair.repair_id.in_(repair_ids),
            TemporaryRepair.is_deleted == False
        ).all()
        for r in rows:
            source_map[('repair', r.repair_id)] = r.id
    if spotwork_ids:
        rows = db.query(SpotWork.id, SpotWork.work_id).filter(
            SpotWork.work_id.in_(spotwork_ids),
            SpotWork.is_deleted == False
        ).all()
        for r in rows:
            source_map[('spotwork', r.work_id)] = r.id
    if maintenance_ids:
        rows = db.query(MaintenancePlan.id, MaintenancePlan.plan_id).filter(
            MaintenancePlan.plan_id.in_(maintenance_ids),
            MaintenancePlan.is_deleted == False
        ).all()
        for r in rows:
            source_map[('maintenance', r.plan_id)] = r.id

    type_code_map = {'定期巡检': 'inspection', '临时维修': 'repair', '零星用工': 'spotwork', '定期维保': 'maintenance'}
    for d in items_dict:
        tc = type_code_map.get(d.get('plan_type', ''), '')
        d['order_type_code'] = tc
        d['source_id'] = source_map.get((tc, d.get('plan_id', '')))

    return PaginatedResponse.success(items_dict, total, page, size)


@router.get("/{id}", response_model=ApiResponse)
def get_work_plan_by_id(
    id: int,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_info)
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
    dto: WorkPlanCreate,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_info)
):
    service = WorkPlanService(db)
    work_plan = service.create(dto, user_info.id, user_info.name)
    return ApiResponse(
        code=200,
        message="创建成功",
        data=work_plan.to_dict()
    )


@router.put("/{id}", response_model=ApiResponse)
def update_work_plan(
    id: int,
    dto: WorkPlanUpdate,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_info)
):
    service = WorkPlanService(db)
    work_plan = service.update(id, dto, user_info.id, user_info.name)
    return ApiResponse(
        code=200,
        message="更新成功",
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
        message="删除成功",
        data=None
    )

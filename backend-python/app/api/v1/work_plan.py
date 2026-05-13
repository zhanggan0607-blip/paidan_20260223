"""
宸ヤ綔璁″垝API
鎻愪緵宸ヤ綔璁″垝鐨凥TTP鎺ュ彛
"""
from app.utils.logging_config import get_logger

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import UserInfo, get_current_user_required
from app.schemas.common import ApiResponse, PaginatedResponse
from app.schemas.work_plan import WorkPlanCreate, WorkPlanUpdate
from app.services.work_plan import WorkPlanService

logger = get_logger(__name__)
router = APIRouter(prefix="/work-plan", tags=["Work Plan Management"])


@router.get("/statistics", response_model=ApiResponse)
def get_statistics(
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_required)
):
    """
    鑾峰彇宸ヤ綔璁″垝缁熻鏁版嵁
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
    plan_type: str | None = Query(None, description="宸ュ崟绫诲瀷锛氬畾鏈熷贰妫€/涓存椂缁翠慨/闆舵槦鐢ㄥ伐"),
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_required)
):
    """
    鑾峰彇鎵€鏈夊伐浣滆鍒掞紙涓嶅垎椤碉級
    鏅€氱敤鎴峰彧鑳界湅鍒拌嚜宸辩殑鏁版嵁锛岀鐞嗗憳鍙互鐪嬪埌鎵€鏈夋暟鎹?
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
    plan_type: str | None = Query(None, description="宸ュ崟绫诲瀷锛氬畾鏈熷贰妫€/涓存椂缁翠慨/闆舵槦鐢ㄥ伐"),
    project_name: str | None = Query(None, description="Project name (fuzzy search)"),
    client_name: str | None = Query(None, description="Client name (fuzzy search)"),
    status: str | None = Query(None, description="Status"),
    plan_id: str | None = Query(None, description="Plan ID (fuzzy search)"),
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_required)
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

    inspection_ids = [d['plan_id'] for d in items_dict if d.get('plan_type') == '瀹氭湡宸℃']
    repair_ids = [d['plan_id'] for d in items_dict if d.get('plan_type') == '涓存椂缁翠慨']
    spotwork_ids = [d['plan_id'] for d in items_dict if d.get('plan_type') == '闆舵槦鐢ㄥ伐']
    maintenance_ids = [d['plan_id'] for d in items_dict if d.get('plan_type') == '瀹氭湡缁翠繚']

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

    type_code_map = {'瀹氭湡宸℃': 'inspection', '涓存椂缁翠慨': 'repair', '闆舵槦鐢ㄥ伐': 'spotwork', '瀹氭湡缁翠繚': 'maintenance'}
    for d in items_dict:
        tc = type_code_map.get(d.get('plan_type', ''), '')
        d['order_type_code'] = tc
        d['source_id'] = source_map.get((tc, d.get('plan_id', '')))

    return PaginatedResponse.success(items_dict, total, page, size)


@router.get("/{id}", response_model=ApiResponse)
def get_work_plan_by_id(
    id: int,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_required)
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
    user_info: UserInfo = Depends(get_current_user_required)
):
    service = WorkPlanService(db)
    work_plan = service.create(dto, user_info.id, user_info.name)
    return ApiResponse(
        code=200,
        message="鍒涘缓鎴愬姛",
        data=work_plan.to_dict()
    )


@router.put("/{id}", response_model=ApiResponse)
def update_work_plan(
    id: int,
    dto: WorkPlanUpdate,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_required)
):
    service = WorkPlanService(db)
    work_plan = service.update(id, dto, user_info.id, user_info.name)
    return ApiResponse(
        code=200,
        message="鏇存柊鎴愬姛",
        data=work_plan.to_dict()
    )


@router.delete("/{id}", response_model=ApiResponse)
def delete_work_plan(
    id: int,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_required)
):
    """
    鍒犻櫎宸ヤ綔璁″垝锛堣蒋鍒犻櫎锛?
    """
    service = WorkPlanService(db)
    service.delete(id, user_info.id, user_info.name)
    return ApiResponse(
        code=200,
        message="鍒犻櫎鎴愬姛",
        data=None
    )

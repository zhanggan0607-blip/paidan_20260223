"""
缁翠繚璁″垝API
鎻愪緵缁翠繚璁″垝鐨凥TTP鎺ュ彛
"""
from app.utils.logging_config import get_logger
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import (
    UserInfo,
    assert_data_owner_or_manager,
    get_current_user_required,
    get_manager_user,
)
from app.schemas.common import ApiResponse, PaginatedResponse
from app.schemas.maintenance_plan import (
    MaintenancePlanCreate,
    MaintenancePlanUpdate,
)
from app.services.maintenance_plan import MaintenancePlanService

logger = get_logger(__name__)
router = APIRouter(prefix="/maintenance-plan", tags=["Maintenance Plan Management"])


@router.get("/all/list", response_model=ApiResponse)
def get_all_maintenance_plan(
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_required)
):
    """
    鑾峰彇鎵€鏈夌淮淇濊鍒掞紙涓嶅垎椤碉級
    鏅€氱敤鎴峰彧鑳界湅鍒拌嚜宸辩殑鏁版嵁锛岀鐞嗗憳鍙互鐪嬪埌鎵€鏈夋暟鎹?    """
    service = MaintenancePlanService(db)
    items = service.get_all_unpaginated()

    if not user_info.is_manager and user_info.name:
        items = [item for item in items if item.maintenance_personnel == user_info.name]

    return ApiResponse.success([item.to_dict() for item in items])


@router.get("/project/{project_id}", response_model=ApiResponse)
def get_maintenance_plan_by_project(
    project_id: str,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_required)
):
    """
    鏍规嵁椤圭洰ID鑾峰彇缁翠繚璁″垝
    鏅€氱敤鎴峰彧鑳界湅鍒拌嚜宸辩殑鏁版嵁锛岀鐞嗗憳鍙互鐪嬪埌鎵€鏈夋暟鎹?    """
    service = MaintenancePlanService(db)
    items = service.get_by_project_id(project_id)

    if not user_info.is_manager and user_info.name:
        items = [item for item in items if item.maintenance_personnel == user_info.name]

    return ApiResponse.success([item.to_dict() for item in items])


@router.get("/upcoming/list", response_model=ApiResponse)
def get_upcoming_maintenance(
    days: int = Query(7, ge=1, le=365, description="Query days"),
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_required)
):
    """
    鑾峰彇鍗冲皢鍒版湡鐨勭淮淇濊鍒?    鏅€氱敤鎴峰彧鑳界湅鍒拌嚜宸辩殑鏁版嵁锛岀鐞嗗憳鍙互鐪嬪埌鎵€鏈夋暟鎹?    """
    service = MaintenancePlanService(db)
    items = service.get_upcoming_maintenance(days)

    if not user_info.is_manager and user_info.name:
        items = [item for item in items if item.maintenance_personnel == user_info.name]

    return ApiResponse.success([item.to_dict() for item in items])


@router.get("/date-range/list", response_model=ApiResponse)
def get_maintenance_plan_by_date_range(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_required)
):
    """
    鏍规嵁鏃ユ湡鑼冨洿鑾峰彇缁翠繚璁″垝
    鏅€氱敤鎴峰彧鑳界湅鍒拌嚜宸辩殑鏁版嵁锛岀鐞嗗憳鍙互鐪嬪埌鎵€鏈夋暟鎹?    """
    try:
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format, please use YYYY-MM-DD"
        ) from e

    service = MaintenancePlanService(db)
    items = service.get_by_date_range(start, end)

    if not user_info.is_manager and user_info.name:
        items = [item for item in items if item.maintenance_personnel == user_info.name]

    return ApiResponse.success([item.to_dict() for item in items])


@router.get("", response_model=PaginatedResponse)
def get_maintenance_plan_list(
    page: int = Query(0, ge=0, description="Page number, starts from 0"),
    size: int = Query(10, ge=1, le=1000, description="Page size"),
    plan_name: str | None = Query(None, description="Plan name (fuzzy search)"),
    project_id: str | None = Query(None, description="Project ID"),
    equipment_name: str | None = Query(None, description="Equipment name (fuzzy search)"),
    plan_status: str | None = Query(None, description="Plan status"),
    execution_status: str | None = Query(None, description="Execution status"),
    responsible_person: str | None = Query(None, description="Responsible person (fuzzy search)"),
    project_name: str | None = Query(None, description="Project name (fuzzy search)"),
    client_name: str | None = Query(None, description="Client name (fuzzy search)"),
    plan_type: str | None = Query(None, description="Plan type (瀹氭湡缁翠繚/涓存椂缁翠慨/闆舵槦鐢ㄥ伐)"),
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_required)
):
    """
    鍒嗛〉鑾峰彇缁翠繚璁″垝鍒楄〃
    鏅€氱敤鎴峰彧鑳界湅鍒拌嚜宸辩殑鏁版嵁锛岀鐞嗗憳鍙互鐪嬪埌鎵€鏈夋暟鎹?    """
    service = MaintenancePlanService(db)
    responsible_person_filter = user_info.get_maintenance_personnel_filter()

    items, total = service.get_all(
        page, size, plan_name, project_id, equipment_name,
        plan_status, execution_status, responsible_person,
        project_name, client_name, plan_type, responsible_person_filter
    )
    items_dict = [item.to_dict() for item in items]
    return PaginatedResponse.success(items_dict, total, page, size)


@router.get("/plan-id/{plan_id}", response_model=ApiResponse)
def get_maintenance_plan_by_plan_id(
    plan_id: str,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_required)
):
    """
    閫氳繃璁″垝缂栧彿鑾峰彇缁翠繚璁″垝璇︽儏
    绠＄悊鍛樺彲鏌ョ湅鎵€鏈夛紝鏅€氱敤鎴峰彧鑳芥煡鐪嬭嚜宸辩殑鏁版嵁
    """
    service = MaintenancePlanService(db)
    maintenance_plan = service.get_by_plan_id(plan_id)

    assert_data_owner_or_manager(user_info, maintenance_plan.maintenance_personnel)

    return ApiResponse.success(maintenance_plan.to_dict())


@router.get("/{id}", response_model=ApiResponse)
def get_maintenance_plan_by_id(
    id: int,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_required)
):
    """
    鏍规嵁ID鑾峰彇缁翠繚璁″垝璇︽儏
    绠＄悊鍛樺彲鏌ョ湅鎵€鏈夛紝鏅€氱敤鎴峰彧鑳芥煡鐪嬭嚜宸辩殑鏁版嵁
    """
    service = MaintenancePlanService(db)
    maintenance_plan = service.get_by_id(id)

    assert_data_owner_or_manager(user_info, maintenance_plan.maintenance_personnel)

    return ApiResponse.success(maintenance_plan.to_dict())


@router.post("", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
def create_maintenance_plan(
    dto: MaintenancePlanCreate,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_manager_user)
):
    """
    鍒涘缓缁翠繚璁″垝
    闇€瑕佺鐞嗗憳鎴栭儴闂ㄧ粡鐞嗘潈闄?    """
    logger.info(f"Creating maintenance plan: plan_id={dto.plan_id}, plan_name={dto.plan_name}")

    service = MaintenancePlanService(db)
    maintenance_plan = service.create(dto, user_info.id, user_info.name)

    logger.info(f"Created successfully: id={maintenance_plan.id}, plan_id={maintenance_plan.plan_id}")
    return ApiResponse.success(maintenance_plan.to_dict(), "Created successfully")


@router.put("/{id}", response_model=ApiResponse)
def update_maintenance_plan(
    id: int,
    dto: MaintenancePlanUpdate,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_required)
):
    """
    鏇存柊缁翠繚璁″垝
    绠＄悊鍛樺彲鏇存柊鎵€鏈夛紝鏅€氱敤鎴峰彧鑳芥洿鏂拌嚜宸辩殑鏁版嵁
    """
    service = MaintenancePlanService(db)

    existing_plan = service.get_by_id(id)
    assert_data_owner_or_manager(user_info, existing_plan.maintenance_personnel)

    maintenance_plan = service.update(id, dto, user_info.id, user_info.name)
    return ApiResponse.success(maintenance_plan.to_dict(), "Updated successfully")


@router.delete("/{id}", response_model=ApiResponse)
def delete_maintenance_plan(
    id: int,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_manager_user)
):
    """
    鍒犻櫎缁翠繚璁″垝锛堣蒋鍒犻櫎锛?    闇€瑕佺鐞嗗憳鎴栭儴闂ㄧ粡鐞嗘潈闄?    """
    service = MaintenancePlanService(db)
    deleted_stats = service.delete(id, user_info.id, user_info.name)
    return ApiResponse.success(deleted_stats, "鍒犻櫎鎴愬姛")


@router.patch("/{id}/status", response_model=ApiResponse)
def update_execution_status(
    id: int,
    status: str = Query(..., description="Execution status"),
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_manager_user)
):
    """
    鏇存柊鎵ц鐘舵€?    闇€瑕佺鐞嗗憳鎴栭儴闂ㄧ粡鐞嗘潈闄?    """
    service = MaintenancePlanService(db)
    maintenance_plan = service.update_execution_status(id, status, user_info.id, user_info.name)
    return ApiResponse.success(maintenance_plan.to_dict(), "Status updated successfully")


@router.patch("/{id}/completion-rate", response_model=ApiResponse)
def update_completion_rate(
    id: int,
    rate: int = Query(..., ge=0, le=100, description="Completion rate (0-100)"),
    db: Session = Depends(get_db)
):
    """
    鏇存柊瀹屾垚鐜?    """
    service = MaintenancePlanService(db)
    maintenance_plan = service.update_completion_rate(id, rate)
    return ApiResponse.success(maintenance_plan.to_dict(), "Completion rate updated successfully")

from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.maintenance_plan import MaintenancePlanService
from app.schemas.maintenance_plan import (
    MaintenancePlanCreate,
    MaintenancePlanUpdate,
    MaintenancePlanResponse,
    PaginatedResponse,
    ApiResponse
)
from app.auth import get_current_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/maintenance-plan", tags=["Maintenance Plan Management"])


@router.get("/all/list", response_model=ApiResponse)
def get_all_maintenance_plan(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    service = MaintenancePlanService(db)
    items = service.get_all_unpaginated()
    return ApiResponse.success([item.to_dict() for item in items])


@router.get("/project/{project_id}", response_model=ApiResponse)
def get_maintenance_plan_by_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    service = MaintenancePlanService(db)
    items = service.get_by_project_id(project_id)
    return ApiResponse.success([item.to_dict() for item in items])


@router.get("/upcoming/list", response_model=ApiResponse)
def get_upcoming_maintenance(
    days: int = Query(7, ge=1, le=365, description="Query days"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    service = MaintenancePlanService(db)
    items = service.get_upcoming_maintenance(days)
    return ApiResponse.success([item.to_dict() for item in items])


@router.get("/date-range/list", response_model=ApiResponse)
def get_maintenance_plan_by_date_range(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format, please use YYYY-MM-DD"
        )

    service = MaintenancePlanService(db)
    items = service.get_by_date_range(start, end)
    return ApiResponse.success([item.to_dict() for item in items])


@router.get("", response_model=PaginatedResponse)
def get_maintenance_plan_list(
    page: int = Query(0, ge=0, description="Page number, starts from 0"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    plan_name: Optional[str] = Query(None, description="Plan name (fuzzy search)"),
    project_id: Optional[str] = Query(None, description="Project ID"),
    equipment_name: Optional[str] = Query(None, description="Equipment name (fuzzy search)"),
    plan_status: Optional[str] = Query(None, description="Plan status"),
    execution_status: Optional[str] = Query(None, description="Execution status"),
    responsible_person: Optional[str] = Query(None, description="Responsible person (fuzzy search)"),
    project_name: Optional[str] = Query(None, description="Project name (fuzzy search)"),
    client_name: Optional[str] = Query(None, description="Client name (fuzzy search)"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    service = MaintenancePlanService(db)
    items, total = service.get_all(
        page, size, plan_name, project_id, equipment_name,
        plan_status, execution_status, responsible_person,
        project_name, client_name
    )
    items_dict = [item.to_dict() for item in items]
    return PaginatedResponse.success(items_dict, total, page, size)


@router.get("/{id}", response_model=ApiResponse)
def get_maintenance_plan_by_id(
    id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    service = MaintenancePlanService(db)
    maintenance_plan = service.get_by_id(id)
    return ApiResponse.success(maintenance_plan.to_dict())


@router.post("", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
def create_maintenance_plan(
    dto: MaintenancePlanCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    logger.info(f"Creating maintenance plan: plan_id={dto.plan_id}, plan_name={dto.plan_name}")

    service = MaintenancePlanService(db)
    maintenance_plan = service.create(dto)

    logger.info(f"Created successfully: id={maintenance_plan.id}, plan_id={maintenance_plan.plan_id}")
    return ApiResponse.success(maintenance_plan.to_dict(), "Created successfully")


@router.put("/{id}", response_model=ApiResponse)
def update_maintenance_plan(
    id: int,
    dto: MaintenancePlanUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    service = MaintenancePlanService(db)
    maintenance_plan = service.update(id, dto)
    return ApiResponse.success(maintenance_plan.to_dict(), "Updated successfully")


@router.delete("/{id}", response_model=ApiResponse)
def delete_maintenance_plan(
    id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    service = MaintenancePlanService(db)
    service.delete(id)
    return ApiResponse.success(None, "Deleted successfully")


@router.patch("/{id}/status", response_model=ApiResponse)
def update_execution_status(
    id: int,
    status: str = Query(..., description="Execution status"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    service = MaintenancePlanService(db)
    maintenance_plan = service.update_execution_status(id, status)
    return ApiResponse.success(maintenance_plan.to_dict(), "Status updated successfully")


@router.patch("/{id}/completion-rate", response_model=ApiResponse)
def update_completion_rate(
    id: int,
    rate: int = Query(..., ge=0, le=100, description="Completion rate (0-100)"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    service = MaintenancePlanService(db)
    maintenance_plan = service.update_completion_rate(id, rate)
    return ApiResponse.success(maintenance_plan.to_dict(), "Completion rate updated successfully")

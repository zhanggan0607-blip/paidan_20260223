from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.user_dashboard_config import UserDashboardConfigService
from app.schemas.common import ApiResponse


router = APIRouter(prefix="/user-dashboard-config", tags=["User Dashboard Config"])


@router.get("/{dashboard_type}", response_model=ApiResponse)
def get_dashboard_config(
    dashboard_type: str,
    user_id: Optional[str] = Query(None, description="User ID"),
    db: Session = Depends(get_db)
):
    service = UserDashboardConfigService(db)
    user_id = user_id or 'default'
    config = service.get_by_user_and_type(user_id, dashboard_type)
    return ApiResponse(
        code=200,
        message="success",
        data=config.to_dict()
    )


@router.post("", response_model=ApiResponse)
def save_dashboard_config(
    user_id: str = Query(..., description="User ID"),
    dashboard_type: str = Query(..., description="Dashboard type"),
    config: dict = None,
    db: Session = Depends(get_db)
):
    service = UserDashboardConfigService(db)
    config = service.save_config(user_id, dashboard_type, config)
    return ApiResponse(
        code=200,
        message="Saved successfully",
        data=config.to_dict()
    )


@router.delete("/{dashboard_type}", response_model=ApiResponse)
def delete_dashboard_config(
    dashboard_type: str,
    user_id: str = Query(..., description="User ID"),
    db: Session = Depends(get_db)
):
    service = UserDashboardConfigService(db)
    service.delete_config(user_id, dashboard_type)
    return ApiResponse(
        code=200,
        message="Deleted successfully",
        data=None
    )


@router.get("/all/{user_id}", response_model=ApiResponse)
def get_all_dashboard_configs(
    user_id: str,
    db: Session = Depends(get_db)
):
    service = UserDashboardConfigService(db)
    configs = service.get_all_by_user(user_id)
    return ApiResponse(
        code=200,
        message="success",
        data=[config.to_dict() for config in configs]
    )

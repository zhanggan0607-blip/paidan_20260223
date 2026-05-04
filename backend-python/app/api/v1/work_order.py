"""
工单管理API - 合并定期巡检、临时维修、零星用工三种工单数据
"""
import logging

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import UserInfo, get_current_user_required
from app.schemas.common import ApiResponse, PaginatedResponse
from app.services.work_order import WorkOrderService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/work-order", tags=["Work Order Management"])


@router.get("", response_model=PaginatedResponse)
def get_work_order_list(
    request: Request,
    page: int = Query(0, ge=0, description="页码，从0开始"),
    size: int = Query(10, ge=1, le=100, description="每页数量"),
    project_name: str | None = Query(None, description="项目名称(模糊搜索)"),
    order_id: str | None = Query(None, description="工单编号(模糊搜索)"),
    order_type: str | None = Query(None, description="工单类型: inspection/repair/spotwork"),
    status: str | None = Query(None, description="状态"),
    maintenance_personnel: str | None = Query(None, description="运维人员(模糊搜索)"),
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_required),
):
    service = WorkOrderService(db)
    all_orders, total = service.get_work_order_list(
        project_name=project_name,
        order_id=order_id,
        order_type=order_type,
        status=status,
        maintenance_personnel=maintenance_personnel,
        user_name=user_info.name,
        is_manager=user_info.is_manager,
        page=page,
        size=size,
    )
    return PaginatedResponse.success(all_orders, total, page, size)


@router.get("/all/list", response_model=ApiResponse)
def get_all_work_orders(
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_required),
):
    service = WorkOrderService(db)
    all_orders = service.get_all_work_orders(
        user_name=user_info.name,
        is_manager=user_info.is_manager,
    )
    return ApiResponse.success(all_orders)


@router.get("/completed-this-year", response_model=PaginatedResponse)
def get_completed_this_year(
    request: Request,
    page: int = Query(0, ge=0, description="页码，从0开始"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_required),
):
    service = WorkOrderService(db)
    all_orders, total = service.get_completed_this_year(
        user_name=user_info.name,
        is_manager=user_info.is_manager,
        page=page,
        size=size,
    )
    return PaginatedResponse.success(all_orders, total, page, size)

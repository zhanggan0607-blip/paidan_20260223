from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.overdue_alert import OverdueAlertService
from app.schemas.common import ApiResponse
from app.auth import get_current_user

router = APIRouter(prefix="/overdue-alert", tags=["Overdue Alert"])


@router.get("", response_model=ApiResponse)
def get_overdue_alerts(
    project_name: Optional[str] = Query(None, description="项目名称"),
    client_name: Optional[str] = Query(None, description="客户名称"),
    work_order_type: Optional[str] = Query(None, description="工单类型"),
    page: int = Query(0, ge=0, description="页码，从0开始"),
    size: int = Query(10, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user)
):
    user_name = None
    is_manager = False
    if current_user:
        user_name = current_user.get('sub') or current_user.get('name')
        role = current_user.get('role', '')
        is_manager = role in ['管理员', '部门经理', '主管']
    
    maintenance_personnel = None if is_manager else user_name
    
    service = OverdueAlertService(db)
    items, total = service.get_overdue_items(
        project_name=project_name,
        client_name=client_name,
        work_order_type=work_order_type,
        page=page,
        size=size,
        maintenance_personnel=maintenance_personnel
    )
    return ApiResponse(
        code=200,
        message="success",
        data={
            'items': items,
            'total': total
        }
    )

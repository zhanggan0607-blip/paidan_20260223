from typing import Optional
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.expiring_soon import ExpiringSoonService
from app.schemas.common import ApiResponse
from app.auth import get_current_user, get_current_user_from_headers

router = APIRouter(prefix="/expiring-soon", tags=["Expiring Soon Alert"])


@router.get("", response_model=ApiResponse)
def get_expiring_alerts(
    request: Request,
    project_name: Optional[str] = Query(None, description="项目名称"),
    client_name: Optional[str] = Query(None, description="客户名称"),
    work_order_type: Optional[str] = Query(None, description="工单类型"),
    page: int = Query(0, ge=0, description="页码，从0开始"),
    size: int = Query(10, ge=1, le=1000, description="每页数量"),
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user)
):
    """
    获取临期工单列表
    
    返回所有计划结束日期在未来7天内且状态不是"已完成"的工单
    """
    user_info = current_user or get_current_user_from_headers(request)
    user_name = None
    is_manager = False
    if user_info:
        user_name = user_info.get('sub') or user_info.get('name')
        role = user_info.get('role', '')
        is_manager = role in ['管理员', '部门经理', '主管']
    
    maintenance_personnel = None if is_manager else user_name
    
    service = ExpiringSoonService(db)
    items, total = service.get_expiring_items(
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


@router.get("/count", response_model=ApiResponse)
def get_expiring_count(
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user)
):
    """
    获取临期工单数量
    
    用于手机端首页显示临期提醒数量
    """
    user_info = current_user or get_current_user_from_headers(request)
    user_name = None
    is_manager = False
    if user_info:
        user_name = user_info.get('sub') or user_info.get('name')
        role = user_info.get('role', '')
        is_manager = role in ['管理员', '部门经理', '主管']
    
    maintenance_personnel = None if is_manager else user_name
    
    service = ExpiringSoonService(db)
    count = service.get_expiring_count(maintenance_personnel=maintenance_personnel)
    
    return ApiResponse(
        code=200,
        message="success",
        data={
            'count': count
        }
    )

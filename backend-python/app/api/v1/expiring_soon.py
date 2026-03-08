
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import UserInfo, get_current_user_info
from app.schemas.common import ApiResponse
from app.services.expiring_soon import ExpiringSoonService

router = APIRouter(prefix="/expiring-soon", tags=["Expiring Soon Alert"])


@router.get("", response_model=ApiResponse)
def get_expiring_alerts(
    request: Request,
    project_name: str | None = Query(None, description="项目名称"),
    client_name: str | None = Query(None, description="客户名称"),
    work_order_type: str | None = Query(None, description="工单类型"),
    page: int = Query(0, ge=0, description="页码，从0开始"),
    size: int = Query(10, ge=1, le=1000, description="每页数量"),
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_info)
):
    """
    获取临期工单列表

    返回所有计划结束日期在未来7天内且状态不是"已完成"的工单
    """
    user_name = user_info.name if not user_info.is_manager else None

    maintenance_personnel = None if user_info.is_manager else user_name

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
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_info)
):
    """
    获取临期工单数量

    用于手机端首页显示临期提醒数量
    """
    maintenance_personnel = None if user_info.is_manager else user_info.name

    service = ExpiringSoonService(db)
    count = service.get_expiring_count(maintenance_personnel=maintenance_personnel)

    return ApiResponse(
        code=200,
        message="success",
        data={
            'count': count
        }
    )

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.common import ApiResponse
from app.models.temporary_repair import TemporaryRepair
from app.auth import get_current_user
from datetime import datetime


router = APIRouter(prefix="/spare-parts", tags=["Spare Parts Management"])


@router.get("/usage")
def get_spare_parts_usage(
    user: Optional[str] = Query(None, description="领用人员"),
    product: Optional[str] = Query(None, description="产品名称"),
    project: Optional[str] = Query(None, description="项目名称"),
    page: int = Query(0, ge=0, description="页码，从0开始"),
    pageSize: int = Query(10, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    query = db.query(TemporaryRepair)

    if user:
        query = query.filter(TemporaryRepair.maintenance_personnel.like(f'%{user}%'))

    if product:
        query = query.filter(TemporaryRepair.remarks.like(f'%{product}%'))

    if project:
        query = query.filter(TemporaryRepair.project_name.like(f'%{project}%'))

    total = query.count()
    items = query.offset(page * pageSize).limit(pageSize).all()

    result_items = []
    for item in items:
        result_items.append({
            'id': item.id,
            'projectId': item.project_id,
            'projectName': item.project_name,
            'productName': item.remarks or '',
            'brand': '',
            'model': '',
            'quantity': 1,
            'userName': item.maintenance_personnel or '',
            'issueTime': item.created_at.strftime('%Y-%m-%d %H:%M:%S') if item.created_at else '',
            'unit': '件'
        })

    return ApiResponse(
        code=200,
        message="success",
        data={
            'items': result_items,
            'total': total
        }
    )

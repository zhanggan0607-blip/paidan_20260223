from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.common import ApiResponse
from app.models.spare_parts_usage import SparePartsUsage
from app.services.spare_parts_usage import SparePartsUsageService
import logging

logger = logging.getLogger(__name__)


router = APIRouter(prefix="/spare-parts", tags=["Spare Parts Management"])


@router.get("/usage", response_model=ApiResponse)
def get_spare_parts_usage(
    user: Optional[str] = Query(None, description="领用人员"),
    product: Optional[str] = Query(None, description="产品名称"),
    project: Optional[str] = Query(None, description="项目名称"),
    page: int = Query(0, ge=0, description="页码，从0开始"),
    pageSize: int = Query(10, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db)
):
    """查询备品备件领用记录"""
    logger.info(f"查询备品备件领用记录: user={user}, product={product}, project={project}, page={page}, pageSize={pageSize}")
    
    service = SparePartsUsageService(db)
    items, total = service.get_all(
        page=page, 
        size=pageSize, 
        user=user, 
        product=product, 
        project=project
    )
    
    result_items = []
    for item in items:
        result_items.append({
            'id': item.id,
            'projectId': item.project_id or '',
            'projectName': item.project_name or '',
            'productName': item.product_name,
            'brand': item.brand or '',
            'model': item.model or '',
            'quantity': item.quantity,
            'userName': item.user_name,
            'issueTime': item.issue_time,
            'unit': item.unit
        })

    logger.info(f"查询成功: 返回{len(result_items)}条记录，总计{total}条")
    
    return ApiResponse(
        code=200,
        message="success",
        data={
            'items': result_items,
            'total': total
        }
    )

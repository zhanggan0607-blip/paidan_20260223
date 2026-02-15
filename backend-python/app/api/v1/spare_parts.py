from typing import List, Optional, Union
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from datetime import datetime
from app.database import get_db
from app.schemas.common import ApiResponse
from app.models.spare_parts_usage import SparePartsUsage
from app.models.spare_parts_stock import SparePartsStock
from app.services.spare_parts_usage import SparePartsUsageService
import logging

logger = logging.getLogger(__name__)


router = APIRouter(prefix="/spare-parts", tags=["Spare Parts Management"])


class SparePartsUsageCreate(BaseModel):
    product_name: str = Field(..., min_length=1, max_length=200, description="产品名称")
    brand: Optional[str] = Field(None, max_length=100, description="品牌")
    model: Optional[str] = Field(None, max_length=100, description="产品型号")
    quantity: int = Field(..., gt=0, description="领用数量")
    user_name: str = Field(..., min_length=1, max_length=100, description="领用人员")
    issue_time: Union[str, datetime] = Field(..., description="领用时间")
    unit: str = Field("件", max_length=20, description="单位")
    project_id: Optional[str] = Field(None, max_length=50, description="项目编号")
    project_name: Optional[str] = Field(None, max_length=200, description="项目名称")


@router.post("/usage", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
def create_spare_parts_usage(
    data: SparePartsUsageCreate,
    db: Session = Depends(get_db)
):
    """创建备品备件领用记录"""
    logger.info(f"创建备品备件领用记录: {data}")
    
    try:
        issue_time = data.issue_time
        if isinstance(issue_time, str):
            try:
                issue_time = datetime.fromisoformat(issue_time.replace('Z', '+00:00'))
            except ValueError:
                try:
                    issue_time = datetime.strptime(issue_time, '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    issue_time = datetime.strptime(issue_time, '%Y-%m-%d')
        
        stock = db.query(SparePartsStock).filter(
            SparePartsStock.product_name == data.product_name,
            SparePartsStock.brand == (data.brand or ''),
            SparePartsStock.model == (data.model or '')
        ).first()
        
        if stock:
            if stock.quantity < data.quantity:
                return ApiResponse(code=400, message=f"库存不足，当前库存: {stock.quantity}", data=None)
            stock.quantity -= data.quantity
        
        usage = SparePartsUsage(
            product_name=data.product_name,
            brand=data.brand or '',
            model=data.model or '',
            quantity=data.quantity,
            user_name=data.user_name,
            issue_time=issue_time,
            unit=data.unit,
            project_id=data.project_id,
            project_name=data.project_name
        )
        
        db.add(usage)
        db.commit()
        db.refresh(usage)
        
        logger.info(f"备品备件领用记录创建成功: id={usage.id}")
        
        return ApiResponse(
            code=200,
            message="领用成功",
            data={
                'id': usage.id,
                'product_name': usage.product_name,
                'quantity': usage.quantity,
                'user_name': usage.user_name
            }
        )
    except Exception as e:
        db.rollback()
        logger.error(f"创建备品备件领用记录失败: {str(e)}")
        return ApiResponse(code=500, message=f"领用失败: {str(e)}", data=None)


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
            'project_id': item.project_id or '',
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

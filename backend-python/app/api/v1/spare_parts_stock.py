from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status, Body
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.common import ApiResponse
from app.models.spare_parts_inbound import SparePartsInbound
from app.models.spare_parts_stock import SparePartsStock
from datetime import datetime
from pydantic import BaseModel, Field
import random
import string


router = APIRouter(prefix="/spare-parts", tags=["Spare Parts Management"])


def generate_inbound_no() -> str:
    """生成入库单号"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_str = ''.join(random.choices(string.digits, k=4))
    return f"IN{timestamp}{random_str}"


class SparePartsInboundCreate(BaseModel):
    product_name: str = Field(..., min_length=1, max_length=200, description="产品名称")
    quantity: int = Field(..., gt=0, description="入库数量")
    brand: Optional[str] = Field(None, max_length=100, description="品牌")
    model: Optional[str] = Field(None, max_length=100, description="产品型号")
    supplier: Optional[str] = Field(None, max_length=200, description="供应商")
    unit: str = Field("件", max_length=20, description="单位")
    user_name: Optional[str] = Field(None, max_length=100, description="入库人")
    remarks: Optional[str] = Field(None, max_length=500, description="备注")


@router.post("/inbound", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
def create_inbound(
    data: SparePartsInboundCreate,
    db: Session = Depends(get_db)
):
    """创建入库单"""
    print(f"接收到的数据: {data}")
    
    if not data.product_name or not data.product_name.strip():
        return ApiResponse(code=400, message="产品名称不能为空", data=None)

    if data.quantity <= 0:
        return ApiResponse(code=400, message="入库数量必须大于0", data=None)

    if not data.user_name or not data.user_name.strip():
        return ApiResponse(code=400, message="入库人不能为空", data=None)

    try:
        inbound_no = generate_inbound_no()

        inbound = SparePartsInbound(
            inbound_no=inbound_no,
            product_name=data.product_name,
            brand=data.brand,
            model=data.model,
            quantity=data.quantity,
            supplier=data.supplier,
            unit=data.unit,
            user_name=data.user_name,
            remarks=data.remarks
        )
        db.add(inbound)

        stock = db.query(SparePartsStock).filter(
            SparePartsStock.product_name == data.product_name,
            SparePartsStock.brand == (data.brand or ''),
            SparePartsStock.model == (data.model or '')
        ).first()

        if stock:
            stock.quantity += data.quantity
        else:
            stock = SparePartsStock(
                product_name=data.product_name,
                brand=data.brand or '',
                model=data.model or '',
                unit=data.unit,
                quantity=data.quantity
            )
            db.add(stock)

        db.commit()

        return ApiResponse(
            code=200,
            message="入库单创建成功",
            data={'inboundNo': inbound_no}
        )
    except Exception as e:
        db.rollback()
        return ApiResponse(code=500, message=f"入库失败: {str(e)}", data=None)


@router.get("/inbound-records", response_model=ApiResponse)
def get_inbound_records(
    product: Optional[str] = Query(None, description="产品名称"),
    user: Optional[str] = Query(None, description="入库人"),
    page: int = Query(0, ge=0, description="页码，从0开始"),
    pageSize: int = Query(10, ge=1, le=2000, description="每页数量"),
    db: Session = Depends(get_db)
):
    """查询入库记录"""
    query = db.query(SparePartsInbound)

    if product:
        query = query.filter(SparePartsInbound.product_name.like(f'%{product}%'))

    if user:
        query = query.filter(SparePartsInbound.user_name.like(f'%{user}%'))

    total = query.count()
    items = query.order_by(SparePartsInbound.created_at.desc()).offset(page * pageSize).limit(pageSize).all()

    result_items = [item.to_dict() for item in items]

    return ApiResponse(
        code=200,
        message="success",
        data={
            'items': result_items,
            'total': total
        }
    )


@router.get("/stock", response_model=ApiResponse)
def get_stock(
    product_name: Optional[str] = Query(None, description="产品名称"),
    db: Session = Depends(get_db)
):
    """查询库存"""
    query = db.query(SparePartsStock)

    if product_name:
        query = query.filter(SparePartsStock.product_name.like(f'%{product_name}%'))

    items = query.all()
    result_items = [item.to_dict() for item in items]

    return ApiResponse(
        code=200,
        message="success",
        data={'items': result_items, 'total': len(result_items)}
    )

@router.get("/products", response_model=ApiResponse)
def get_products(
    product_name: Optional[str] = Query(None, description="产品名称"),
    db: Session = Depends(get_db)
):
    """获取备品备件列表（用于表单选择）"""
    query = db.query(SparePartsStock)

    if product_name:
        query = query.filter(SparePartsStock.product_name.like(f'%{product_name}%'))

    items = query.order_by(SparePartsStock.product_name.asc()).all()
    result_items = []

    for item in items:
        result_items.append({
            'id': item.id,
            'productName': item.product_name,
            'brand': item.brand,
            'model': item.model,
            'unit': item.unit
        })

    return ApiResponse(
        code=200,
        message="success",
        data=result_items
    )

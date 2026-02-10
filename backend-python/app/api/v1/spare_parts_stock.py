from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.common import ApiResponse
from app.models.spare_parts_inbound import SparePartsInbound
from app.models.spare_parts_stock import SparePartsStock
from app.auth import get_current_user
from datetime import datetime
import random
import string


router = APIRouter(prefix="/spare-parts", tags=["Spare Parts Management"])


def generate_inbound_no() -> str:
    """生成入库单号"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_str = ''.join(random.choices(string.digits, k=4))
    return f"IN{timestamp}{random_str}"


@router.post("/inbound")
def create_inbound(
    product_name: str,
    quantity: int,
    brand: Optional[str] = None,
    model: Optional[str] = None,
    supplier: Optional[str] = None,
    unit: str = "件",
    user_name: str = "",
    remarks: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """创建入库单"""
    if not product_name:
        return ApiResponse(code=400, message="产品名称不能为空", data=None)

    if quantity <= 0:
        return ApiResponse(code=400, message="入库数量必须大于0", data=None)

    if not user_name:
        return ApiResponse(code=400, message="入库人不能为空", data=None)

    try:
        inbound_no = generate_inbound_no()

        inbound = SparePartsInbound(
            inbound_no=inbound_no,
            product_name=product_name,
            brand=brand,
            model=model,
            quantity=quantity,
            supplier=supplier,
            unit=unit,
            user_name=user_name,
            remarks=remarks
        )
        db.add(inbound)

        stock = db.query(SparePartsStock).filter(
            SparePartsStock.product_name == product_name,
            SparePartsStock.brand == (brand or ''),
            SparePartsStock.model == (model or '')
        ).first()

        if stock:
            stock.quantity += quantity
        else:
            stock = SparePartsStock(
                product_name=product_name,
                brand=brand or '',
                model=model or '',
                unit=unit,
                quantity=quantity
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


@router.get("/inbound-records")
def get_inbound_records(
    product: Optional[str] = Query(None, description="产品名称"),
    user: Optional[str] = Query(None, description="入库人"),
    page: int = Query(0, ge=0, description="页码，从0开始"),
    pageSize: int = Query(10, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
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


@router.get("/stock")
def get_stock(
    product_name: Optional[str] = Query(None, description="产品名称"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
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

@router.get("/products")
def get_products(
    product_name: Optional[str] = Query(None, description="产品名称"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
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

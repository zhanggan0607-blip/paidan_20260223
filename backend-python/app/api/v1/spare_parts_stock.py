import logging
import random
import string
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import UserInfo, get_current_user_required
from app.exceptions import BusinessException, ValidationException
from app.models.spare_parts_inbound import SparePartsInbound
from app.models.spare_parts_stock import SparePartsStock
from app.schemas.common import ApiResponse

logger = logging.getLogger(__name__)


router = APIRouter(prefix="/spare-parts-stock", tags=["Spare Parts Stock Management"])


def generate_inbound_no() -> str:
    """生成入库单号"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_str = ''.join(random.choices(string.digits, k=4))
    return f"IN{timestamp}{random_str}"


class SparePartsInboundCreate(BaseModel):
    product_name: str = Field(..., min_length=1, max_length=200, description="产品名称")
    quantity: int = Field(..., gt=0, description="入库数量")
    brand: str | None = Field(None, max_length=100, description="品牌")
    model: str | None = Field(None, max_length=100, description="产品型号")
    supplier: str | None = Field(None, max_length=200, description="供应商")
    unit: str = Field("件", max_length=20, description="单位")
    user_name: str | None = Field(None, max_length=100, description="入库人")
    remarks: str | None = Field(None, max_length=500, description="备注")


MATERIAL_MANAGER_ROLE = '材料员'


@router.post("/inbound", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
def create_inbound(
    data: SparePartsInboundCreate,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_required)
):
    """
    创建入库单
    需要管理员或材料管理员权限
    """
    if not user_info.is_manager and user_info.role != MATERIAL_MANAGER_ROLE:
        raise BusinessException("需要管理员或材料管理员权限")

    if not data.product_name or not data.product_name.strip():
        raise ValidationException("产品名称不能为空")

    if data.quantity <= 0:
        raise ValidationException("入库数量必须大于0")

    if not data.user_name or not data.user_name.strip():
        raise ValidationException("入库人不能为空")

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
            stock.stock += data.quantity
        else:
            stock = SparePartsStock(
                product_name=data.product_name,
                brand=data.brand or '',
                model=data.model or '',
                unit=data.unit,
                stock=data.quantity
            )
            db.add(stock)

        db.commit()

        logger.info(f"用户 {user_info.name} 创建入库单成功: {inbound_no}")

        return ApiResponse(
            code=200,
            message="入库单创建成功",
            data={'inboundNo': inbound_no}
        )
    except ValidationException:
        raise
    except BusinessException:
        raise
    except Exception as e:
        db.rollback()
        error_id = str(uuid.uuid4())[:8]
        logger.error(f"[{error_id}] 创建入库单失败: {str(e)}")
        raise BusinessException(f"入库操作失败，错误ID: {error_id}，请联系管理员") from None


@router.get("/inbound-records", response_model=ApiResponse)
def get_inbound_records(
    product: str | None = Query(None, description="产品名称"),
    user: str | None = Query(None, description="入库人"),
    page: int = Query(0, ge=0, description="页码，从0开始"),
    pageSize: int = Query(10, ge=1, le=1000, description="每页数量"),
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
    product_name: str | None = Query(None, description="产品名称"),
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
    product_name: str | None = Query(None, description="产品名称"),
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


class SparePartsInboundUpdate(BaseModel):
    product_name: str | None = Field(None, min_length=1, max_length=200, description="产品名称")
    quantity: int | None = Field(None, gt=0, description="入库数量")
    brand: str | None = Field(None, max_length=100, description="品牌")
    model: str | None = Field(None, max_length=100, description="产品型号")
    supplier: str | None = Field(None, max_length=200, description="供应商")
    unit: str | None = Field(None, max_length=20, description="单位")
    user_name: str | None = Field(None, max_length=100, description="入库人")
    remarks: str | None = Field(None, max_length=500, description="备注")


@router.put("/inbound/{inbound_id}", response_model=ApiResponse)
def update_inbound(
    inbound_id: int,
    data: SparePartsInboundUpdate,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_required)
):
    """
    更新入库记录
    需要管理员或材料管理员权限
    """
    if not user_info.is_manager and user_info.role != MATERIAL_MANAGER_ROLE:
        raise BusinessException("需要管理员或材料管理员权限")

    inbound = db.query(SparePartsInbound).filter(SparePartsInbound.id == inbound_id).first()
    if not inbound:
        raise BusinessException("入库记录不存在")

    try:
        old_product_name = inbound.product_name
        old_brand = inbound.brand or ''
        old_model = inbound.model or ''
        old_quantity = inbound.quantity

        if data.product_name is not None:
            inbound.product_name = data.product_name
        if data.brand is not None:
            inbound.brand = data.brand
        if data.model is not None:
            inbound.model = data.model
        if data.quantity is not None:
            inbound.quantity = data.quantity
        if data.supplier is not None:
            inbound.supplier = data.supplier
        if data.unit is not None:
            inbound.unit = data.unit
        if data.user_name is not None:
            inbound.user_name = data.user_name
        if data.remarks is not None:
            inbound.remarks = data.remarks

        new_product_name = inbound.product_name
        new_brand = inbound.brand or ''
        new_model = inbound.model or ''
        new_quantity = inbound.quantity

        if old_product_name != new_product_name or old_brand != new_brand or old_model != new_model:
            old_stock = db.query(SparePartsStock).filter(
                SparePartsStock.product_name == old_product_name,
                SparePartsStock.brand == old_brand,
                SparePartsStock.model == old_model
            ).first()
            if old_stock:
                old_stock.stock -= old_quantity
                if old_stock.stock < 0:
                    old_stock.stock = 0

            new_stock = db.query(SparePartsStock).filter(
                SparePartsStock.product_name == new_product_name,
                SparePartsStock.brand == new_brand,
                SparePartsStock.model == new_model
            ).first()
            if new_stock:
                new_stock.stock += new_quantity
            else:
                new_stock = SparePartsStock(
                    product_name=new_product_name,
                    brand=new_brand,
                    model=new_model,
                    unit=inbound.unit,
                    stock=new_quantity
                )
                db.add(new_stock)
        elif old_quantity != new_quantity:
            stock = db.query(SparePartsStock).filter(
                SparePartsStock.product_name == new_product_name,
                SparePartsStock.brand == new_brand,
                SparePartsStock.model == new_model
            ).first()
            if stock:
                stock.stock = stock.stock - old_quantity + new_quantity
                if stock.stock < 0:
                    stock.stock = 0

        db.commit()
        logger.info(f"用户 {user_info.name} 更新入库记录成功: {inbound.inbound_no}")

        return ApiResponse(
            code=200,
            message="入库记录更新成功",
            data={'inboundNo': inbound.inbound_no}
        )
    except BusinessException:
        raise
    except Exception as e:
        db.rollback()
        error_id = str(uuid.uuid4())[:8]
        logger.error(f"[{error_id}] 更新入库记录失败: {str(e)}")
        raise BusinessException(f"更新操作失败，错误ID: {error_id}，请联系管理员") from None


@router.delete("/inbound/{inbound_id}", response_model=ApiResponse)
def delete_inbound(
    inbound_id: int,
    db: Session = Depends(get_db),
    user_info: UserInfo = Depends(get_current_user_required)
):
    """
    删除入库记录（软删除）
    需要管理员或材料管理员权限
    """
    if not user_info.is_manager and user_info.role != MATERIAL_MANAGER_ROLE:
        raise BusinessException("需要管理员或材料管理员权限")

    inbound = db.query(SparePartsInbound).filter(SparePartsInbound.id == inbound_id).first()
    if not inbound:
        raise BusinessException("入库记录不存在")

    try:
        stock = db.query(SparePartsStock).filter(
            SparePartsStock.product_name == inbound.product_name,
            SparePartsStock.brand == (inbound.brand or ''),
            SparePartsStock.model == (inbound.model or '')
        ).first()
        if stock:
            stock.stock -= inbound.quantity
            if stock.stock < 0:
                stock.stock = 0

        db.delete(inbound)
        db.commit()

        logger.info(f"用户 {user_info.name} 删除入库记录成功: {inbound.inbound_no}")

        return ApiResponse(
            code=200,
            message="入库记录删除成功"
        )
    except BusinessException:
        raise
    except Exception as e:
        db.rollback()
        error_id = str(uuid.uuid4())[:8]
        logger.error(f"[{error_id}] 删除入库记录失败: {str(e)}")
        raise BusinessException(f"删除操作失败，错误ID: {error_id}，请联系管理员") from None

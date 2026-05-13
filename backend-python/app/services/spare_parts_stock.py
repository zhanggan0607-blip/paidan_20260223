"""
备品备件库存Service
提供备品备件库存管理的业务逻辑
"""
import random
import string
import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from app.exceptions import BusinessException, ValidationException
from app.repositories.spare_parts_stock import SparePartsStockRepository, SparePartsInboundRepository
from app.utils.logging_config import get_logger

logger = get_logger(__name__)


class SparePartsStockService:
    def __init__(self, db: Session):
        self._db = db
        self._stock_repo = SparePartsStockRepository(db)
        self._inbound_repo = SparePartsInboundRepository(db)

    @staticmethod
    def generate_inbound_no() -> str:
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        random_str = ''.join(random.choices(string.digits, k=4))
        return f"IN{timestamp}{random_str}"

    def create_inbound(self, data: dict, user_info) -> dict:
        if not data.get('product_name') or not data['product_name'].strip():
            raise ValidationException("产品名称不能为空")
        if data.get('quantity', 0) <= 0:
            raise ValidationException("入库数量必须大于0")
        if not data.get('user_name') or not data['user_name'].strip():
            raise ValidationException("入库人不能为空")

        try:
            inbound_no = self.generate_inbound_no()
            from app.models.spare_parts_inbound import SparePartsInbound
            inbound = SparePartsInbound(
                inbound_no=inbound_no,
                product_name=data['product_name'],
                brand=data.get('brand'),
                model=data.get('model'),
                quantity=data['quantity'],
                supplier=data.get('supplier'),
                unit=data.get('unit', '件'),
                user_name=data['user_name'],
                remarks=data.get('remarks')
            )
            self._db.add(inbound)

            self._stock_repo.upsert_stock(
                product_name=data['product_name'],
                brand=data.get('brand') or '',
                model=data.get('model') or '',
                unit=data.get('unit', '件'),
                quantity=data['quantity']
            )

            self._db.commit()
            logger.info(f"用户 {user_info.name} 创建入库单成功: {inbound_no}")
            return {"inboundNo": inbound_no}
        except (ValidationException, BusinessException):
            raise
        except Exception as e:
            self._db.rollback()
            error_id = str(uuid.uuid4())[:8]
            logger.error(f"[{error_id}] 创建入库单失败: {str(e)}")
            raise BusinessException(f"入库操作失败，错误ID: {error_id}，请联系管理员") from None

    def get_inbound_records(self, product: str | None = None, user: str | None = None,
                            page: int = 0, page_size: int = 10) -> dict:
        items, total = self._inbound_repo.search_inbound_records(product, user, page, page_size)
        return {"items": [item.to_dict() for item in items], "total": total}

    def get_stock(self, product_name: str | None = None) -> dict:
        items = self._stock_repo.search_stock(product_name)
        return {"items": [item.to_dict() for item in items], "total": len(items)}

    def get_products(self, product_name: str | None = None) -> list[dict]:
        items = self._stock_repo.get_products(product_name)
        return [{
            'id': item.id,
            'productName': item.product_name,
            'brand': item.brand,
            'model': item.model,
            'unit': item.unit
        } for item in items]

    def get_inbound_by_id(self, inbound_id: int):
        return self._inbound_repo.get_by_id(inbound_id)

    def update_inbound(self, inbound_id: int, data: dict, user_info) -> dict:
        inbound = self._inbound_repo.get_by_id(inbound_id)
        if not inbound:
            raise ValidationException("入库记录不存在")

        old_quantity = inbound.quantity
        old_product_name = inbound.product_name
        old_brand = inbound.brand or ''
        old_model = inbound.model or ''

        update_data = {k: v for k, v in data.items() if v is not None}
        for key, value in update_data.items():
            setattr(inbound, key, value)

        new_quantity = data.get('quantity', old_quantity)
        new_product_name = data.get('product_name', old_product_name)
        new_brand = data.get('brand', old_brand)
        new_model = data.get('model', old_model)

        product_changed = (new_product_name != old_product_name or
                           new_brand != old_brand or
                           new_model != old_model)
        quantity_diff = new_quantity - old_quantity

        if product_changed:
            self._stock_repo.adjust_stock(old_product_name, old_brand, old_model, -old_quantity)
            self._stock_repo.upsert_stock(
                product_name=new_product_name,
                brand=new_brand,
                model=new_model,
                unit=data.get('unit', inbound.unit or '件'),
                quantity=new_quantity
            )
        elif quantity_diff != 0:
            self._stock_repo.adjust_stock(new_product_name, new_brand, new_model, quantity_diff)

        self._db.commit()
        logger.info(f"用户 {user_info.name} 更新入库单: ID={inbound_id}")
        return inbound.to_dict()

    def delete_inbound(self, inbound_id: int, user_info) -> dict:
        inbound = self._inbound_repo.get_by_id(inbound_id)
        if not inbound:
            raise ValidationException("入库记录不存在")

        self._stock_repo.adjust_stock(
            inbound.product_name,
            inbound.brand or '',
            inbound.model or '',
            -inbound.quantity
        )

        self._db.delete(inbound)
        self._db.commit()
        logger.info(f"用户 {user_info.name} 删除入库单: ID={inbound_id}")
        return {"message": "删除成功"}

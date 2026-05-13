"""
备品备件库存Repository
提供备品备件库存相关的数据库操作
"""
from sqlalchemy.orm import Session

from app.models.spare_parts_inbound import SparePartsInbound
from app.models.spare_parts_stock import SparePartsStock
from app.repositories.base import BaseRepository


class SparePartsStockRepository(BaseRepository[SparePartsStock]):
    def __init__(self, db: Session):
        super().__init__(db, SparePartsStock)

    def find_by_product(self, product_name: str, brand: str, model: str) -> SparePartsStock | None:
        return self.db.query(SparePartsStock).filter(
            SparePartsStock.product_name == product_name,
            SparePartsStock.brand == brand,
            SparePartsStock.model == model
        ).first()

    def search_stock(self, product_name: str | None = None) -> list[SparePartsStock]:
        query = self.db.query(SparePartsStock)
        if product_name:
            query = query.filter(SparePartsStock.product_name.like(f'%{product_name}%'))
        return query.all()

    def get_products(self, product_name: str | None = None) -> list[SparePartsStock]:
        query = self.db.query(SparePartsStock)
        if product_name:
            query = query.filter(SparePartsStock.product_name.like(f'%{product_name}%'))
        return query.order_by(SparePartsStock.product_name.asc()).all()

    def upsert_stock(self, product_name: str, brand: str, model: str, unit: str, quantity: int) -> SparePartsStock:
        stock = self.find_by_product(product_name, brand, model)
        if stock:
            stock.stock += quantity
        else:
            stock = SparePartsStock(
                product_name=product_name,
                brand=brand,
                model=model,
                unit=unit,
                stock=quantity
            )
            self.db.add(stock)
        return stock

    def adjust_stock(self, product_name: str, brand: str, model: str, quantity_diff: int) -> SparePartsStock | None:
        stock = self.find_by_product(product_name, brand, model)
        if stock:
            stock.stock += quantity_diff
            if stock.stock < 0:
                stock.stock = 0
        return stock


class SparePartsInboundRepository(BaseRepository[SparePartsInbound]):
    def __init__(self, db: Session):
        super().__init__(db, SparePartsInbound)

    def search_inbound_records(self, product: str | None = None, user: str | None = None,
                               page: int = 0, page_size: int = 10) -> tuple[list[SparePartsInbound], int]:
        query = self.db.query(SparePartsInbound)
        if product:
            query = query.filter(SparePartsInbound.product_name.like(f'%{product}%'))
        if user:
            query = query.filter(SparePartsInbound.user_name.like(f'%{user}%'))
        total = query.count()
        items = query.order_by(SparePartsInbound.created_at.desc()).offset(page * page_size).limit(page_size).all()
        return items, total

from sqlalchemy import BigInteger, Column, DateTime, Index, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base
from app.models.mixins import SerializationMixin


class SparePartsStock(Base, SerializationMixin):
    __tablename__ = "spare_parts_stock"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    product_id = Column(String(50), comment="产品编号")
    product_name = Column(String(200), nullable=False, comment="产品名称")
    brand = Column(String(100), comment="品牌")
    model = Column(String(100), comment="产品型号")
    category = Column(String(50), comment="分类")
    unit = Column(String(20), nullable=False, default="件", comment="单位")
    stock = Column(Integer, nullable=False, default=0, comment="库存数量")
    quantity = Column(Integer, nullable=False, default=0, comment="数量")
    min_stock = Column(Integer, default=5, comment="最低库存预警")
    location = Column(String(100), comment="存放位置")
    status = Column(String(20), nullable=False, default="在库", comment="状态：在库/已使用/缺货")
    remark = Column(Text, comment="备注")
    created_at = Column(DateTime, server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")

    usages = relationship("SparePartsUsage", back_populates="stock", passive_deletes=True)

    __table_args__ = (
        Index('idx_product_name_brand_model', 'product_name', 'brand', 'model'),
        Index('idx_spare_parts_status', 'status'),
        {'comment': '备品备件库存表'}
    )

    def to_dict(self):
        return {
            'id': self.id,
            'productId': self.product_id or '',
            'productName': self.product_name,
            'brand': self.brand or '',
            'model': self.model or '',
            'category': self.category or '',
            'unit': self.unit,
            'stock': self.stock,
            'quantity': self.quantity or 0,
            'minStock': self.min_stock or 5,
            'location': self.location or '',
            'status': self.status,
            'remark': self.remark or '',
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None
        }

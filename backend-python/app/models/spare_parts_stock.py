from sqlalchemy import Column, BigInteger, String, Integer, Index, DateTime
from sqlalchemy.sql import func
from app.database import Base


class SparePartsStock(Base):
    __tablename__ = "spare_parts_stock"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    product_name = Column(String(200), nullable=False, comment="产品名称")
    brand = Column(String(100), comment="品牌")
    model = Column(String(100), comment="产品型号")
    unit = Column(String(20), nullable=False, default="件", comment="单位")
    quantity = Column(Integer, nullable=False, default=0, comment="库存数量")
    status = Column(String(20), nullable=False, default="在库", comment="状态：在库/已使用/缺货")
    created_at = Column(DateTime, server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")
    
    __table_args__ = (
        Index('idx_product_name_brand_model', 'product_name', 'brand', 'model'),
        Index('idx_spare_parts_status', 'status'),
        {'comment': '备品备件库存表'}
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'productName': self.product_name,
            'brand': self.brand or '',
            'model': self.model or '',
            'unit': self.unit,
            'quantity': self.quantity,
            'status': self.status,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None
        }

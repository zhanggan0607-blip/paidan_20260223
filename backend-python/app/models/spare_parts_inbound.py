from sqlalchemy import Column, BigInteger, String, DateTime, Integer, Index
from sqlalchemy.sql import func
from app.database import Base


class SparePartsInbound(Base):
    __tablename__ = "spare_parts_inbound"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    inbound_no = Column(String(50), unique=True, nullable=False, comment="入库单号")
    product_name = Column(String(200), nullable=False, comment="产品名称")
    brand = Column(String(100), comment="品牌")
    model = Column(String(100), comment="产品型号")
    quantity = Column(Integer, nullable=False, comment="入库数量")
    supplier = Column(String(200), comment="供应商")
    unit = Column(String(20), nullable=False, default="件", comment="单位")
    user_name = Column(String(100), nullable=False, comment="入库人")
    remarks = Column(String(500), comment="备注")
    created_at = Column(DateTime, server_default=func.now(), nullable=False, comment="入库时间")
    
    __table_args__ = (
        Index('idx_inbound_no', 'inbound_no'),
        Index('idx_product_name', 'product_name'),
        Index('idx_user_name', 'user_name'),
        Index('idx_created_at', 'created_at'),
        {'comment': '备品备件入库记录表'}
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'inboundNo': self.inbound_no,
            'productName': self.product_name,
            'brand': self.brand or '',
            'model': self.model or '',
            'quantity': self.quantity,
            'supplier': self.supplier or '',
            'unit': self.unit,
            'userName': self.user_name,
            'remarks': self.remarks or '',
            'inboundTime': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else ''
        }

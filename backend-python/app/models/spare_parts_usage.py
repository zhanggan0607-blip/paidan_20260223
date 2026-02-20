from sqlalchemy import Column, BigInteger, String, Integer, DateTime, Index, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class SparePartsUsage(Base):
    __tablename__ = "spare_parts_usage"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    product_name = Column(String(200), nullable=False, comment="产品名称")
    brand = Column(String(100), comment="品牌")
    model = Column(String(100), comment="产品型号")
    quantity = Column(Integer, nullable=False, comment="领用数量")
    user_name = Column(String(100), nullable=False, comment="运维人员员")
    issue_time = Column(DateTime, nullable=False, comment="领用时间")
    unit = Column(String(20), nullable=False, default="件", comment="单位")
    project_id = Column(String(50), comment="项目编号")
    project_name = Column(String(200), comment="项目名称")
    stock_id = Column(BigInteger, ForeignKey('spare_parts_stock.id', ondelete='SET NULL'), comment="库存记录ID")
    status = Column(String(20), nullable=False, default="已使用", comment="状态：已使用")
    created_at = Column(DateTime, server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")
    
    stock = relationship("SparePartsStock", back_populates="usages")
    
    __table_args__ = (
        Index('idx_usage_product_name', 'product_name'),
        Index('idx_usage_user_name', 'user_name'),
        Index('idx_usage_project_name', 'project_name'),
        Index('idx_usage_issue_time', 'issue_time'),
        Index('idx_usage_status', 'status'),
        Index('idx_usage_stock_id', 'stock_id'),
        {'comment': '备品备件领用表'}
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'product_name': self.product_name,
            'brand': self.brand or '',
            'model': self.model or '',
            'quantity': self.quantity,
            'user_name': self.user_name,
            'issue_time': self.issue_time.strftime('%Y-%m-%d %H:%M:%S') if self.issue_time else '',
            'unit': self.unit,
            'project_id': self.project_id or '',
            'project_name': self.project_name or '',
            'stock_id': self.stock_id,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

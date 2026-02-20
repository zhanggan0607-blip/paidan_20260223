from sqlalchemy import Column, BigInteger, String, Integer, DateTime
from sqlalchemy.sql import func
from app.database import Base


class OperationType(Base):
    __tablename__ = "operation_type"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    type_code = Column(String(50), unique=True, nullable=False, comment="类型编码")
    type_name = Column(String(50), nullable=False, comment="类型名称")
    color_code = Column(String(20), comment="颜色代码(用于前端显示)")
    sort_order = Column(Integer, default=0, comment="排序顺序")
    is_active = Column(Integer, default=1, comment="是否启用: 1启用, 0禁用")
    created_at = Column(DateTime, server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")
    
    def to_dict(self):
        return {
            'id': self.id,
            'type_code': self.type_code,
            'type_name': self.type_name,
            'color_code': self.color_code,
            'sort_order': self.sort_order,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

from sqlalchemy import Column, BigInteger, String, Integer, Boolean, DateTime, Index
from sqlalchemy.sql import func
from app.database import Base


class Dictionary(Base):
    __tablename__ = "dictionary"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    dict_type = Column(String(50), nullable=False, comment="字典类型")
    dict_key = Column(String(50), nullable=False, comment="字典键")
    dict_value = Column(String(200), nullable=False, comment="字典值")
    dict_label = Column(String(200), nullable=False, comment="字典标签")
    sort_order = Column(Integer, default=0, comment="排序")
    is_active = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(DateTime, server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")
    
    __table_args__ = (
        Index('idx_dict_type', 'dict_type'),
        Index('idx_dict_key', 'dict_key'),
        Index('idx_dict_type_key', 'dict_type', 'dict_key'),
        {'comment': '字典表'}
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'dict_type': self.dict_type,
            'dict_key': self.dict_key,
            'dict_value': self.dict_value,
            'dict_label': self.dict_label,
            'sort_order': self.sort_order,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

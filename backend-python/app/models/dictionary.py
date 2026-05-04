from sqlalchemy import BigInteger, Boolean, Column, DateTime, Index, Integer, String
from sqlalchemy.sql import func

from app.database import Base
from app.models.mixins import SerializationMixin


class Dictionary(Base, SerializationMixin):
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

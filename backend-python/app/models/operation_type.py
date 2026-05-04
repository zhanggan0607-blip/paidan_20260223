from sqlalchemy import BigInteger, Column, DateTime, Integer, String
from sqlalchemy.sql import func

from app.database import Base
from app.models.mixins import SerializationMixin


class OperationType(Base, SerializationMixin):
    __tablename__ = "operation_type"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    type_code = Column(String(50), unique=True, nullable=False, comment="类型编码")
    type_name = Column(String(50), nullable=False, comment="类型名称")
    color_code = Column(String(20), comment="颜色代码(用于前端显示)")
    sort_order = Column(Integer, default=0, comment="排序顺序")
    is_active = Column(Integer, default=1, comment="是否启用: 1启用, 0禁用")
    created_at = Column(DateTime, server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")

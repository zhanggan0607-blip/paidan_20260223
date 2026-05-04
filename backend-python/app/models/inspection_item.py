from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base
from app.models.mixins import SerializationMixin


class InspectionItem(Base, SerializationMixin):
    __tablename__ = 'inspection_item'

    id = Column(Integer, primary_key=True, index=True)
    item_code = Column(String(50), unique=True, nullable=False, index=True, comment='事项编码')
    item_name = Column(String(200), nullable=False, index=True, comment='事项名称')
    item_type = Column(String(50), nullable=False, comment='事项类型')
    level = Column(Integer, default=1, comment='层级: 1-项目类型, 2-系统类型, 3-检查项')
    parent_id = Column(Integer, ForeignKey('inspection_item.id'), nullable=True, comment='父节点ID')
    check_content = Column(Text, comment='检查内容')
    check_standard = Column(Text, comment='检查标准')
    sort_order = Column(Integer, default=0, comment='排序')
    deleted_at = Column(DateTime(timezone=True), nullable=True, comment='删除时间')
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment='创建时间')
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment='更新时间')

    children = relationship("InspectionItem", backref="parent", remote_side=[id])

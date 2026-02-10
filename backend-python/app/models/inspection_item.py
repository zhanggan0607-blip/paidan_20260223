from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.database import Base

class InspectionItem(Base):
    __tablename__ = 'inspection_item'

    id = Column(Integer, primary_key=True, index=True)
    item_code = Column(String(50), unique=True, nullable=False, index=True, comment='事项编码')
    item_name = Column(String(200), nullable=False, index=True, comment='事项名称')
    item_type = Column(String(50), nullable=False, comment='事项类型')
    check_content = Column(Text, comment='检查内容')
    check_standard = Column(Text, comment='检查标准')
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment='创建时间')
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment='更新时间')

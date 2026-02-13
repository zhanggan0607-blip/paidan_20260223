from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.database import Base

class Customer(Base):
    __tablename__ = "customer"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False, comment="客户单位")
    address = Column(String(200), nullable=True, comment="客户地址")
    contact_person = Column(String(50), nullable=False, comment="客户联系人")
    phone = Column(String(20), nullable=False, comment="客户联系方式")
    contact_position = Column(String(50), nullable=True, comment="客户联系人职位")
    remarks = Column(Text, nullable=True, comment="备注")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class CustomerContact(Base):
    __tablename__ = "customer_contact"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customer.id", ondelete="CASCADE"), nullable=False, index=True, comment="客户ID")
    contact_person = Column(String(50), nullable=False, comment="联系人姓名")
    phone = Column(String(20), nullable=True, comment="联系方式")
    contact_position = Column(String(50), nullable=True, comment="联系人职位")
    remarks = Column(Text, nullable=True, comment="备注")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    customer = relationship("Customer", backref="contacts")

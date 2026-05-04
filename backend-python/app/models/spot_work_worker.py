from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base
from app.models.mixins import SerializationMixin


class SpotWorkWorker(Base, SerializationMixin):
    """
    施工人员信息
    """
    __tablename__ = "spot_work_worker"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    spot_work_id = Column(BigInteger, ForeignKey('spot_work.id', ondelete='CASCADE'), nullable=True, index=True, comment="关联用工单ID")
    project_id = Column(String(50), nullable=False, index=True, comment="项目编号")
    project_name = Column(String(200), comment="项目名称")
    start_date = Column(DateTime, comment="开始日期")
    end_date = Column(DateTime, comment="结束日期")
    name = Column(String(50), nullable=False, comment="姓名")
    gender = Column(String(10), comment="性别")
    birth_date = Column(String(20), comment="出生日期")
    address = Column(String(200), comment="住址")
    id_card_number = Column(String(18), comment="身份证号码")
    issuing_authority = Column(String(100), comment="签发机关")
    valid_period = Column(String(50), comment="有效期限")
    id_card_front = Column(String(500), comment="身份证正面照片URL")
    id_card_back = Column(String(500), comment="身份证反面照片URL")
    created_at = Column(DateTime, server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")

    spot_work = relationship("SpotWork", foreign_keys=[spot_work_id])

    __table_args__ = (
        Index('idx_worker_id_card_number', 'id_card_number'),
    )

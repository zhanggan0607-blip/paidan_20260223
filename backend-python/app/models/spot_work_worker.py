# -*- coding: utf-8 -*-
from sqlalchemy import Column, BigInteger, String, DateTime, Integer, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class SpotWorkWorker(Base):
    """
    施工人员信息
    """
    __tablename__ = "spot_work_worker"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
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
    
    def to_dict(self):
        return {
            'id': self.id,
            'spot_work_id': self.spot_work_id,
            'project_id': self.project_id,
            'project_name': self.project_name,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'name': self.name,
            'gender': self.gender,
            'birth_date': self.birth_date,
            'address': self.address,
            'id_card_number': self.id_card_number,
            'issuing_authority': self.issuing_authority,
            'valid_period': self.valid_period,
            'id_card_front': self.id_card_front,
            'id_card_back': self.id_card_back,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

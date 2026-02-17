from sqlalchemy import Column, BigInteger, String, DateTime, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime


class ProjectInfo(Base):
    __tablename__ = "project_info"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    project_id = Column(String(50), nullable=False, unique=True, comment="项目编号")
    project_name = Column(String(200), nullable=False, comment="项目名称")
    completion_date = Column(DateTime, nullable=False, comment="开始日期")
    maintenance_end_date = Column(DateTime, nullable=False, comment="结束日期")
    maintenance_period = Column(String(20), nullable=False, comment="维保频率")
    client_name = Column(String(100), nullable=False, comment="客户单位名称")
    address = Column(String(200), nullable=False, comment="客户地址")
    project_abbr = Column(String(10), comment="项目简称")
    project_manager = Column(String(50), comment="运维人员")
    client_contact = Column(String(50), comment="客户联系人")
    client_contact_position = Column(String(20), comment="客户联系人职位")
    client_contact_info = Column(String(50), comment="客户联系方式")
    created_at = Column(DateTime, comment="创建时间")
    updated_at = Column(DateTime, comment="更新时间")
    
    temporary_repairs = relationship("TemporaryRepair", back_populates="project", passive_deletes=True)
    spot_works = relationship("SpotWork", back_populates="project", passive_deletes=True)
    maintenance_plans = relationship("MaintenancePlan", back_populates="project", passive_deletes=True)
    periodic_inspections = relationship("PeriodicInspection", back_populates="project", passive_deletes=True)
    work_plans = relationship("WorkPlan", back_populates="project", passive_deletes=True)
    
    __table_args__ = (
        Index('idx_project_info_id', 'project_id'),
        Index('idx_project_info_client_name', 'client_name'),
        Index('idx_project_info_project_name', 'project_name'),
        {'comment': '项目信息表'}
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'project_name': self.project_name,
            'completion_date': self.completion_date.isoformat() if self.completion_date else None,
            'maintenance_end_date': self.maintenance_end_date.isoformat() if self.maintenance_end_date else None,
            'maintenance_period': self.maintenance_period,
            'client_name': self.client_name,
            'address': self.address,
            'project_abbr': self.project_abbr,
            'project_manager': self.project_manager,
            'client_contact': self.client_contact,
            'client_contact_position': self.client_contact_position,
            'client_contact_info': self.client_contact_info,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

from sqlalchemy import Column, BigInteger, String, DateTime, Integer, Index, ForeignKey, Text, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.mixins import SoftDeleteMixin


class SpotWork(Base, SoftDeleteMixin):
    __tablename__ = "spot_work"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    work_id = Column(String(50), unique=True, nullable=False, comment="用工单编号")
    plan_id = Column(String(50), ForeignKey('maintenance_plan.plan_id', ondelete='CASCADE'), nullable=True, index=True, comment="关联维保计划编号")
    project_id = Column(String(50), ForeignKey('project_info.project_id', ondelete='CASCADE'), nullable=False, comment="项目编号")
    project_name = Column(String(200), nullable=False, comment="项目名称")
    plan_start_date = Column(DateTime, nullable=False, comment="计划开始日期")
    plan_end_date = Column(DateTime, nullable=False, comment="计划结束日期")
    client_name = Column(String(100), comment="客户单位")
    client_contact = Column(String(100), comment="客户联系人")
    client_contact_info = Column(String(50), comment="客户联系电话")
    maintenance_personnel = Column(String(100), comment="运维人员")
    work_content = Column(Text, comment="工作内容")
    photos = Column(Text, comment="现场图片JSON数组")
    signature = Column(Text, comment="班组签字图片")
    status = Column(String(20), nullable=False, default="未进行", comment="状态")
    remarks = Column(String(500), comment="备注")
    actual_completion_date = Column(DateTime, comment="实际完成时间")
    created_at = Column(DateTime, server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")
    
    project = relationship("ProjectInfo", back_populates="spot_works")
    maintenance_plan = relationship("MaintenancePlan", back_populates="spot_works")
    
    __table_args__ = (
        Index('idx_spot_work_id', 'work_id'),
        Index('idx_spot_project_id', 'project_id'),
        Index('idx_spot_project_name', 'project_name'),
        Index('idx_spot_client_name', 'client_name'),
        Index('idx_spot_status', 'status'),
        Index('idx_spot_plan_start_date', 'plan_start_date'),
        Index('idx_spot_status_created', 'status', 'created_at'),
        Index('idx_spot_status_updated', 'status', 'updated_at'),
        {'comment': '零星用工单表'}
    )
    
    def to_dict(self):
        import json
        project_name = self.project_name
        client_name = self.client_name
        address = ''
        client_contact_position = ''
        if self.project:
            project_name = self.project.project_name or project_name
            client_name = self.project.client_name or client_name
            address = self.project.address or ''
            client_contact_position = self.project.client_contact_position or ''
        
        client_contact = self.client_contact or ''
        client_contact_info = self.client_contact_info or ''
        if not client_contact and self.project:
            client_contact = self.project.client_contact or ''
        if not client_contact_info and self.project:
            client_contact_info = self.project.client_contact_info or ''
        
        photos = []
        if self.photos:
            try:
                photos = json.loads(self.photos)
            except:
                photos = []
        
        return {
            'id': self.id,
            'work_id': self.work_id,
            'plan_id': self.plan_id,
            'project_id': self.project_id,
            'project_name': project_name,
            'plan_start_date': self.plan_start_date.isoformat() if self.plan_start_date else None,
            'plan_end_date': self.plan_end_date.isoformat() if self.plan_end_date else None,
            'client_name': client_name,
            'client_contact': client_contact,
            'client_contact_info': client_contact_info,
            'address': address,
            'client_contact_position': client_contact_position,
            'maintenance_personnel': self.maintenance_personnel,
            'work_content': self.work_content,
            'photos': photos,
            'signature': self.signature,
            'status': self.status,
            'remarks': self.remarks,
            'actual_completion_date': self.actual_completion_date.isoformat() if self.actual_completion_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

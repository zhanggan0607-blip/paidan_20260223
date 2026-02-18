from sqlalchemy import Column, BigInteger, String, DateTime, Integer, Index, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class WorkPlan(Base):
    __tablename__ = "work_plan"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    plan_id = Column(String(50), unique=True, nullable=False, comment="计划编号")
    plan_type = Column(String(20), nullable=False, comment="工单类型：定期巡检/临时维修/零星用工")
    project_id = Column(String(50), ForeignKey('project_info.project_id', ondelete='CASCADE'), nullable=False, comment="项目编号")
    project_name = Column(String(200), nullable=False, comment="项目名称")
    plan_start_date = Column(DateTime, nullable=False, comment="计划开始日期")
    plan_end_date = Column(DateTime, nullable=False, comment="计划结束日期")
    client_name = Column(String(100), comment="客户单位")
    maintenance_personnel = Column(String(100), comment="运维人员")
    status = Column(String(20), nullable=False, default="未进行", comment="状态")
    filled_count = Column(Integer, default=0, comment="已填写检查项数量")
    total_count = Column(Integer, default=5, comment="检查项总数量")
    remarks = Column(Text, comment="备注")
    created_at = Column(DateTime, server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")
    
    project = relationship("ProjectInfo", back_populates="work_plans")
    
    __table_args__ = (
        Index('idx_work_plan_id', 'plan_id'),
        Index('idx_work_plan_type', 'plan_type'),
        Index('idx_work_plan_project_id', 'project_id'),
        Index('idx_work_plan_project_name', 'project_name'),
        Index('idx_work_plan_client_name', 'client_name'),
        Index('idx_work_plan_status', 'status'),
        Index('idx_work_plan_start_date', 'plan_start_date'),
        {'comment': '工作计划表（统一管理定期巡检、临时维修、零星用工）'}
    )
    
    def to_dict(self):
        project_name = self.project_name
        client_name = self.client_name
        client_contact = ''
        client_contact_info = ''
        address = ''
        client_contact_position = ''
        if self.project:
            project_name = self.project.project_name or project_name
            client_name = self.project.client_name or client_name
            client_contact = self.project.client_contact or ''
            client_contact_info = self.project.client_contact_info or ''
            address = self.project.address or ''
            client_contact_position = self.project.client_contact_position or ''
        
        return {
            'id': self.id,
            'plan_id': self.plan_id,
            'plan_type': self.plan_type,
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
            'status': self.status,
            'filled_count': self.filled_count or 0,
            'total_count': self.total_count or 5,
            'remarks': self.remarks,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

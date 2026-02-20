from sqlalchemy import Column, BigInteger, String, DateTime, Integer, Index, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class PeriodicInspection(Base):
    __tablename__ = "periodic_inspection"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    inspection_id = Column(String(50), unique=True, nullable=False, comment="工单编号")
    plan_id = Column(String(50), ForeignKey('maintenance_plan.plan_id', ondelete='CASCADE'), nullable=True, index=True, comment="关联维保计划编号")
    project_id = Column(String(50), ForeignKey('project_info.project_id', ondelete='CASCADE'), nullable=False, comment="项目编号")
    project_name = Column(String(200), nullable=False, comment="项目名称")
    plan_start_date = Column(DateTime, nullable=False, comment="计划开始日期")
    plan_end_date = Column(DateTime, nullable=False, comment="计划结束日期")
    client_name = Column(String(100), comment="客户单位")
    maintenance_personnel = Column(String(100), comment="运维人员")
    status = Column(String(20), nullable=False, default="未进行", comment="状态")
    filled_count = Column(Integer, default=0, comment="已填写检查项数量")
    total_count = Column(Integer, default=5, comment="检查项总数量")
    execution_result = Column(Text, comment="发现问题")
    remarks = Column(String(500), comment="处理结果")
    signature = Column(Text, comment="用户签名(base64)")
    actual_completion_date = Column(DateTime, comment="实际完成时间")
    created_at = Column(DateTime, server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")
    
    project = relationship("ProjectInfo", back_populates="periodic_inspections")
    maintenance_plan = relationship("MaintenancePlan", back_populates="periodic_inspections")
    
    __table_args__ = (
        Index('idx_periodic_inspection_id', 'inspection_id'),
        Index('idx_periodic_project_id', 'project_id'),
        Index('idx_periodic_project_name', 'project_name'),
        Index('idx_periodic_client_name', 'client_name'),
        Index('idx_periodic_status', 'status'),
        Index('idx_periodic_plan_start_date', 'plan_start_date'),
        {'comment': '定期巡检单表'}
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
            'inspection_id': self.inspection_id,
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
            'status': self.status,
            'filled_count': self.filled_count or 0,
            'total_count': self.total_count or 5,
            'execution_result': self.execution_result,
            'remarks': self.remarks,
            'signature': self.signature,
            'actual_completion_date': self.actual_completion_date.isoformat() if self.actual_completion_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

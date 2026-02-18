from sqlalchemy import Column, BigInteger, String, DateTime, Text, Integer, Float, Index, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class MaintenancePlan(Base):
    __tablename__ = "maintenance_plan"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    plan_id = Column(String(50), nullable=False, unique=True, comment="计划编号")
    plan_name = Column(String(200), nullable=False, comment="计划名称")
    project_id = Column(String(50), ForeignKey('project_info.project_id', ondelete='CASCADE'), nullable=False, comment="关联项目编号")
    project_name = Column(String(200), comment="项目名称")
    plan_type = Column(String(20), nullable=False, comment="工单类型")
    equipment_id = Column(String(50), nullable=False, comment="设备编号")
    equipment_name = Column(String(200), nullable=False, comment="设备名称")
    equipment_model = Column(String(100), comment="设备型号")
    equipment_location = Column(String(200), comment="设备位置")
    plan_start_date = Column(DateTime, nullable=False, comment="计划开始日期")
    plan_end_date = Column(DateTime, nullable=False, comment="计划结束日期")
    execution_date = Column(DateTime, comment="执行日期")
    next_maintenance_date = Column(DateTime, comment="下次维保日期")
    responsible_person = Column(String(50), nullable=False, comment="负责人")
    responsible_department = Column(String(100), comment="负责部门")
    contact_info = Column(String(50), comment="联系方式")
    maintenance_content = Column(Text, nullable=False, comment="维保内容")
    maintenance_requirements = Column(Text, comment="维保要求")
    maintenance_standard = Column(Text, comment="维保标准")
    plan_status = Column(String(20), nullable=False, comment="计划状态")
    execution_status = Column(String(20), nullable=False, comment="执行状态")
    completion_rate = Column(Integer, default=0, comment="完成率")
    remarks = Column(Text, comment="备注")
    inspection_items = Column(Text, comment="巡查项数据(JSON格式)")
    created_at = Column(DateTime, server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")
    
    project = relationship("ProjectInfo", back_populates="maintenance_plans")
    periodic_inspections = relationship("PeriodicInspection", back_populates="maintenance_plan", passive_deletes=True)
    temporary_repairs = relationship("TemporaryRepair", back_populates="maintenance_plan", passive_deletes=True)
    spot_works = relationship("SpotWork", back_populates="maintenance_plan", passive_deletes=True)
    
    __table_args__ = (
        Index('idx_maintenance_plan_id', 'plan_id'),
        Index('idx_maintenance_project_id', 'project_id'),
        Index('idx_maintenance_equipment_id', 'equipment_id'),
        Index('idx_maintenance_plan_status', 'plan_status'),
        Index('idx_maintenance_execution_status', 'execution_status'),
        Index('idx_maintenance_execution_date', 'execution_date'),
        {'comment': '维保计划表'}
    )
    
    def to_dict(self):
        project_name = self.project_name
        client_name = ''
        address = ''
        if self.project:
            project_name = self.project.project_name or project_name
            client_name = self.project.client_name or ''
            address = self.project.address or ''
        
        return {
            'id': self.id,
            'plan_id': self.plan_id,
            'plan_name': self.plan_name,
            'project_id': self.project_id,
            'project_name': project_name or '',
            'client_name': client_name,
            'address': address,
            'plan_type': self.plan_type,
            'equipment_id': self.equipment_id,
            'equipment_name': self.equipment_name,
            'equipment_model': self.equipment_model,
            'equipment_location': self.equipment_location,
            'plan_start_date': self.plan_start_date.isoformat() if self.plan_start_date else None,
            'plan_end_date': self.plan_end_date.isoformat() if self.plan_end_date else None,
            'execution_date': self.execution_date.isoformat() if self.execution_date else None,
            'next_maintenance_date': self.next_maintenance_date.isoformat() if self.next_maintenance_date else None,
            'responsible_person': self.responsible_person,
            'responsible_department': self.responsible_department,
            'contact_info': self.contact_info,
            'maintenance_content': self.maintenance_content,
            'maintenance_requirements': self.maintenance_requirements,
            'maintenance_standard': self.maintenance_standard,
            'plan_status': self.plan_status,
            'execution_status': self.execution_status,
            'completion_rate': self.completion_rate,
            'remarks': self.remarks,
            'inspection_items': self.inspection_items,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

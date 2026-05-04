from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base
from app.models.mixins import SoftDeleteMixin, SerializationMixin


class MaintenancePlan(Base, SoftDeleteMixin, SerializationMixin):
    __tablename__ = "maintenance_plan"

    _relation_overrides = {
        'project_name': ('project', 'project_name'),
    }
    _relation_extras = {
        'client_name': ('project', 'client_name'),
        'client_contact': ('project', 'client_contact'),
        'client_contact_info': ('project', 'client_contact_info'),
        'address': ('project', 'address'),
        'client_contact_position': ('project', 'client_contact_position'),
    }

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
    maintenance_personnel = Column(String(100), comment="运维人员")
    responsible_person = Column(String(100), comment="负责人")
    responsible_department = Column(String(100), comment="负责部门")
    contact_info = Column(String(50), comment="联系方式")
    maintenance_content = Column(Text, nullable=False, comment="维保内容")
    maintenance_requirements = Column(Text, comment="维保要求")
    maintenance_standard = Column(Text, comment="维保标准")
    plan_status = Column(String(20), nullable=False, comment="计划状态")
    execution_status = Column(String(20), comment="执行状态")
    status = Column(String(20), nullable=False, default="执行中", comment="执行状态")
    completion_rate = Column(Integer, default=0, comment="完成率")
    filled_count = Column(Integer, default=0, comment="已填写检查项数量")
    total_count = Column(Integer, default=5, comment="检查项总数量")
    remarks = Column(Text, comment="备注")
    inspection_items = Column(JSONB, default=list, comment="巡查项数据(JSON格式)")
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
        Index('idx_maintenance_status', 'status'),
        Index('idx_maintenance_execution_date', 'execution_date'),
        Index('idx_maintenance_personnel', 'maintenance_personnel'),
        {'comment': '维保计划表'}
    )

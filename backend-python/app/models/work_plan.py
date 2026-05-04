from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base
from app.models.mixins import SoftDeleteMixin, SerializationMixin


class WorkPlan(Base, SoftDeleteMixin, SerializationMixin):
    __tablename__ = "work_plan"

    _relation_overrides = {
        'project_name': ('project', 'project_name'),
        'client_name': ('project', 'client_name'),
    }
    _relation_extras = {
        'client_contact': ('project', 'client_contact'),
        'client_contact_info': ('project', 'client_contact_info'),
        'address': ('project', 'address'),
        'client_contact_position': ('project', 'client_contact_position'),
    }

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    plan_id = Column(String(50), unique=True, nullable=False, comment="计划编号")
    plan_name = Column(String(200), comment="计划名称")
    plan_type = Column(String(20), nullable=False, comment="工单类型：定期巡检/临时维修/零星用工")
    project_id = Column(String(50), ForeignKey('project_info.project_id', ondelete='CASCADE'), nullable=False, comment="项目编号")
    project_name = Column(String(200), nullable=False, comment="项目名称")
    plan_start_date = Column(DateTime, nullable=False, comment="计划开始日期")
    plan_end_date = Column(DateTime, nullable=False, comment="计划结束日期")
    client_name = Column(String(100), comment="客户单位")
    maintenance_personnel = Column(String(100), comment="运维人员")
    status = Column(String(20), nullable=False, default="执行中", comment="状态")
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
        Index('idx_work_plan_project_status', 'project_name', 'status'),
        Index('idx_work_plan_type_status', 'plan_type', 'status'),
        Index('idx_work_plan_created_status', 'created_at', 'status'),
        {'comment': '工作计划表（统一管理定期巡检、临时维修、零星用工）'}
    )

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base
from app.models.mixins import SoftDeleteMixin, SerializationMixin


class PeriodicInspection(Base, SoftDeleteMixin, SerializationMixin):
    __tablename__ = "periodic_inspection"

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
    inspection_id = Column(String(50), unique=True, nullable=False, comment="工单编号")
    plan_id = Column(String(50), ForeignKey('maintenance_plan.plan_id', ondelete='CASCADE'), nullable=True, index=True, comment="关联维保计划编号")
    project_id = Column(String(50), ForeignKey('project_info.project_id', ondelete='CASCADE'), nullable=False, comment="项目编号")
    project_name = Column(String(200), nullable=False, comment="项目名称")
    plan_start_date = Column(DateTime, nullable=False, comment="计划开始日期")
    plan_end_date = Column(DateTime, nullable=False, comment="计划结束日期")
    client_name = Column(String(100), comment="客户单位")
    maintenance_personnel = Column(String(100), comment="运维人员")
    status = Column(String(20), nullable=False, default="执行中", comment="状态")
    filled_count = Column(Integer, default=0, comment="已填写检查项数量")
    total_count = Column(Integer, default=5, comment="检查项总数量")
    inspection_item_ids = Column(String(500), comment="巡检项ID列表")
    execution_result = Column(Text, comment="发现问题")
    remarks = Column(String(500), comment="处理结果")
    signature = Column(Text, comment="用户签名(base64)")
    actual_completion_date = Column(DateTime, comment="实际完成时间")
    reject_reason = Column(String(500), comment="退回原因")
    created_at = Column(DateTime, server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")

    project = relationship("ProjectInfo", back_populates="periodic_inspections")
    maintenance_plan = relationship("MaintenancePlan", back_populates="periodic_inspections")

    _list_exclude_fields = {'signature', 'reject_reason'}

    def to_list_dict(self) -> dict:
        return self.to_dict(exclude=self._list_exclude_fields)

    __table_args__ = (
        Index('idx_periodic_inspection_id', 'inspection_id'),
        Index('idx_periodic_project_id', 'project_id'),
        Index('idx_periodic_project_name', 'project_name'),
        Index('idx_periodic_client_name', 'client_name'),
        Index('idx_periodic_status', 'status'),
        Index('idx_periodic_plan_start_date', 'plan_start_date'),
        {'comment': '定期巡检单表'}
    )

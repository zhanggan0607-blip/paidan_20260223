from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base
from app.models.mixins import SoftDeleteMixin, SerializationMixin


class TemporaryRepair(Base, SoftDeleteMixin, SerializationMixin):
    __tablename__ = "temporary_repair"

    _relation_overrides = {
        'project_name': ('project', 'project_name'),
        'client_name': ('project', 'client_name'),
    }
    _relation_extras = {
        'address': ('project', 'address'),
        'client_contact_position': ('project', 'client_contact_position'),
    }

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    repair_id = Column(String(50), unique=True, nullable=False, comment="维修单编号")
    plan_id = Column(String(50), ForeignKey('maintenance_plan.plan_id', ondelete='CASCADE'), nullable=True, index=True, comment="关联维保计划编号")
    project_id = Column(String(50), ForeignKey('project_info.project_id', ondelete='CASCADE'), nullable=False, comment="项目编号")
    project_name = Column(String(200), nullable=False, comment="项目名称")
    plan_start_date = Column(DateTime, nullable=False, comment="计划开始日期")
    plan_end_date = Column(DateTime, nullable=False, comment="计划结束日期")
    client_name = Column(String(100), comment="客户单位")
    client_contact = Column(String(100), comment="客户联系人")
    client_contact_info = Column(String(50), comment="客户联系电话")
    maintenance_personnel = Column(String(100), comment="运维人员")
    created_by = Column(String(100), comment="创建人")
    status = Column(String(20), nullable=False, default="执行中", comment="状态")
    remarks = Column(String(500), comment="备注")
    fault_description = Column(Text, comment="故障描述")
    solution = Column(Text, comment="解决方案")
    photos = Column(JSONB, default=list, comment="现场图片JSON数组")
    signature = Column(Text, comment="用户签字Base64")
    customer_signature = Column(Text, comment="客户签字Base64")
    execution_date = Column(DateTime, comment="执行日期")
    actual_completion_date = Column(DateTime, comment="实际完成时间")
    reject_reason = Column(String(500), comment="退回原因")
    created_at = Column(DateTime, server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")

    project = relationship("ProjectInfo", back_populates="temporary_repairs")
    maintenance_plan = relationship("MaintenancePlan", back_populates="temporary_repairs")

    _list_exclude_fields = {'photos', 'signature', 'customer_signature', 'reject_reason'}

    def to_list_dict(self) -> dict:
        return self.to_dict(exclude=self._list_exclude_fields)

    __table_args__ = (
        Index('idx_temp_repair_id', 'repair_id'),
        Index('idx_temp_project_id', 'project_id'),
        Index('idx_temp_project_name', 'project_name'),
        Index('idx_temp_client_name', 'client_name'),
        Index('idx_temp_status', 'status'),
        Index('idx_temp_plan_start_date', 'plan_start_date'),
        Index('idx_temp_project_status', 'project_name', 'status'),
        Index('idx_temp_created_status', 'created_at', 'status'),
        Index('idx_temp_created_by', 'created_by'),
        {'comment': '临时维修单表'}
    )

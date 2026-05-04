from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base
from app.models.mixins import SoftDeleteMixin, SerializationMixin


class MaintenanceLog(Base, SoftDeleteMixin, SerializationMixin):
    __tablename__ = "maintenance_log"

    _date_only_fields = {'log_date'}

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    log_id = Column(String(50), unique=True, nullable=False, comment="日志编号")
    project_id = Column(String(50), ForeignKey('project_info.project_id', ondelete='CASCADE'), nullable=True, comment="项目编号")
    project_name = Column(String(200), nullable=True, comment="项目名称")
    log_type = Column(String(20), nullable=False, default="maintenance", comment="日志类型: maintenance维修日志")
    log_date = Column(DateTime, nullable=False, comment="日志日期")
    work_content = Column(Text, comment="工作内容")
    images = Column(JSONB, default=list, comment="现场照片JSON数组")
    remark = Column(String(500), comment="备注")
    status = Column(String(20), default="submitted", comment="状态: submitted已提交/rejected已退回")
    reject_reason = Column(String(500), comment="退回原因")
    created_by = Column(String(100), comment="创建人")
    created_at = Column(DateTime, server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")

    project = relationship("ProjectInfo", back_populates="maintenance_logs")

    __table_args__ = (
        Index('idx_maintenance_log_id', 'log_id'),
        Index('idx_maintenance_log_project_id', 'project_id'),
        Index('idx_maintenance_log_project_name', 'project_name'),
        Index('idx_maintenance_log_type', 'log_type'),
        Index('idx_maintenance_log_date', 'log_date'),
        Index('idx_maintenance_log_created_by', 'created_by'),
        Index('idx_maintenance_log_status', 'status'),
        {'comment': '维保日志表'}
    )

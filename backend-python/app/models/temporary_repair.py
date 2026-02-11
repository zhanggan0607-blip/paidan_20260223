from sqlalchemy import Column, BigInteger, String, DateTime, Integer, Index, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class TemporaryRepair(Base):
    __tablename__ = "temporary_repair"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    repair_id = Column(String(50), unique=True, nullable=False, comment="维修单编号")
    project_id = Column(String(50), ForeignKey('project_info.project_id'), nullable=False, comment="项目编号")
    project_name = Column(String(200), nullable=False, comment="项目名称")
    plan_start_date = Column(DateTime, nullable=False, comment="计划开始日期")
    plan_end_date = Column(DateTime, nullable=False, comment="计划结束日期")
    client_name = Column(String(100), comment="客户单位")
    maintenance_personnel = Column(String(100), comment="运维人员")
    status = Column(String(20), nullable=False, default="未进行", comment="状态")
    remarks = Column(String(500), comment="备注")
    created_at = Column(DateTime, server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")
    
    project = relationship("ProjectInfo", back_populates="temporary_repairs")
    
    __table_args__ = (
        Index('idx_temp_repair_id', 'repair_id'),
        Index('idx_temp_project_id', 'project_id'),
        Index('idx_temp_project_name', 'project_name'),
        Index('idx_temp_client_name', 'client_name'),
        Index('idx_temp_status', 'status'),
        Index('idx_temp_plan_start_date', 'plan_start_date'),
        {'comment': '临时维修单表'}
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'repair_id': self.repair_id,
            'project_id': self.project_id,
            'project_name': self.project_name,
            'plan_start_date': self.plan_start_date.isoformat() if self.plan_start_date else None,
            'plan_end_date': self.plan_end_date.isoformat() if self.plan_end_date else None,
            'client_name': self.client_name,
            'maintenance_personnel': self.maintenance_personnel,
            'status': self.status,
            'remarks': self.remarks,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

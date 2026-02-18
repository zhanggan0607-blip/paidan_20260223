from sqlalchemy import Column, BigInteger, String, DateTime, Text, Index, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class MaintenanceLog(Base):
    __tablename__ = "maintenance_log"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    log_id = Column(String(50), unique=True, nullable=False, comment="日志编号")
    project_id = Column(String(50), ForeignKey('project_info.project_id', ondelete='CASCADE'), nullable=False, comment="项目编号")
    project_name = Column(String(200), nullable=False, comment="项目名称")
    log_type = Column(String(20), nullable=False, default="periodic", comment="日志类型: periodic巡检/repair维修/spot用工")
    log_date = Column(DateTime, nullable=False, comment="日志日期")
    work_content = Column(Text, comment="工作内容")
    images = Column(Text, comment="现场照片JSON数组")
    remark = Column(String(500), comment="备注")
    created_by = Column(String(100), comment="创建人")
    is_deleted = Column(BigInteger, default=0, comment="是否删除: 0否/1是")
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
        {'comment': '维保日志表'}
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'log_id': self.log_id,
            'project_id': self.project_id,
            'project_name': self.project_name,
            'log_type': self.log_type,
            'log_date': self.log_date.strftime('%Y-%m-%d') if self.log_date else None,
            'work_content': self.work_content,
            'images': self.images,
            'remark': self.remark,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

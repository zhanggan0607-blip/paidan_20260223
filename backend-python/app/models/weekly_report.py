from sqlalchemy import Column, BigInteger, String, DateTime, Text, Index, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class WeeklyReport(Base):
    __tablename__ = "weekly_report"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    report_id = Column(String(50), unique=True, nullable=False, comment="周报编号")
    project_id = Column(String(50), ForeignKey('project_info.project_id', ondelete='SET NULL'), nullable=True, comment="项目编号")
    project_name = Column(String(200), nullable=True, comment="项目名称")
    week_start_date = Column(DateTime, nullable=True, comment="周开始日期")
    week_end_date = Column(DateTime, nullable=True, comment="周结束日期")
    report_date = Column(DateTime, nullable=False, comment="填报日期")
    work_summary = Column(Text, comment="本周工作总结")
    work_content = Column(Text, comment="具体工作内容JSON数组")
    next_week_plan = Column(Text, comment="下周工作计划")
    issues = Column(Text, comment="存在问题")
    suggestions = Column(Text, comment="建议措施")
    images = Column(Text, comment="现场照片JSON数组")
    manager_signature = Column(Text, comment="部门经理签字图片")
    manager_sign_time = Column(DateTime, comment="部门经理签字时间")
    status = Column(String(20), default="draft", comment="状态: draft草稿/submitted已提交/approved已审核/rejected已退回")
    approved_by = Column(String(100), comment="审核人")
    approved_at = Column(DateTime, comment="审核时间")
    reject_reason = Column(String(500), comment="退回原因")
    created_by = Column(String(100), comment="创建人")
    is_deleted = Column(BigInteger, default=0, comment="是否删除: 0否/1是")
    created_at = Column(DateTime, server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")

    project = relationship("ProjectInfo", back_populates="weekly_reports")

    __table_args__ = (
        Index('idx_weekly_report_id', 'report_id'),
        Index('idx_weekly_report_project_id', 'project_id'),
        Index('idx_weekly_report_project_name', 'project_name'),
        Index('idx_weekly_report_week_start', 'week_start_date'),
        Index('idx_weekly_report_week_end', 'week_end_date'),
        Index('idx_weekly_report_status', 'status'),
        Index('idx_weekly_report_created_by', 'created_by'),
        {'comment': '维保周报表'}
    )

    def to_dict(self):
        return {
            'id': self.id,
            'report_id': self.report_id,
            'project_id': self.project_id,
            'project_name': self.project_name,
            'week_start_date': self.week_start_date.strftime('%Y-%m-%d') if self.week_start_date else None,
            'week_end_date': self.week_end_date.strftime('%Y-%m-%d') if self.week_end_date else None,
            'report_date': self.report_date.strftime('%Y-%m-%d') if self.report_date else None,
            'work_summary': self.work_summary,
            'work_content': self.work_content,
            'next_week_plan': self.next_week_plan,
            'issues': self.issues,
            'suggestions': self.suggestions,
            'images': self.images,
            'manager_signature': self.manager_signature,
            'manager_sign_time': self.manager_sign_time.strftime('%Y-%m-%d %H:%M:%S') if self.manager_sign_time else None,
            'status': self.status,
            'approved_by': self.approved_by,
            'approved_at': self.approved_at.strftime('%Y-%m-%d %H:%M:%S') if self.approved_at else None,
            'reject_reason': self.reject_reason,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

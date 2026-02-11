from sqlalchemy import Column, BigInteger, String, JSON, DateTime, Index
from sqlalchemy.sql import func
from app.database import Base


class UserDashboardConfig(Base):
    __tablename__ = "user_dashboard_config"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    user_id = Column(String(100), nullable=False, comment="用户ID")
    dashboard_type = Column(String(50), nullable=False, comment="仪表板类型")
    config = Column(JSON, nullable=False, comment="配置数据")
    created_at = Column(DateTime, server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")
    
    __table_args__ = (
        Index('idx_user_dashboard', 'user_id', 'dashboard_type'),
        {'comment': '用户仪表板配置表'}
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'dashboard_type': self.dashboard_type,
            'config': self.config,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

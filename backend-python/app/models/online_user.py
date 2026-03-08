from sqlalchemy import BigInteger, Boolean, Column, DateTime, Index, String
from sqlalchemy.sql import func

from app.database import Base


class OnlineUser(Base):
    __tablename__ = "online_users"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    user_id = Column(BigInteger, nullable=False, index=True, comment="用户ID")
    user_name = Column(String(50), nullable=False, comment="用户姓名")
    department = Column(String(100), comment="所属部门")
    role = Column(String(20), comment="角色")
    login_time = Column(DateTime, nullable=False, comment="登录时间")
    last_activity = Column(DateTime, nullable=False, comment="最后活动时间")
    ip_address = Column(String(50), comment="IP地址")
    device_type = Column(String(20), default="h5", comment="设备类型(pc/h5)")
    is_active = Column(Boolean, default=True, comment="是否在线")
    created_at = Column(DateTime, server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")

    __table_args__ = (
        Index('idx_online_user_user_id', 'user_id'),
        Index('idx_online_user_is_active', 'is_active'),
        {'comment': '在线用户表'}
    )

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_name': self.user_name,
            'department': self.department,
            'role': self.role,
            'login_time': self.login_time.isoformat() if self.login_time else None,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None,
            'ip_address': self.ip_address,
            'device_type': self.device_type,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

"""
在线用户模型
用于追踪当前在线用户的实时状态
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from app.database import Base


class OnlineUser(Base):
    """
    在线用户表
    记录当前在线用户的实时状态信息
    """
    __tablename__ = "online_users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True, comment="用户ID")
    user_name = Column(String(50), nullable=False, comment="用户名")
    department = Column(String(100), nullable=True, comment="部门")
    role = Column(String(50), nullable=True, comment="角色")
    login_time = Column(DateTime, nullable=False, default=datetime.utcnow, comment="登录时间")
    last_activity = Column(DateTime, nullable=False, default=datetime.utcnow, comment="最后活动时间")
    ip_address = Column(String(50), nullable=True, comment="IP地址")
    device_type = Column(String(20), nullable=False, default="pc", comment="设备类型: pc/h5")
    is_active = Column(Boolean, default=True, comment="是否活跃")

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "user_name": self.user_name,
            "department": self.department,
            "role": self.role,
            "login_time": self.login_time.strftime("%Y-%m-%d %H:%M:%S") if self.login_time else None,
            "last_activity": self.last_activity.strftime("%Y-%m-%d %H:%M:%S") if self.last_activity else None,
            "ip_address": self.ip_address,
            "device_type": self.device_type,
            "is_active": self.is_active
        }

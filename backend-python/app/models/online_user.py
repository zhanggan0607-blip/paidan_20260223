from sqlalchemy import Boolean, Column, DateTime, Index, Integer, String

from app.database import Base
from app.models.mixins import SerializationMixin


class OnlineUser(Base, SerializationMixin):
    __tablename__ = "online_users"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    user_id = Column(Integer, nullable=False, index=True, comment="用户ID")
    user_name = Column(String(50), nullable=False, comment="用户姓名")
    department = Column(String(100), comment="所属部门")
    role = Column(String(20), comment="角色")
    login_time = Column(DateTime, nullable=False, comment="登录时间")
    last_activity = Column(DateTime, nullable=False, comment="最后活动时间")
    ip_address = Column(String(50), comment="IP地址")
    device_type = Column(String(20), default="h5", comment="设备类型(pc/h5)")
    is_active = Column(Boolean, default=True, comment="是否在线")

    __table_args__ = (
        Index('idx_online_user_user_id', 'user_id'),
        Index('idx_online_user_is_active', 'is_active'),
        {'comment': '在线用户表'}
    )

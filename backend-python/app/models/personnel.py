from sqlalchemy import BigInteger, Boolean, Column, DateTime, Index, String
from sqlalchemy.sql import func

from app.database import Base


class Personnel(Base):
    __tablename__ = "personnel"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    name = Column(String(50), nullable=False, comment="姓名")
    gender = Column(String(10), nullable=False, comment="性别")
    phone = Column(String(20), comment="联系电话")
    password_hash = Column(String(255), nullable=True, comment="密码哈希")
    must_change_password = Column(Boolean, default=True, comment="是否需要修改密码")
    department = Column(String(100), comment="所属部门")
    role = Column(String(20), nullable=False, default="运维人员", comment="角色")
    address = Column(String(200), comment="地址")
    remarks = Column(String(500), comment="备注")
    dingtalk_userid = Column(String(100), unique=True, nullable=True, index=True, comment="钉钉用户ID")
    dingtalk_unionid = Column(String(100), unique=True, nullable=True, comment="钉钉UnionID(已废弃)")
    dingtalk_avatar = Column(String(500), nullable=True, comment="钉钉头像URL(已废弃)")
    dingtalk_title = Column(String(100), nullable=True, comment="钉钉职位(已废弃)")
    is_synced = Column(Boolean, default=False, comment="是否从钉钉同步")
    last_login_at = Column(DateTime, nullable=True, comment="最后登录时间")
    created_at = Column(DateTime, server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")

    __table_args__ = (
        Index('idx_name', 'name'),
        Index('idx_department', 'department'),
        Index('idx_role', 'role'),
        Index('idx_dingtalk_userid', 'dingtalk_userid'),
        {'comment': '人员信息表'}
    )

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'gender': self.gender,
            'phone': self.phone,
            'department': self.department,
            'role': self.role,
            'address': self.address,
            'remarks': self.remarks,
            'dingtalk_userid': self.dingtalk_userid,
            'dingtalk_unionid': self.dingtalk_unionid,
            'dingtalk_avatar': self.dingtalk_avatar,
            'dingtalk_title': self.dingtalk_title,
            'is_synced': self.is_synced,
            'must_change_password': self.must_change_password,
            'last_login_at': self.last_login_at.strftime('%Y-%m-%d %H:%M:%S') if self.last_login_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

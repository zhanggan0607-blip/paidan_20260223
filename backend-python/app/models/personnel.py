from sqlalchemy import Column, BigInteger, String, DateTime, Integer, Index
from sqlalchemy.sql import func
from app.database import Base

class Personnel(Base):
    __tablename__ = "personnel"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    name = Column(String(50), nullable=False, comment="姓名")
    gender = Column(String(10), nullable=False, comment="性别")
    phone = Column(String(20), comment="联系电话")
    department = Column(String(100), comment="所属部门")
    role = Column(String(20), nullable=False, default="员工", comment="角色")
    address = Column(String(200), comment="地址")
    remarks = Column(String(500), comment="备注")
    created_at = Column(DateTime, server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")
    
    __table_args__ = (
        Index('idx_name', 'name'),
        Index('idx_department', 'department'),
        Index('idx_role', 'role'),
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
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

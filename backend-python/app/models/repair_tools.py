from sqlalchemy import Column, BigInteger, String, Integer, Index, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base


class RepairToolsStock(Base):
    __tablename__ = "repair_tools_stock"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    tool_id = Column(String(50), comment="工具编号")
    tool_name = Column(String(200), nullable=False, comment="工具名称")
    category = Column(String(50), comment="工具分类")
    specification = Column(String(200), comment="规格型号")
    unit = Column(String(20), nullable=False, default="个", comment="单位")
    stock = Column(Integer, nullable=False, default=0, comment="库存数量")
    min_stock = Column(Integer, default=5, comment="最低库存预警")
    location = Column(String(100), comment="存放位置")
    remark = Column(Text, comment="备注")
    created_at = Column(DateTime, server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")
    
    __table_args__ = (
        Index('idx_repair_tool_name', 'tool_name'),
        Index('idx_repair_tool_category', 'category'),
        {'comment': '维修工具库存表'}
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'tool_id': self.tool_id or f'TOOL{self.id:06d}',
            'tool_name': self.tool_name,
            'category': self.category or '',
            'specification': self.specification or '',
            'unit': self.unit,
            'stock': self.stock,
            'min_stock': self.min_stock or 5,
            'location': self.location or '',
            'remark': self.remark or '',
            'last_stock_time': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else '',
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class RepairToolsIssue(Base):
    __tablename__ = "repair_tools_issue"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    tool_id = Column(String(50), comment="工具编号")
    tool_name = Column(String(200), nullable=False, comment="工具名称")
    specification = Column(String(200), comment="规格型号")
    quantity = Column(Integer, nullable=False, comment="领用数量")
    return_quantity = Column(Integer, default=0, comment="归还数量")
    user_id = Column(BigInteger, comment="领用人ID")
    user_name = Column(String(100), nullable=False, comment="领用人姓名")
    issue_time = Column(DateTime, nullable=False, comment="领用时间")
    return_time = Column(DateTime, comment="归还时间")
    project_id = Column(BigInteger, comment="项目ID")
    project_name = Column(String(200), comment="项目名称")
    status = Column(String(20), default="已领用", comment="状态：已领用/已归还")
    remark = Column(Text, comment="备注")
    stock_id = Column(BigInteger, comment="库存记录ID")
    created_at = Column(DateTime, server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")
    
    __table_args__ = (
        Index('idx_repair_issue_tool_name', 'tool_name'),
        Index('idx_repair_issue_user_name', 'user_name'),
        Index('idx_repair_issue_status', 'status'),
        Index('idx_repair_issue_issue_time', 'issue_time'),
        {'comment': '维修工具领用表'}
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'tool_id': self.tool_id or '',
            'tool_name': self.tool_name,
            'specification': self.specification or '',
            'quantity': self.quantity,
            'return_quantity': self.return_quantity or 0,
            'issue_quantity': self.quantity,
            'user_id': self.user_id,
            'user_name': self.user_name,
            'issue_time': self.issue_time.strftime('%Y-%m-%d %H:%M:%S') if self.issue_time else '',
            'return_time': self.return_time.strftime('%Y-%m-%d %H:%M:%S') if self.return_time else None,
            'project_id': self.project_id,
            'project_name': self.project_name or '',
            'status': self.status,
            'remark': self.remark or '',
            'stock_id': self.stock_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

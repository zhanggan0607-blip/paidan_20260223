from sqlalchemy import Column, BigInteger, String, DateTime, Integer, Index, Text
from sqlalchemy.sql import func
from app.database import Base


class RepairToolsInbound(Base):
    __tablename__ = "repair_tools_inbound"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    inbound_no = Column(String(50), unique=True, nullable=False, comment="入库单号")
    tool_name = Column(String(200), nullable=False, comment="工具名称")
    tool_id = Column(String(50), comment="工具编号")
    category = Column(String(50), comment="工具分类")
    specification = Column(String(200), comment="规格型号")
    quantity = Column(Integer, nullable=False, comment="入库数量")
    unit = Column(String(20), nullable=False, default="个", comment="单位")
    supplier = Column(String(200), comment="供应商")
    location = Column(String(100), comment="存放位置")
    user_name = Column(String(100), nullable=False, comment="入库人")
    remark = Column(Text, comment="备注")
    created_at = Column(DateTime, server_default=func.now(), nullable=False, comment="入库时间")
    
    __table_args__ = (
        Index('idx_repair_tools_inbound_no', 'inbound_no'),
        Index('idx_repair_tools_inbound_tool_name', 'tool_name'),
        Index('idx_repair_tools_inbound_user_name', 'user_name'),
        Index('idx_repair_tools_inbound_created_at', 'created_at'),
        {'comment': '维修工具入库记录表'}
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'inboundNo': self.inbound_no,
            'toolName': self.tool_name,
            'toolId': self.tool_id or '',
            'category': self.category or '',
            'specification': self.specification or '',
            'quantity': self.quantity,
            'unit': self.unit,
            'supplier': self.supplier or '',
            'location': self.location or '',
            'userName': self.user_name,
            'remark': self.remark or '',
            'inboundTime': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else ''
        }

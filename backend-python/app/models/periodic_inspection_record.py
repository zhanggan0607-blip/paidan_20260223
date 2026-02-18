from sqlalchemy import Column, BigInteger, String, DateTime, Integer, Text, ForeignKey, Boolean, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class PeriodicInspectionRecord(Base):
    __tablename__ = "periodic_inspection_record"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    inspection_id = Column(String(50), ForeignKey('periodic_inspection.inspection_id', ondelete='CASCADE'), nullable=False, index=True, comment="巡检单编号")
    item_id = Column(String(50), nullable=False, comment="巡检项ID")
    item_name = Column(String(200), comment="巡检项名称")
    inspection_item = Column(String(200), comment="巡查项")
    inspection_content = Column(Text, comment="巡查内容")
    check_content = Column(Text, comment="检查要求")
    brief_description = Column(Text, comment="简要说明")
    equipment_name = Column(String(200), comment="设备名称")
    equipment_location = Column(String(200), comment="设备位置")
    inspected = Column(Boolean, default=False, comment="是否已处理")
    photos = Column(Text, comment="照片URL列表(JSON)")
    inspection_result = Column(Text, comment="巡检结果")
    created_at = Column(DateTime, server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")
    
    __table_args__ = (
        Index('idx_record_inspection_id', 'inspection_id'),
        Index('idx_record_item_id', 'item_id'),
        {'comment': '定期巡检记录表'}
    )
    
    def to_dict(self):
        import json
        photos = []
        if self.photos:
            try:
                photos = json.loads(self.photos)
            except:
                photos = []
        
        return {
            'id': self.id,
            'inspection_id': self.inspection_id,
            'item_id': self.item_id,
            'item_name': self.item_name,
            'inspection_item': self.inspection_item,
            'inspection_content': self.inspection_content,
            'check_content': self.check_content,
            'brief_description': self.brief_description,
            'equipment_name': self.equipment_name,
            'equipment_location': self.equipment_location,
            'inspected': self.inspected or False,
            'photos': photos,
            'photos_uploaded': len(photos) > 0,
            'inspection_result': self.inspection_result or '',
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

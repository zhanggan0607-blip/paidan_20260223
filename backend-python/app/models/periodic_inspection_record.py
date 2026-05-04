from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base
from app.models.mixins import SerializationMixin


class PeriodicInspectionRecord(Base, SerializationMixin):
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
    photos = Column(JSONB, default=list, comment="照片URL列表(JSON)")
    inspection_result = Column(Text, comment="巡检结果")
    created_at = Column(DateTime, server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")

    inspection = relationship("PeriodicInspection", foreign_keys=[inspection_id])

    __table_args__ = (
        Index('idx_record_inspection_id', 'inspection_id'),
        Index('idx_record_item_id', 'item_id'),
        {'comment': '定期巡检记录表'}
    )

    def to_dict(self, **kwargs):
        result = super().to_dict(**kwargs)
        photos = result.get('photos') or []
        result['photos_uploaded'] = len(photos) > 0
        return result

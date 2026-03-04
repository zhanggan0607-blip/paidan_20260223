"""
巡检记录Repository
提供巡检记录数据访问方法
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.periodic_inspection_record import PeriodicInspectionRecord
from app.repositories.base import BaseRepository
import logging

logger = logging.getLogger(__name__)


class PeriodicInspectionRecordRepository(BaseRepository[PeriodicInspectionRecord]):
    """
    巡检记录Repository
    继承BaseRepository，复用通用CRUD方法
    """
    
    def __init__(self, db: Session):
        super().__init__(db, PeriodicInspectionRecord)

    def find_by_inspection_id(self, inspection_id: str) -> List[PeriodicInspectionRecord]:
        """
        根据巡检单编号查询所有记录
        
        Args:
            inspection_id: 巡检单编号
            
        Returns:
            巡检记录列表
        """
        try:
            return self.db.query(PeriodicInspectionRecord).filter(
                PeriodicInspectionRecord.inspection_id == inspection_id
            ).all()
        except Exception as e:
            logger.error(f"查询巡检记录失败 (inspection_id={inspection_id}): {str(e)}")
            raise

    def find_by_inspection_id_and_item_id(
        self, 
        inspection_id: str, 
        item_id: str
    ) -> Optional[PeriodicInspectionRecord]:
        """
        根据巡检单编号和事项ID查询记录
        
        Args:
            inspection_id: 巡检单编号
            item_id: 事项ID
            
        Returns:
            巡检记录，未找到返回None
        """
        try:
            return self.db.query(PeriodicInspectionRecord).filter(
                PeriodicInspectionRecord.inspection_id == inspection_id,
                PeriodicInspectionRecord.item_id == item_id
            ).first()
        except Exception as e:
            logger.error(f"查询巡检记录失败 (inspection_id={inspection_id}, item_id={item_id}): {str(e)}")
            raise

    def delete_by_inspection_id(self, inspection_id: str) -> int:
        """
        删除指定巡检单的所有记录
        
        Args:
            inspection_id: 巡检单编号
            
        Returns:
            删除的记录数量
        """
        try:
            count = self.db.query(PeriodicInspectionRecord).filter(
                PeriodicInspectionRecord.inspection_id == inspection_id
            ).delete()
            self.db.commit()
            return count
        except Exception as e:
            self.db.rollback()
            logger.error(f"删除巡检记录失败 (inspection_id={inspection_id}): {str(e)}")
            raise

    def upsert(
        self, 
        inspection_id: str,
        item_id: str,
        item_name: Optional[str] = None,
        inspection_item: Optional[str] = None,
        inspection_content: Optional[str] = None,
        check_content: Optional[str] = None,
        brief_description: Optional[str] = None,
        equipment_name: Optional[str] = None,
        equipment_location: Optional[str] = None,
        inspected: bool = False,
        photos: Optional[str] = None,
        inspection_result: Optional[str] = None
    ) -> PeriodicInspectionRecord:
        """
        创建或更新巡检记录
        
        Args:
            inspection_id: 巡检单编号
            item_id: 事项ID
            其他参数: 记录字段
            
        Returns:
            创建或更新后的记录
        """
        try:
            existing = self.find_by_inspection_id_and_item_id(inspection_id, item_id)
            
            if existing:
                if item_name is not None:
                    existing.item_name = item_name
                if inspection_item is not None:
                    existing.inspection_item = inspection_item
                if inspection_content is not None:
                    existing.inspection_content = inspection_content
                if check_content is not None:
                    existing.check_content = check_content
                if brief_description is not None:
                    existing.brief_description = brief_description
                if equipment_name is not None:
                    existing.equipment_name = equipment_name
                if equipment_location is not None:
                    existing.equipment_location = equipment_location
                if inspected is not None:
                    existing.inspected = inspected
                if photos is not None:
                    existing.photos = photos
                if inspection_result is not None:
                    existing.inspection_result = inspection_result
                self.db.commit()
                self.db.refresh(existing)
                return existing
            else:
                record = PeriodicInspectionRecord(
                    inspection_id=inspection_id,
                    item_id=item_id,
                    item_name=item_name,
                    inspection_item=inspection_item,
                    inspection_content=inspection_content,
                    check_content=check_content,
                    brief_description=brief_description,
                    equipment_name=equipment_name,
                    equipment_location=equipment_location,
                    inspected=inspected,
                    photos=photos or '[]',
                    inspection_result=inspection_result
                )
                return self.create(record)
        except Exception as e:
            self.db.rollback()
            logger.error(f"创建或更新巡检记录失败: {str(e)}")
            raise

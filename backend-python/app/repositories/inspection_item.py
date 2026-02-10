from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from app.models.inspection_item import InspectionItem
from app.schemas.inspection_item import InspectionItemCreate, InspectionItemUpdate
import logging

logger = logging.getLogger(__name__)


class InspectionItemRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[InspectionItem]:
        try:
            return self.db.query(InspectionItem).order_by(InspectionItem.created_at.desc()).all()
        except Exception as e:
            logger.error(f"查询所有巡检事项失败: {str(e)}")
            raise

    def get_by_id(self, item_id: int) -> Optional[InspectionItem]:
        try:
            return self.db.query(InspectionItem).filter(InspectionItem.id == item_id).first()
        except Exception as e:
            logger.error(f"查询巡检事项失败 (id={item_id}): {str(e)}")
            raise

    def get_by_code(self, item_code: str) -> Optional[InspectionItem]:
        try:
            return self.db.query(InspectionItem).filter(InspectionItem.item_code == item_code).first()
        except Exception as e:
            logger.error(f"查询巡检事项失败 (code={item_code}): {str(e)}")
            raise

    def search(self, keyword: Optional[str] = None) -> List[InspectionItem]:
        try:
            query = self.db.query(InspectionItem)
            if keyword:
                search_pattern = f"%{keyword}%"
                query = query.filter(
                    or_(
                        InspectionItem.item_code.ilike(search_pattern),
                        InspectionItem.item_name.ilike(search_pattern)
                    )
                )
            return query.order_by(InspectionItem.created_at.desc()).all()
        except Exception as e:
            logger.error(f"搜索巡检事项失败: {str(e)}")
            raise

    def create(self, item_data: InspectionItemCreate) -> InspectionItem:
        try:
            db_item = InspectionItem(**item_data.model_dump())
            self.db.add(db_item)
            self.db.commit()
            self.db.refresh(db_item)
            return db_item
        except Exception as e:
            self.db.rollback()
            logger.error(f"创建巡检事项失败: {str(e)}")
            raise

    def update(self, item_id: int, item_data: InspectionItemUpdate) -> Optional[InspectionItem]:
        try:
            db_item = self.get_by_id(item_id)
            if not db_item:
                return None

            update_data = item_data.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_item, key, value)

            self.db.commit()
            self.db.refresh(db_item)
            return db_item
        except Exception as e:
            self.db.rollback()
            logger.error(f"更新巡检事项失败: {str(e)}")
            raise

    def delete(self, item_id: int) -> bool:
        try:
            db_item = self.get_by_id(item_id)
            if not db_item:
                return False

            self.db.delete(db_item)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"删除巡检事项失败: {str(e)}")
            raise

    def get_paginated(self, skip: int = 0, limit: int = 10) -> tuple[List[InspectionItem], int]:
        try:
            query = self.db.query(InspectionItem)
            total = query.count()
            items = query.offset(skip).limit(limit).all()
            return items, total
        except Exception as e:
            logger.error(f"查询巡检事项分页失败: {str(e)}")
            raise

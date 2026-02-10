from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from app.models.inspection_item import InspectionItem
from app.schemas.inspection_item import InspectionItemCreate, InspectionItemUpdate

class InspectionItemRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[InspectionItem]:
        return self.db.query(InspectionItem).order_by(InspectionItem.created_at.desc()).all()

    def get_by_id(self, item_id: int) -> Optional[InspectionItem]:
        return self.db.query(InspectionItem).filter(InspectionItem.id == item_id).first()

    def get_by_code(self, item_code: str) -> Optional[InspectionItem]:
        return self.db.query(InspectionItem).filter(InspectionItem.item_code == item_code).first()

    def search(self, keyword: Optional[str] = None) -> List[InspectionItem]:
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

    def create(self, item_data: InspectionItemCreate) -> InspectionItem:
        db_item = InspectionItem(**item_data.model_dump())
        self.db.add(db_item)
        self.db.commit()
        self.db.refresh(db_item)
        return db_item

    def update(self, item_id: int, item_data: InspectionItemUpdate) -> Optional[InspectionItem]:
        db_item = self.get_by_id(item_id)
        if not db_item:
            return None
        
        update_data = item_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_item, key, value)
        
        self.db.commit()
        self.db.refresh(db_item)
        return db_item

    def delete(self, item_id: int) -> bool:
        db_item = self.get_by_id(item_id)
        if not db_item:
            return False
        
        self.db.delete(db_item)
        self.db.commit()
        return True

    def get_paginated(self, skip: int = 0, limit: int = 10) -> tuple[List[InspectionItem], int]:
        query = self.db.query(InspectionItem)
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, total

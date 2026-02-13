from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.repositories.inspection_item import InspectionItemRepository
from app.schemas.inspection_item import InspectionItemCreate, InspectionItemUpdate, InspectionItem

class InspectionItemService:
    def __init__(self, db: Session):
        self.repository = InspectionItemRepository(db)

    def get_all_items(self) -> List[InspectionItem]:
        return self.repository.get_all()

    def get_item_by_id(self, item_id: int) -> Optional[InspectionItem]:
        return self.repository.get_by_id(item_id)

    def get_tree(self) -> List[Dict[str, Any]]:
        return self.repository.get_tree()

    def search_items(self, keyword: Optional[str] = None) -> List[InspectionItem]:
        return self.repository.search(keyword)

    def create_item(self, item_data: InspectionItemCreate) -> InspectionItem:
        existing_item = self.repository.get_by_code(item_data.item_code)
        if existing_item:
            raise ValueError(f"事项编码 '{item_data.item_code}' 已存在")
        return self.repository.create(item_data)

    def update_item(self, item_id: int, item_data: InspectionItemUpdate) -> Optional[InspectionItem]:
        if item_data.item_code:
            existing_item = self.repository.get_by_code(item_data.item_code)
            if existing_item and existing_item.id != item_id:
                raise ValueError(f"事项编码 '{item_data.item_code}' 已存在")
        return self.repository.update(item_id, item_data)

    def delete_item(self, item_id: int) -> bool:
        return self.repository.delete(item_id)

    def get_paginated_items(self, skip: int = 0, limit: int = 10) -> tuple[List[InspectionItem], int]:
        return self.repository.get_paginated(skip, limit)

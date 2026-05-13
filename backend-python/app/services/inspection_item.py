from typing import Any

from sqlalchemy.orm import Session

from app.repositories.inspection_item import InspectionItemRepository
from app.schemas.inspection_item import InspectionItem, InspectionItemCreate, InspectionItemUpdate
from app.services.base import BaseService


class InspectionItemService(BaseService):
    def __init__(self, db: Session):
        super().__init__(db)
        self.repository = InspectionItemRepository(db)

    def get_all_items(self) -> list[InspectionItem]:
        return self.repository.get_all()

    def get_item_by_id(self, item_id: int) -> InspectionItem | None:
        return self.repository.get_by_id(item_id)

    def get_tree(self) -> list[dict[str, Any]]:
        return self.repository.get_tree()

    def search_items(self, keyword: str | None = None) -> list[InspectionItem]:
        return self.repository.search(keyword)

    def create_item(self, item_data: InspectionItemCreate) -> InspectionItem:
        existing_item = self.repository.get_by_code(item_data.item_code)
        if existing_item:
            raise ValueError(f"事项编码 '{item_data.item_code}' 已存在")
        item = self.repository.create(item_data)
        self.commit()
        return item

    def update_item(self, item_id: int, item_data: InspectionItemUpdate) -> InspectionItem | None:
        if item_data.item_code:
            existing_item = self.repository.get_by_code(item_data.item_code)
            if existing_item and existing_item.id != item_id:
                raise ValueError(f"事项编码 '{item_data.item_code}' 已存在")
        item = self.repository.update(item_id, item_data)
        if item:
            self.commit()
        return item

    def delete_item(self, item_id: int) -> bool:
        result = self.repository.delete(item_id)
        if result:
            self.commit()
        return result

    def get_paginated_items(self, skip: int = 0, limit: int = 10) -> tuple[list[InspectionItem], int]:
        return self.repository.get_paginated(skip, limit)

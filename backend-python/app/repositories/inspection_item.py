from app.utils.logging_config import get_logger
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.inspection_item import InspectionItem
from app.schemas.inspection_item import InspectionItemCreate, InspectionItemUpdate

logger = get_logger(__name__)


class InspectionItemRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[InspectionItem]:
        try:
            return self.db.query(InspectionItem).filter(
                InspectionItem.deleted_at.is_(None)
            ).order_by(InspectionItem.sort_order, InspectionItem.created_at.desc()).all()
        except Exception as e:
            logger.error(f"查询所有巡检事项失败: {str(e)}")
            raise

    def get_by_id(self, item_id: int) -> InspectionItem | None:
        try:
            return self.db.query(InspectionItem).filter(InspectionItem.id == item_id).first()
        except Exception as e:
            logger.error(f"查询巡检事项失败 (id={item_id}): {str(e)}")
            raise

    def get_by_code(self, item_code: str, include_deleted: bool = False) -> InspectionItem | None:
        try:
            query = self.db.query(InspectionItem).filter(
                InspectionItem.item_code == item_code
            )
            if not include_deleted:
                query = query.filter(InspectionItem.deleted_at.is_(None))
            return query.first()
        except Exception as e:
            logger.error(f"查询巡检事项失败 (code={item_code}): {str(e)}")
            raise

    def get_children(self, parent_id: int) -> list[InspectionItem]:
        try:
            return self.db.query(InspectionItem).filter(
                InspectionItem.parent_id == parent_id,
                InspectionItem.deleted_at.is_(None)
            ).order_by(InspectionItem.sort_order, InspectionItem.created_at.desc()).all()
        except Exception as e:
            logger.error(f"查询子节点失败 (parent_id={parent_id}): {str(e)}")
            raise

    def get_root_items(self) -> list[InspectionItem]:
        try:
            return self.db.query(InspectionItem).filter(
                InspectionItem.parent_id.is_(None),
                InspectionItem.deleted_at.is_(None)
            ).order_by(InspectionItem.sort_order, InspectionItem.created_at.desc()).all()
        except Exception as e:
            logger.error(f"查询根节点失败: {str(e)}")
            raise

    def get_tree(self) -> list[dict[str, Any]]:
        try:
            all_items = self.get_all()
            return self._build_tree(all_items)
        except Exception as e:
            logger.error(f"构建树形结构失败: {str(e)}", exc_info=True)
            return []

    def _build_tree(self, items: list[InspectionItem], parent_id: int | None = None) -> list[dict[str, Any]]:
        tree = []
        for item in items:
            if item.parent_id == parent_id:
                try:
                    node = item.to_dict()
                except Exception as e:
                    logger.error(f"序列化巡检事项失败 (id={item.id}): {str(e)}")
                    node = {
                        'id': item.id,
                        'item_code': getattr(item, 'item_code', ''),
                        'item_name': getattr(item, 'item_name', ''),
                        'item_type': getattr(item, 'item_type', ''),
                        'level': getattr(item, 'level', 1),
                        'parent_id': item.parent_id,
                        'sort_order': getattr(item, 'sort_order', 0),
                        'children': [],
                    }
                children = self._build_tree(items, item.id)
                node['children'] = children
                tree.append(node)
        return tree

    def search(self, keyword: str | None = None) -> list[InspectionItem]:
        try:
            query = self.db.query(InspectionItem).filter(
                InspectionItem.deleted_at.is_(None)
            )
            if keyword:
                search_pattern = f"%{keyword}%"
                query = query.filter(
                    or_(
                        InspectionItem.item_code.ilike(search_pattern),
                        InspectionItem.item_name.ilike(search_pattern)
                    )
                )
            return query.order_by(InspectionItem.sort_order, InspectionItem.created_at.desc()).all()
        except Exception as e:
            logger.error(f"搜索巡检事项失败: {str(e)}")
            raise

    def create(self, item_data: InspectionItemCreate) -> InspectionItem:
        try:
            db_item = InspectionItem(**item_data.model_dump())
            self.db.add(db_item)
            self.db.flush()
            self.db.refresh(db_item)
            return db_item
        except Exception as e:
            self.db.rollback()
            logger.error(f"创建巡检事项失败: {str(e)}")
            raise

    def update(self, item_id: int, item_data: InspectionItemUpdate) -> InspectionItem | None:
        try:
            db_item = self.get_by_id(item_id)
            if not db_item:
                return None

            update_data = item_data.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_item, key, value)

            self.db.flush()
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

            now = datetime.now(timezone.utc)
            db_item.deleted_at = now

            children = self.db.query(InspectionItem).filter(
                InspectionItem.parent_id == item_id
            ).all()
            for child in children:
                self._soft_delete_cascade(child.id, now)

            self.db.flush()
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"删除巡检事项失败: {str(e)}")
            raise

    def _soft_delete_cascade(self, item_id: int, deleted_at: datetime) -> None:
        item = self.get_by_id(item_id)
        if item:
            item.deleted_at = deleted_at
            children = self.db.query(InspectionItem).filter(
                InspectionItem.parent_id == item_id
            ).all()
            for child in children:
                self._soft_delete_cascade(child.id, deleted_at)

    def get_paginated(self, skip: int = 0, limit: int = 10) -> tuple[list[InspectionItem], int]:
        try:
            query = self.db.query(InspectionItem).filter(
                InspectionItem.deleted_at.is_(None)
            )
            total = query.count()
            items = query.offset(skip).limit(limit).all()
            return items, total
        except Exception as e:
            logger.error(f"查询巡检事项分页失败: {str(e)}")
            raise

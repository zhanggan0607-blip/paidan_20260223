from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.spare_parts_usage import SparePartsUsage
import logging

logger = logging.getLogger(__name__)


class SparePartsUsageRepository:
    def __init__(self, db: Session):
        self.db = db

    def find_all(
        self,
        page: int = 0,
        size: int = 10,
        user: Optional[str] = None,
        product: Optional[str] = None,
        project: Optional[str] = None,
        status_filter: Optional[str] = None
    ) -> tuple[List[SparePartsUsage], int]:
        try:
            query = self.db.query(SparePartsUsage)

            if user:
                query = query.filter(SparePartsUsage.user_name.like(f'%{user}%'))

            if product:
                query = query.filter(SparePartsUsage.product_name.like(f'%{product}%'))

            if project:
                query = query.filter(SparePartsUsage.project_name.like(f'%{project}%'))

            if status_filter:
                query = query.filter(SparePartsUsage.status == status_filter)

            total = query.count()
            items = query.order_by(SparePartsUsage.issue_time.desc()).offset(page * size).limit(size).all()

            return items, total
        except Exception as e:
            logger.error(f"查询备品备件领用列表失败: {str(e)}")
            raise

    def find_by_id(self, id: int) -> Optional[SparePartsUsage]:
        try:
            return self.db.query(SparePartsUsage).filter(SparePartsUsage.id == id).first()
        except Exception as e:
            logger.error(f"查询备品备件领用失败 (id={id}): {str(e)}")
            raise

    def create(self, usage: SparePartsUsage) -> SparePartsUsage:
        try:
            self.db.add(usage)
            self.db.commit()
            self.db.refresh(usage)
            return usage
        except Exception as e:
            self.db.rollback()
            logger.error(f"创建备品备件领用失败: {str(e)}")
            raise

    def update(self, usage: SparePartsUsage) -> SparePartsUsage:
        try:
            self.db.commit()
            self.db.refresh(usage)
            return usage
        except Exception as e:
            self.db.rollback()
            logger.error(f"更新备品备件领用失败: {str(e)}")
            raise

    def delete(self, usage: SparePartsUsage) -> None:
        try:
            self.db.delete(usage)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            logger.error(f"删除备品备件领用失败: {str(e)}")
            raise

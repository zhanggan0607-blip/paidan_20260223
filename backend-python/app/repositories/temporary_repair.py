from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.temporary_repair import TemporaryRepair
import logging

logger = logging.getLogger(__name__)


class TemporaryRepairRepository:
    def __init__(self, db: Session):
        self._db = db
    
    @property
    def db(self):
        return self._db

    def find_all(
        self,
        page: int = 0,
        size: int = 10,
        project_name: Optional[str] = None,
        client_name: Optional[str] = None,
        status: Optional[str] = None
    ) -> tuple[List[TemporaryRepair], int]:
        try:
            query = self.db.query(TemporaryRepair)

            if project_name:
                query = query.filter(TemporaryRepair.project_name.like(f'%{project_name}%'))

            if client_name:
                query = query.filter(TemporaryRepair.client_name.like(f'%{client_name}%'))

            if status:
                query = query.filter(TemporaryRepair.status == status)

            total = query.count()
            items = query.offset(page * size).limit(size).all()

            return items, total
        except Exception as e:
            logger.error(f"查询临时维修列表失败: {str(e)}")
            raise

    def find_by_id(self, id: int) -> Optional[TemporaryRepair]:
        try:
            return self.db.query(TemporaryRepair).filter(TemporaryRepair.id == id).first()
        except Exception as e:
            logger.error(f"查询临时维修失败 (id={id}): {str(e)}")
            raise

    def find_by_repair_id(self, repair_id: str) -> Optional[TemporaryRepair]:
        try:
            return self.db.query(TemporaryRepair).filter(TemporaryRepair.repair_id == repair_id).first()
        except Exception as e:
            logger.error(f"查询临时维修失败 (repair_id={repair_id}): {str(e)}")
            raise

    def exists_by_repair_id(self, repair_id: str) -> bool:
        try:
            return self.db.query(TemporaryRepair).filter(TemporaryRepair.repair_id == repair_id).first() is not None
        except Exception as e:
            logger.error(f"检查临时维修是否存在失败 (repair_id={repair_id}): {str(e)}")
            raise

    def create(self, repair: TemporaryRepair) -> TemporaryRepair:
        try:
            self.db.add(repair)
            self.db.commit()
            self.db.refresh(repair)
            return repair
        except Exception as e:
            self.db.rollback()
            logger.error(f"创建临时维修失败: {str(e)}")
            raise

    def update(self, repair: TemporaryRepair) -> TemporaryRepair:
        try:
            self.db.commit()
            self.db.refresh(repair)
            return repair
        except Exception as e:
            self.db.rollback()
            logger.error(f"更新临时维修失败: {str(e)}")
            raise

    def delete(self, repair: TemporaryRepair) -> None:
        try:
            self.db.delete(repair)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            logger.error(f"删除临时维修失败: {str(e)}")
            raise

    def find_all_unpaginated(self) -> List[TemporaryRepair]:
        try:
            return self.db.query(TemporaryRepair).all()
        except Exception as e:
            logger.error(f"查询所有临时维修失败: {str(e)}")
            raise

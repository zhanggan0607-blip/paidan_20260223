from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.spot_work import SpotWork
import logging

logger = logging.getLogger(__name__)


class SpotWorkRepository:
    def __init__(self, db: Session):
        self.db = db

    def find_all(
        self,
        page: int = 0,
        size: int = 10,
        project_name: Optional[str] = None,
        client_name: Optional[str] = None,
        status: Optional[str] = None
    ) -> tuple[List[SpotWork], int]:
        try:
            query = self.db.query(SpotWork)

            if project_name:
                query = query.filter(SpotWork.project_name.like(f'%{project_name}%'))

            if client_name:
                query = query.filter(SpotWork.client_name.like(f'%{client_name}%'))

            if status:
                query = query.filter(SpotWork.status == status)

            total = query.count()
            items = query.offset(page * size).limit(size).all()

            return items, total
        except Exception as e:
            logger.error(f"查询零星用工列表失败: {str(e)}")
            raise

    def find_by_id(self, id: int) -> Optional[SpotWork]:
        try:
            return self.db.query(SpotWork).filter(SpotWork.id == id).first()
        except Exception as e:
            logger.error(f"查询零星用工失败 (id={id}): {str(e)}")
            raise

    def find_by_work_id(self, work_id: str) -> Optional[SpotWork]:
        try:
            return self.db.query(SpotWork).filter(SpotWork.work_id == work_id).first()
        except Exception as e:
            logger.error(f"查询零星用工失败 (work_id={work_id}): {str(e)}")
            raise

    def exists_by_work_id(self, work_id: str) -> bool:
        try:
            return self.db.query(SpotWork).filter(SpotWork.work_id == work_id).first() is not None
        except Exception as e:
            logger.error(f"检查零星用工是否存在失败 (work_id={work_id}): {str(e)}")
            raise

    def create(self, work: SpotWork) -> SpotWork:
        try:
            self.db.add(work)
            self.db.commit()
            self.db.refresh(work)
            return work
        except Exception as e:
            self.db.rollback()
            logger.error(f"创建零星用工失败: {str(e)}")
            raise

    def update(self, work: SpotWork) -> SpotWork:
        try:
            self.db.commit()
            self.db.refresh(work)
            return work
        except Exception as e:
            self.db.rollback()
            logger.error(f"更新零星用工失败: {str(e)}")
            raise

    def delete(self, work: SpotWork) -> None:
        try:
            self.db.delete(work)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            logger.error(f"删除零星用工失败: {str(e)}")
            raise

    def find_all_unpaginated(self) -> List[SpotWork]:
        try:
            return self.db.query(SpotWork).all()
        except Exception as e:
            logger.error(f"查询所有零星用工失败: {str(e)}")
            raise

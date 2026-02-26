from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from app.models.spot_work import SpotWork
import logging

logger = logging.getLogger(__name__)


class SpotWorkRepository:
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
        work_id: Optional[str] = None,
        status: Optional[str] = None,
        maintenance_personnel: Optional[str] = None,
        client_name: Optional[str] = None
    ) -> tuple[List[SpotWork], int]:
        try:
            query = self.db.query(SpotWork).options(joinedload(SpotWork.project)).filter(
                SpotWork.is_deleted == False
            )

            if project_name:
                query = query.filter(SpotWork.project_name.like(f'%{project_name}%'))

            if work_id:
                query = query.filter(SpotWork.work_id.like(f'%{work_id}%'))

            if status:
                query = query.filter(SpotWork.status == status)
            
            if maintenance_personnel:
                query = query.filter(SpotWork.maintenance_personnel == maintenance_personnel)
            
            if client_name:
                query = query.filter(SpotWork.client_name.like(f'%{client_name}%'))

            total = query.count()
            items = query.order_by(SpotWork.created_at.desc()).offset(page * size).limit(size).all()

            return items, total
        except Exception as e:
            logger.error(f"查询零星用工列表失败: {str(e)}")
            raise

    def find_by_id(self, id: int) -> Optional[SpotWork]:
        try:
            return self.db.query(SpotWork).options(joinedload(SpotWork.project)).filter(
                SpotWork.id == id,
                SpotWork.is_deleted == False
            ).first()
        except Exception as e:
            logger.error(f"查询零星用工失败 (id={id}): {str(e)}")
            raise

    def find_by_work_id(self, work_id: str) -> Optional[SpotWork]:
        try:
            return self.db.query(SpotWork).options(joinedload(SpotWork.project)).filter(
                SpotWork.work_id == work_id,
                SpotWork.is_deleted == False
            ).first()
        except Exception as e:
            logger.error(f"查询零星用工失败 (work_id={work_id}): {str(e)}")
            raise

    def exists_by_work_id(self, work_id: str) -> bool:
        try:
            return self.db.query(SpotWork).filter(
                SpotWork.work_id == work_id,
                SpotWork.is_deleted == False
            ).first() is not None
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

    def soft_delete(self, work: SpotWork, user_id: int = None) -> None:
        """
        软删除零星用工单
        
        Args:
            work: 要删除的工单对象
            user_id: 执行删除的用户ID
        """
        try:
            work.soft_delete(user_id)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            logger.error(f"软删除零星用工失败: {str(e)}")
            raise

    def delete(self, work: SpotWork) -> None:
        """
        物理删除（已弃用，请使用soft_delete）
        """
        try:
            self.db.delete(work)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            logger.error(f"删除零星用工失败: {str(e)}")
            raise

    def find_all_unpaginated(self) -> List[SpotWork]:
        try:
            return self.db.query(SpotWork).options(joinedload(SpotWork.project)).filter(
                SpotWork.is_deleted == False
            ).all()
        except Exception as e:
            logger.error(f"查询所有零星用工失败: {str(e)}")
            raise

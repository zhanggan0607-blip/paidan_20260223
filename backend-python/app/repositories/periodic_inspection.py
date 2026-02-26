from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from app.models.periodic_inspection import PeriodicInspection
import logging

logger = logging.getLogger(__name__)


class PeriodicInspectionRepository:
    def __init__(self, db: Session):
        self._db = db
    
    @property
    def db(self):
        return self._db

    def find_by_id(self, id: int) -> Optional[PeriodicInspection]:
        try:
            return self.db.query(PeriodicInspection).options(
                joinedload(PeriodicInspection.project)
            ).filter(
                PeriodicInspection.id == id,
                PeriodicInspection.is_deleted == False
            ).first()
        except Exception as e:
            logger.error(f"查询定期巡检失败 (id={id}): {str(e)}")
            raise

    def find_by_inspection_id(self, inspection_id: str) -> Optional[PeriodicInspection]:
        try:
            return self.db.query(PeriodicInspection).filter(
                PeriodicInspection.inspection_id == inspection_id,
                PeriodicInspection.is_deleted == False
            ).first()
        except Exception as e:
            logger.error(f"查询定期巡检失败 (inspection_id={inspection_id}): {str(e)}")
            raise

    def exists_by_inspection_id(self, inspection_id: str) -> bool:
        try:
            return self.db.query(PeriodicInspection).filter(
                PeriodicInspection.inspection_id == inspection_id,
                PeriodicInspection.is_deleted == False
            ).first() is not None
        except Exception as e:
            logger.error(f"检查定期巡检是否存在失败 (inspection_id={inspection_id}): {str(e)}")
            raise

    def find_all(
        self,
        page: int = 0,
        size: int = 10,
        project_name: Optional[str] = None,
        client_name: Optional[str] = None,
        inspection_id: Optional[str] = None,
        status: Optional[str] = None,
        maintenance_personnel: Optional[str] = None
    ) -> tuple[List[PeriodicInspection], int]:
        try:
            query = self.db.query(PeriodicInspection).options(
                joinedload(PeriodicInspection.project)
            ).filter(PeriodicInspection.is_deleted == False)

            if project_name:
                query = query.filter(PeriodicInspection.project_name.like(f"%{project_name}%"))

            if client_name:
                query = query.filter(PeriodicInspection.client_name.like(f"%{client_name}%"))

            if inspection_id:
                query = query.filter(PeriodicInspection.inspection_id.like(f"%{inspection_id}%"))

            if status:
                query = query.filter(PeriodicInspection.status == status)
            
            if maintenance_personnel:
                query = query.filter(PeriodicInspection.maintenance_personnel == maintenance_personnel)

            total = query.count()
            items = query.order_by(PeriodicInspection.updated_at.desc().nullslast(), PeriodicInspection.created_at.desc()).offset(page * size).limit(size).all()

            return items, total
        except Exception as e:
            logger.error(f"查询定期巡检列表失败: {str(e)}")
            raise

    def find_all_unpaginated(self) -> List[PeriodicInspection]:
        try:
            return self.db.query(PeriodicInspection).options(
                joinedload(PeriodicInspection.project)
            ).filter(
                PeriodicInspection.is_deleted == False
            ).order_by(PeriodicInspection.updated_at.desc().nullslast(), PeriodicInspection.created_at.desc()).all()
        except Exception as e:
            logger.error(f"查询所有定期巡检失败: {str(e)}")
            raise

    def create(self, inspection: PeriodicInspection) -> PeriodicInspection:
        try:
            self.db.add(inspection)
            self.db.commit()
            self.db.refresh(inspection)
            return inspection
        except Exception as e:
            self.db.rollback()
            logger.error(f"创建定期巡检失败: {str(e)}")
            raise

    def update(self, inspection: PeriodicInspection) -> PeriodicInspection:
        try:
            self.db.commit()
            self.db.refresh(inspection)
            return inspection
        except Exception as e:
            self.db.rollback()
            logger.error(f"更新定期巡检失败: {str(e)}")
            raise

    def soft_delete(self, inspection: PeriodicInspection, user_id: int = None) -> None:
        """
        软删除定期巡检单
        
        Args:
            inspection: 要删除的巡检单对象
            user_id: 执行删除的用户ID
        """
        try:
            inspection.soft_delete(user_id)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            logger.error(f"软删除定期巡检失败: {str(e)}")
            raise

    def delete(self, inspection: PeriodicInspection) -> None:
        """
        物理删除（已弃用，请使用soft_delete）
        """
        try:
            self.db.delete(inspection)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            logger.error(f"删除定期巡检失败: {str(e)}")
            raise

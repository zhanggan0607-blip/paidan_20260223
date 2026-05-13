"""
定期巡检Repository
提供定期巡检数据访问方法
"""
from app.utils.logging_config import get_logger

from sqlalchemy.orm import Session, selectinload

from app.models.periodic_inspection import PeriodicInspection
from app.repositories.base import BaseRepository

logger = get_logger(__name__)


class PeriodicInspectionRepository(BaseRepository[PeriodicInspection]):
    """
    定期巡检Repository
    继承BaseRepository，复用通用CRUD方法
    """

    def __init__(self, db: Session):
        super().__init__(db, PeriodicInspection)

    def find_by_id(self, id: int) -> PeriodicInspection | None:
        try:
            return self.db.query(PeriodicInspection).options(
                selectinload(PeriodicInspection.project)
            ).filter(
                PeriodicInspection.id == id,
                PeriodicInspection.is_deleted == False
            ).first()
        except Exception as e:
            logger.error(f"查询定期巡检失败 (id={id}): {str(e)}")
            raise

    def find_by_inspection_id(self, inspection_id: str) -> PeriodicInspection | None:
        """
        根据巡检单编号查询

        Args:
            inspection_id: 巡检单编号

        Returns:
            巡检单对象，未找到返回None
        """
        try:
            return self.db.query(PeriodicInspection).filter(
                PeriodicInspection.inspection_id == inspection_id,
                PeriodicInspection.is_deleted == False
            ).first()
        except Exception as e:
            logger.error(f"查询定期巡检失败 (inspection_id={inspection_id}): {str(e)}")
            raise

    def exists_by_inspection_id(self, inspection_id: str) -> bool:
        """
        检查巡检单编号是否存在

        Args:
            inspection_id: 巡检单编号

        Returns:
            是否存在
        """
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
        project_name: str | None = None,
        client_name: str | None = None,
        inspection_id: str | None = None,
        status: str | None = None,
        maintenance_personnel: str | None = None,
        statuses: list[str] | None = None
    ) -> tuple[list[PeriodicInspection], int]:
        try:
            query = self.db.query(PeriodicInspection).filter(PeriodicInspection.is_deleted == False)

            if project_name:
                query = query.filter(PeriodicInspection.project_name.like(f"%{self.escape_like(project_name)}%", escape='\\'))

            if client_name:
                query = query.filter(PeriodicInspection.client_name.like(f"%{self.escape_like(client_name)}%", escape='\\'))

            if inspection_id:
                query = query.filter(PeriodicInspection.inspection_id.like(f"%{self.escape_like(inspection_id)}%", escape='\\'))

            if status:
                query = query.filter(PeriodicInspection.status == status)

            if statuses:
                query = query.filter(PeriodicInspection.status.in_(statuses))

            if maintenance_personnel:
                query = query.filter(PeriodicInspection.maintenance_personnel == maintenance_personnel)

            total = query.count()
            items = query.order_by(PeriodicInspection.created_at.desc(), PeriodicInspection.id.desc()).offset(page * size).limit(size).all()

            return items, total
        except Exception as e:
            logger.error(f"查询定期巡检列表失败: {str(e)}")
            raise

    def find_all_unpaginated(self) -> list[PeriodicInspection]:
        try:
            return list(
                self.db.query(PeriodicInspection).options(
                    selectinload(PeriodicInspection.project)
                ).filter(
                    PeriodicInspection.is_deleted == False
                ).order_by(PeriodicInspection.created_at.desc(), PeriodicInspection.id.desc())
                .yield_per(200)
            )
        except Exception as e:
            logger.error(f"查询所有定期巡检失败: {str(e)}")
            raise


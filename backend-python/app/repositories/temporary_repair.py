"""
临时维修Repository
提供临时维修数据访问方法
"""
from app.utils.logging_config import get_logger

from sqlalchemy.orm import Session, selectinload

from app.models.temporary_repair import TemporaryRepair
from app.repositories.base import BaseRepository

logger = get_logger(__name__)


class TemporaryRepairRepository(BaseRepository[TemporaryRepair]):
    """
    临时维修Repository
    继承BaseRepository，复用通用CRUD方法
    """

    def __init__(self, db: Session):
        super().__init__(db, TemporaryRepair)

    def find_all(
        self,
        page: int = 0,
        size: int = 10,
        project_name: str | None = None,
        repair_id: str | None = None,
        status: str | None = None,
        maintenance_personnel: str | None = None,
        client_name: str | None = None,
        statuses: list[str] | None = None
    ) -> tuple[list[TemporaryRepair], int]:
        try:
            query = self.db.query(TemporaryRepair).filter(TemporaryRepair.is_deleted == False)

            if project_name:
                query = query.filter(TemporaryRepair.project_name.like(f'%{self.escape_like(project_name)}%', escape='\\'))

            if repair_id:
                query = query.filter(TemporaryRepair.repair_id.like(f'%{self.escape_like(repair_id)}%', escape='\\'))

            if status:
                query = query.filter(TemporaryRepair.status == status)

            if statuses:
                query = query.filter(TemporaryRepair.status.in_(statuses))

            if maintenance_personnel:
                query = query.filter(TemporaryRepair.maintenance_personnel == maintenance_personnel)

            if client_name:
                query = query.filter(TemporaryRepair.client_name.like(f'%{self.escape_like(client_name)}%', escape='\\'))

            total = query.count()
            items = query.order_by(TemporaryRepair.created_at.desc(), TemporaryRepair.id.desc()).offset(page * size).limit(size).all()

            return items, total
        except Exception as e:
            logger.error(f"查询临时维修列表失败: {str(e)}")
            raise

    def find_by_id(self, id: int) -> TemporaryRepair | None:
        try:
            return self.db.query(TemporaryRepair).options(
                selectinload(TemporaryRepair.project)
            ).filter(
                TemporaryRepair.id == id,
                TemporaryRepair.is_deleted == False
            ).first()
        except Exception as e:
            logger.error(f"查询临时维修失败 (id={id}): {str(e)}")
            raise

    def find_by_repair_id(self, repair_id: str) -> TemporaryRepair | None:
        try:
            return self.db.query(TemporaryRepair).options(
                selectinload(TemporaryRepair.project)
            ).filter(
                TemporaryRepair.repair_id == repair_id,
                TemporaryRepair.is_deleted == False
            ).first()
        except Exception as e:
            logger.error(f"查询临时维修失败 (repair_id={repair_id}): {str(e)}")
            raise

    def exists_by_repair_id(self, repair_id: str, include_deleted: bool = False) -> bool:
        """
        检查维修单编号是否存在

        Args:
            repair_id: 维修单编号
            include_deleted: 是否包含已删除的记录

        Returns:
            是否存在
        """
        try:
            query = self.db.query(TemporaryRepair).filter(
                TemporaryRepair.repair_id == repair_id
            )
            if not include_deleted:
                query = query.filter(TemporaryRepair.is_deleted == False)
            return query.first() is not None
        except Exception as e:
            logger.error(f"检查临时维修是否存在失败 (repair_id={repair_id}): {str(e)}")
            raise

    def find_all_unpaginated(self) -> list[TemporaryRepair]:
        try:
            return list(
                self.db.query(TemporaryRepair).options(
                    selectinload(TemporaryRepair.project)
                ).filter(
                    TemporaryRepair.is_deleted == False
                ).order_by(TemporaryRepair.created_at.desc(), TemporaryRepair.id.desc())
                .yield_per(200)
            )
        except Exception as e:
            logger.error(f"查询所有临时维修失败: {str(e)}")
            raise

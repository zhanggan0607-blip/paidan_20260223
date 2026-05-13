from app.utils.logging_config import get_logger

from sqlalchemy.orm import Session

from app.models.project_info import ProjectInfo
from app.repositories.base import BaseRepository

logger = get_logger(__name__)


class ProjectInfoRepository(BaseRepository[ProjectInfo]):

    def __init__(self, db: Session):
        super().__init__(db, ProjectInfo)

    def find_by_id(self, id: int, options: list | None = None) -> ProjectInfo | None:
        try:
            query = self.db.query(ProjectInfo).filter(
                ProjectInfo.id == id
            )
            if options:
                for option in options:
                    query = query.options(option)
            return query.first()
        except Exception as e:
            logger.error(f"查询项目信息失败 (id={id}): {str(e)}")
            raise

    def find_by_project_id(self, project_id: str) -> ProjectInfo | None:
        return self.db.query(ProjectInfo).filter(
            ProjectInfo.project_id == project_id
        ).first()

    def exists_by_project_id(self, project_id: str) -> bool:
        return self.db.query(ProjectInfo).filter(
            ProjectInfo.project_id == project_id
        ).first() is not None

    def find_all(
        self,
        page: int = 0,
        size: int = 10,
        project_name: str | None = None,
        client_name: str | None = None,
        project_ids: list[str] | None = None
    ) -> tuple[list[ProjectInfo], int]:
        try:
            query = self.db.query(ProjectInfo)

            if project_name:
                query = query.filter(ProjectInfo.project_name.like(f"%{project_name}%"))

            if client_name:
                query = query.filter(ProjectInfo.client_name.like(f"%{client_name}%"))

            if project_ids:
                query = query.filter(ProjectInfo.project_id.in_(project_ids))

            total = query.count()
            items = query.order_by(ProjectInfo.created_at.desc(), ProjectInfo.id.desc()).offset(page * size).limit(size).all()
            return items, total
        except Exception as e:
            logger.error(f"查询项目信息列表失败: {str(e)}")
            raise

    def find_all_unpaginated(self, project_ids: list[str] | None = None) -> list[ProjectInfo]:
        try:
            query = self.db.query(ProjectInfo)
            if project_ids:
                query = query.filter(ProjectInfo.project_id.in_(project_ids))
            return list(query.order_by(ProjectInfo.created_at.desc(), ProjectInfo.id.desc()).yield_per(200))
        except Exception as e:
            logger.error(f"查询所有项目信息失败: {str(e)}")
            raise

"""
项目信息Repository
提供项目信息数据访问操作
"""
import logging

from sqlalchemy.orm import Session

from app.models.project_info import ProjectInfo
from app.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class ProjectInfoRepository(BaseRepository[ProjectInfo]):
    """
    项目信息Repository
    继承BaseRepository，复用通用CRUD操作
    """

    def __init__(self, db: Session):
        super().__init__(db, ProjectInfo)

    def find_by_project_id(self, project_id: str) -> ProjectInfo | None:
        """
        根据项目编号查询项目信息

        Args:
            project_id: 项目编号

        Returns:
            项目信息，未找到返回None
        """
        return self.find_by_field('project_id', project_id)

    def exists_by_project_id(self, project_id: str) -> bool:
        """
        检查项目编号是否存在

        Args:
            project_id: 项目编号

        Returns:
            是否存在
        """
        return self.exists_by_field('project_id', project_id)

    def find_all(
        self,
        page: int = 0,
        size: int = 10,
        project_name: str | None = None,
        client_name: str | None = None,
        project_ids: list[str] | None = None
    ) -> tuple[list[ProjectInfo], int]:
        """
        分页查询项目信息列表

        Args:
            page: 页码
            size: 每页数量
            project_name: 项目名称（模糊查询）
            client_name: 客户名称（模糊查询）
            project_ids: 项目编号列表（精确筛选）

        Returns:
            (项目列表, 总数)
        """
        try:
            query = self.db.query(ProjectInfo)

            if project_name:
                query = query.filter(ProjectInfo.project_name.like(f"%{project_name}%"))

            if client_name:
                query = query.filter(ProjectInfo.client_name.like(f"%{client_name}%"))

            if project_ids:
                query = query.filter(ProjectInfo.project_id.in_(project_ids))

            total = query.count()
            items = query.order_by(ProjectInfo.id.asc()).offset(page * size).limit(size).all()
            return items, total
        except Exception as e:
            logger.error(f"查询项目信息列表失败: {str(e)}")
            raise

    def find_all_unpaginated(self, project_ids: list[str] | None = None) -> list[ProjectInfo]:
        """
        查询所有项目信息（不分页）

        Args:
            project_ids: 项目编号列表（精确筛选）

        Returns:
            项目列表
        """
        try:
            query = self.db.query(ProjectInfo)
            if project_ids:
                query = query.filter(ProjectInfo.project_id.in_(project_ids))
            return query.order_by(ProjectInfo.created_at.desc()).all()
        except Exception as e:
            logger.error(f"查询所有项目信息失败: {str(e)}")
            raise

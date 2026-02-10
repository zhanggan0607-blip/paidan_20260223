from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from app.models.project_info import ProjectInfo
import logging

logger = logging.getLogger(__name__)


class ProjectInfoRepository:
    def __init__(self, db: Session):
        self.db = db

    def find_by_id(self, id: int) -> Optional[ProjectInfo]:
        try:
            return self.db.query(ProjectInfo).filter(ProjectInfo.id == id).first()
        except Exception as e:
            logger.error(f"查询项目信息失败 (id={id}): {str(e)}")
            raise

    def find_by_project_id(self, project_id: str) -> Optional[ProjectInfo]:
        try:
            return self.db.query(ProjectInfo).filter(ProjectInfo.project_id == project_id).first()
        except Exception as e:
            logger.error(f"查询项目信息失败 (project_id={project_id}): {str(e)}")
            raise

    def exists_by_project_id(self, project_id: str) -> bool:
        try:
            return self.db.query(ProjectInfo).filter(ProjectInfo.project_id == project_id).first() is not None
        except Exception as e:
            logger.error(f"检查项目信息是否存在失败 (project_id={project_id}): {str(e)}")
            raise

    def find_all(
        self,
        page: int = 0,
        size: int = 10,
        project_name: Optional[str] = None,
        client_name: Optional[str] = None
    ) -> tuple[List[ProjectInfo], int]:
        try:
            query = self.db.query(ProjectInfo)

            if project_name:
                query = query.filter(ProjectInfo.project_name.like(f"%{project_name}%"))

            if client_name:
                query = query.filter(ProjectInfo.client_name.like(f"%{client_name}%"))

            total = query.count()
            items = query.order_by(ProjectInfo.created_at.desc()).offset(page * size).limit(size).all()

            return items, total
        except Exception as e:
            logger.error(f"查询项目信息列表失败: {str(e)}")
            raise

    def find_all_unpaginated(self) -> List[ProjectInfo]:
        try:
            return self.db.query(ProjectInfo).order_by(ProjectInfo.created_at.desc()).all()
        except Exception as e:
            logger.error(f"查询所有项目信息失败: {str(e)}")
            raise

    def create(self, project_info: ProjectInfo) -> ProjectInfo:
        try:
            print(f"📥 [Repository] 准备插入数据: id={project_info.id}, project_id={project_info.project_id}")

            self.db.add(project_info)
            self.db.commit()
            self.db.refresh(project_info)
            print(f"✅ [Repository] 数据库插入成功: id={project_info.id}, project_id={project_info.project_id}")
            return project_info
        except Exception as e:
            print(f"❌ [Repository] 数据库插入失败: {str(e)}")
            self.db.rollback()
            logger.error(f"创建项目信息失败: {str(e)}")
            raise

    def update(self, project_info: ProjectInfo) -> ProjectInfo:
        try:
            self.db.commit()
            self.db.refresh(project_info)
            return project_info
        except Exception as e:
            self.db.rollback()
            logger.error(f"更新项目信息失败: {str(e)}")
            raise

    def delete(self, project_info: ProjectInfo) -> None:
        try:
            self.db.delete(project_info)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            logger.error(f"删除项目信息失败: {str(e)}")
            raise

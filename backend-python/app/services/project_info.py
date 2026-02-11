from typing import List, Optional
import logging
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.project_info import ProjectInfo
from app.repositories.project_info import ProjectInfoRepository
from app.schemas.project_info import ProjectInfoCreate, ProjectInfoUpdate

logger = logging.getLogger(__name__)


class ProjectInfoService:
    def __init__(self, db: Session):
        self.repository = ProjectInfoRepository(db)
    
    def get_all(
        self, 
        page: int = 0, 
        size: int = 10, 
        project_name: Optional[str] = None, 
        client_name: Optional[str] = None
    ) -> tuple[List[ProjectInfo], int]:
        return self.repository.find_all(page, size, project_name, client_name)
    
    def get_by_id(self, id: int) -> ProjectInfo:
        project_info = self.repository.find_by_id(id)
        if not project_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="项目信息不存在"
            )
        return project_info
    
    def get_by_project_id(self, project_id: str) -> ProjectInfo:
        project_info = self.repository.find_by_project_id(project_id)
        if not project_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="项目信息不存在"
            )
        return project_info
    
    def create(self, dto: ProjectInfoCreate) -> ProjectInfo:
        logger.info(f"📥 [Service] 开始创建项目: project_id={dto.project_id}, project_name={dto.project_name}")

        if self.repository.exists_by_project_id(dto.project_id):
            logger.error(f"❌ [Service] 项目编号已存在: {dto.project_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="项目编号已存在"
            )

        project_info = ProjectInfo(
            project_id=dto.project_id,
            project_name=dto.project_name,
            completion_date=dto.completion_date,
            maintenance_end_date=dto.maintenance_end_date,
            maintenance_period=dto.maintenance_period,
            client_name=dto.client_name,
            address=dto.address,
            project_abbr=dto.project_abbr,
            client_contact=dto.client_contact,
            client_contact_position=dto.client_contact_position,
            client_contact_info=dto.client_contact_info
        )

        logger.info(f"📥 [Service] 准备保存到数据库: project_id={project_info.project_id}, project_name={project_info.project_name}")
        result = self.repository.create(project_info)
        logger.info(f"✅ [Service] 数据库保存成功: id={result.id}, project_id={result.project_id}")
        return result
    
    def update(self, id: int, dto: ProjectInfoUpdate) -> ProjectInfo:
        existing_project = self.get_by_id(id)
        
        if existing_project.project_id != dto.project_id and self.repository.exists_by_project_id(dto.project_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="项目编号已存在"
            )
        
        existing_project.project_name = dto.project_name
        existing_project.project_id = dto.project_id
        existing_project.completion_date = dto.completion_date
        existing_project.maintenance_end_date = dto.maintenance_end_date
        existing_project.maintenance_period = dto.maintenance_period
        existing_project.client_name = dto.client_name
        existing_project.address = dto.address
        existing_project.project_abbr = dto.project_abbr
        existing_project.client_contact = dto.client_contact
        existing_project.client_contact_position = dto.client_contact_position
        existing_project.client_contact_info = dto.client_contact_info
        
        return self.repository.update(existing_project)
    
    def delete(self, id: int) -> None:
        project_info = self.get_by_id(id)
        self.repository.delete(project_info)
    
    def get_all_unpaginated(self) -> List[ProjectInfo]:
        return self.repository.find_all_unpaginated()

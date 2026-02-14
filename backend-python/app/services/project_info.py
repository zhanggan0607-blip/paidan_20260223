from typing import List, Optional
import logging
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models.project_info import ProjectInfo
from app.repositories.project_info import ProjectInfoRepository
from app.schemas.project_info import ProjectInfoCreate, ProjectInfoUpdate

logger = logging.getLogger(__name__)


class ProjectInfoService:
    def __init__(self, db: Session):
        self.repository = ProjectInfoRepository(db)
        self.db = db
    
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
            project_manager=dto.project_manager,
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
        
        if existing_project.project_id != dto.project_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="项目编号不允许修改"
            )
        
        existing_project.project_name = dto.project_name
        existing_project.completion_date = dto.completion_date
        existing_project.maintenance_end_date = dto.maintenance_end_date
        existing_project.maintenance_period = dto.maintenance_period
        existing_project.client_name = dto.client_name
        existing_project.address = dto.address
        existing_project.project_abbr = dto.project_abbr
        existing_project.project_manager = dto.project_manager
        existing_project.client_contact = dto.client_contact
        existing_project.client_contact_position = dto.client_contact_position
        existing_project.client_contact_info = dto.client_contact_info
        
        result = self.repository.update(existing_project)
        
        return result
    
    def delete(self, id: int, cascade: bool = False) -> dict:
        project_info = self.get_by_id(id)
        
        from app.models.work_plan import WorkPlan
        from app.models.periodic_inspection import PeriodicInspection
        from app.models.temporary_repair import TemporaryRepair
        from app.models.spot_work import SpotWork
        from app.models.maintenance_plan import MaintenancePlan
        
        project_id = project_info.project_id
        
        work_plan_count = self.db.query(WorkPlan).filter(WorkPlan.project_id == project_id).count()
        periodic_count = self.db.query(PeriodicInspection).filter(PeriodicInspection.project_id == project_id).count()
        repair_count = self.db.query(TemporaryRepair).filter(TemporaryRepair.project_id == project_id).count()
        spot_count = self.db.query(SpotWork).filter(SpotWork.project_id == project_id).count()
        maintenance_count = self.db.query(MaintenancePlan).filter(MaintenancePlan.project_id == project_id).count()
        
        total_related = work_plan_count + periodic_count + repair_count + spot_count + maintenance_count
        
        if total_related > 0 and not cascade:
            details = []
            if work_plan_count > 0:
                details.append(f"{work_plan_count} 条工作计划")
            if periodic_count > 0:
                details.append(f"{periodic_count} 条定期巡检")
            if repair_count > 0:
                details.append(f"{repair_count} 条临时维修")
            if spot_count > 0:
                details.append(f"{spot_count} 条零星用工")
            if maintenance_count > 0:
                details.append(f"{maintenance_count} 条维保计划")
            
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"该项目下有 {', '.join(details)}，请确认是否级联删除"
            )
        
        deleted_counts = {}
        
        if cascade:
            if work_plan_count > 0:
                self.db.query(WorkPlan).filter(WorkPlan.project_id == project_id).delete(synchronize_session=False)
                deleted_counts['work_plan'] = work_plan_count
            
            if periodic_count > 0:
                self.db.query(PeriodicInspection).filter(PeriodicInspection.project_id == project_id).delete(synchronize_session=False)
                deleted_counts['periodic_inspection'] = periodic_count
            
            if repair_count > 0:
                self.db.query(TemporaryRepair).filter(TemporaryRepair.project_id == project_id).delete(synchronize_session=False)
                deleted_counts['temporary_repair'] = repair_count
            
            if spot_count > 0:
                self.db.query(SpotWork).filter(SpotWork.project_id == project_id).delete(synchronize_session=False)
                deleted_counts['spot_work'] = spot_count
            
            if maintenance_count > 0:
                self.db.query(MaintenancePlan).filter(MaintenancePlan.project_id == project_id).delete(synchronize_session=False)
                deleted_counts['maintenance_plan'] = maintenance_count
            
            self.db.commit()
        
        self.repository.delete(project_info)
        
        return {
            'project_name': project_info.project_name,
            'deleted_related': deleted_counts
        }
    
    def get_all_unpaginated(self) -> List[ProjectInfo]:
        return self.repository.find_all_unpaginated()

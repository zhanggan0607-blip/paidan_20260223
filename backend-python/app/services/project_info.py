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
    
    def _sync_customer_data(self, client_name: str, client_contact: Optional[str], client_contact_info: Optional[str], address: Optional[str], client_contact_position: Optional[str]):
        """
        同步客户数据到customer表
        如果客户不存在则创建，存在则更新
        """
        from app.models.customer import Customer
        
        if not client_name:
            return
        
        try:
            existing_customer = self.db.query(Customer).filter(Customer.name == client_name).first()
            
            if existing_customer:
                if client_contact and client_contact != existing_customer.contact_person:
                    existing_customer.contact_person = client_contact
                if client_contact_info and client_contact_info != existing_customer.phone:
                    existing_customer.phone = client_contact_info
                if address and address != existing_customer.address:
                    existing_customer.address = address
                if client_contact_position and client_contact_position != existing_customer.contact_position:
                    existing_customer.contact_position = client_contact_position
                self.db.commit()
                logger.info(f"同步更新客户信息: {client_name}")
            else:
                new_customer = Customer(
                    name=client_name,
                    contact_person=client_contact or '',
                    phone=client_contact_info or '',
                    address=address or '',
                    contact_position=client_contact_position or ''
                )
                self.db.add(new_customer)
                self.db.commit()
                logger.info(f"自动创建客户: {client_name}")
        except Exception as e:
            self.db.rollback()
            logger.error(f"同步客户数据失败: {str(e)}")
    
    def get_all(
        self, 
        page: int = 0, 
        size: int = 10, 
        project_name: Optional[str] = None, 
        client_name: Optional[str] = None,
        project_ids: Optional[List[str]] = None
    ) -> tuple[List[ProjectInfo], int]:
        return self.repository.find_all(page, size, project_name, client_name, project_ids)
    
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
        
        self._sync_customer_data(
            dto.client_name,
            dto.client_contact,
            dto.client_contact_info,
            dto.address,
            dto.client_contact_position
        )
        
        logger.info(f"✅ [Service] 数据库保存成功: id={result.id}, project_id={result.project_id}")
        return result
    
    def update(self, id: int, dto: ProjectInfoUpdate) -> ProjectInfo:
        existing_project = self.get_by_id(id)
        
        if existing_project.project_id != dto.project_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="项目编号不允许修改"
            )
        
        old_project_name = existing_project.project_name
        old_client_name = existing_project.client_name
        old_project_manager = existing_project.project_manager
        
        project_name_changed = old_project_name != dto.project_name
        client_name_changed = old_client_name != dto.client_name
        project_manager_changed = old_project_manager != dto.project_manager
        
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
        
        self._sync_customer_data(
            dto.client_name,
            dto.client_contact,
            dto.client_contact_info,
            dto.address,
            dto.client_contact_position
        )
        
        if project_name_changed or client_name_changed:
            self._sync_related_tables(
                existing_project.project_id,
                existing_project.id,
                dto.project_name if project_name_changed else None,
                dto.client_name if client_name_changed else None
            )
        
        if project_manager_changed and dto.project_manager:
            self._sync_maintenance_plan_responsible_person(
                existing_project.project_id,
                dto.project_manager
            )
        
        return result
    
    def _sync_related_tables(
        self, 
        project_id: str,
        project_pk: int,
        new_project_name: Optional[str] = None, 
        new_client_name: Optional[str] = None
    ):
        from app.models.work_plan import WorkPlan
        from app.models.periodic_inspection import PeriodicInspection
        from app.models.temporary_repair import TemporaryRepair
        from app.models.spot_work import SpotWork
        from app.models.spare_parts_usage import SparePartsUsage
        from app.models.repair_tools import RepairToolsIssue
        from app.models.maintenance_plan import MaintenancePlan
        
        sync_count = 0
        
        if new_project_name:
            work_plan_updated = self.db.query(WorkPlan).filter(
                WorkPlan.project_id == project_id
            ).update({"project_name": new_project_name}, synchronize_session=False)
            sync_count += work_plan_updated
            
            periodic_updated = self.db.query(PeriodicInspection).filter(
                PeriodicInspection.project_id == project_id
            ).update({"project_name": new_project_name}, synchronize_session=False)
            sync_count += periodic_updated
            
            repair_updated = self.db.query(TemporaryRepair).filter(
                TemporaryRepair.project_id == project_id
            ).update({"project_name": new_project_name}, synchronize_session=False)
            sync_count += repair_updated
            
            spot_work_updated = self.db.query(SpotWork).filter(
                SpotWork.project_id == project_id
            ).update({"project_name": new_project_name}, synchronize_session=False)
            sync_count += spot_work_updated
            
            spare_parts_updated = self.db.query(SparePartsUsage).filter(
                SparePartsUsage.project_id == project_id
            ).update({"project_name": new_project_name}, synchronize_session=False)
            sync_count += spare_parts_updated
            
            tools_issue_updated = self.db.query(RepairToolsIssue).filter(
                RepairToolsIssue.project_id == project_id
            ).update({"project_name": new_project_name}, synchronize_session=False)
            sync_count += tools_issue_updated
            
            maintenance_plan_updated = self.db.query(MaintenancePlan).filter(
                MaintenancePlan.project_id == project_id
            ).update({"project_name": new_project_name}, synchronize_session=False)
            sync_count += maintenance_plan_updated
        
        if new_client_name:
            work_plan_updated = self.db.query(WorkPlan).filter(
                WorkPlan.project_id == project_id
            ).update({"client_name": new_client_name}, synchronize_session=False)
            sync_count += work_plan_updated
            
            periodic_updated = self.db.query(PeriodicInspection).filter(
                PeriodicInspection.project_id == project_id
            ).update({"client_name": new_client_name}, synchronize_session=False)
            sync_count += periodic_updated
            
            repair_updated = self.db.query(TemporaryRepair).filter(
                TemporaryRepair.project_id == project_id
            ).update({"client_name": new_client_name}, synchronize_session=False)
            sync_count += repair_updated
            
            spot_work_updated = self.db.query(SpotWork).filter(
                SpotWork.project_id == project_id
            ).update({"client_name": new_client_name}, synchronize_session=False)
            sync_count += spot_work_updated
        
        if sync_count > 0:
            self.db.commit()
            logger.info(f"✅ [Service] 同步更新关联表数据: project_id={project_id}, 更新记录数={sync_count}")
    
    def _sync_maintenance_plan_responsible_person(self, project_id: str, new_responsible_person: str):
        """
        同步更新维保计划的负责人
        当项目信息的运维人员变更时，自动更新所有关联维保计划的负责人
        """
        from app.models.maintenance_plan import MaintenancePlan
        
        try:
            updated_count = self.db.query(MaintenancePlan).filter(
                MaintenancePlan.project_id == project_id
            ).update({"responsible_person": new_responsible_person}, synchronize_session=False)
            
            if updated_count > 0:
                self.db.commit()
                logger.info(f"✅ [Service] 同步更新维保计划负责人: project_id={project_id}, 新负责人={new_responsible_person}, 更新记录数={updated_count}")
        except Exception as e:
            self.db.rollback()
            logger.error(f"❌ [Service] 同步更新维保计划负责人失败: {str(e)}")
    
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
    
    def get_all_unpaginated(self, project_ids: Optional[List[str]] = None) -> List[ProjectInfo]:
        return self.repository.find_all_unpaginated(project_ids)
    
    def get_user_project_ids(self, user_name: str) -> List[str]:
        """
        获取用户关联的项目ID列表（通过项目运维人员字段关联）
        返回 None 表示用户可以看到所有项目（管理员/部门经理）
        返回空列表表示用户没有任何关联项目
        返回非空列表表示用户只能看到这些项目
        """
        projects = self.db.query(ProjectInfo.project_id).filter(
            ProjectInfo.project_manager == user_name
        ).all()
        project_ids = [p[0] for p in projects if p[0]]
        return project_ids if project_ids else []

from typing import List, Optional, Union
import logging
from fastapi import HTTPException, status
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.maintenance_plan import MaintenancePlan
from app.models.periodic_inspection import PeriodicInspection
from app.models.temporary_repair import TemporaryRepair
from app.models.spot_work import SpotWork
from app.repositories.maintenance_plan import MaintenancePlanRepository
from app.schemas.maintenance_plan import MaintenancePlanCreate, MaintenancePlanUpdate

logger = logging.getLogger(__name__)


class MaintenancePlanService:
    def __init__(self, db: Session):
        self.repository = MaintenancePlanRepository(db)
    
    def _parse_date(self, date_value: Union[str, datetime, None]) -> Optional[datetime]:
        if date_value is None:
            return None
        if isinstance(date_value, datetime):
            return date_value
        if isinstance(date_value, str):
            try:
                return datetime.fromisoformat(date_value)
            except ValueError:
                try:
                    return datetime.strptime(date_value, '%Y-%m-%d')
                except ValueError:
                    raise ValueError(f'日期格式无效: {date_value}')
        return None
    
    def get_all(
        self, 
        page: int = 0, 
        size: int = 10, 
        plan_name: Optional[str] = None, 
        project_id: Optional[str] = None,
        equipment_name: Optional[str] = None,
        plan_status: Optional[str] = None,
        execution_status: Optional[str] = None,
        responsible_person: Optional[str] = None,
        project_name: Optional[str] = None,
        client_name: Optional[str] = None,
        plan_type: Optional[str] = None,
        responsible_person_filter: Optional[str] = None
    ) -> tuple[List[MaintenancePlan], int]:
        return self.repository.find_all(
            page, size, plan_name, project_id, equipment_name, 
            plan_status, execution_status, responsible_person,
            project_name, client_name, plan_type, responsible_person_filter
        )
    
    def get_by_id(self, id: int) -> MaintenancePlan:
        maintenance_plan = self.repository.find_by_id(id)
        if not maintenance_plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="维保计划不存在"
            )
        return maintenance_plan
    
    def get_by_plan_id(self, plan_id: str) -> MaintenancePlan:
        maintenance_plan = self.repository.find_by_plan_id(plan_id)
        if not maintenance_plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="维保计划不存在"
            )
        return maintenance_plan
    
    def get_by_project_id(self, project_id: str) -> List[MaintenancePlan]:
        return self.repository.find_by_project_id_list(project_id)
    
    def get_upcoming_maintenance(self, days: int = 7) -> List[MaintenancePlan]:
        return self.repository.find_upcoming_maintenance(days)
    
    def get_by_date_range(self, start_date, end_date) -> List[MaintenancePlan]:
        return self.repository.find_by_date_range(start_date, end_date)
    
    def create(self, dto: MaintenancePlanCreate) -> MaintenancePlan:
        logger.info(f"📥 [Service] 开始创建维保计划: plan_id={dto.plan_id}, plan_name={dto.plan_name}")

        if self.repository.exists_by_plan_id(dto.plan_id):
            logger.error(f"❌ [Service] 计划编号已存在: {dto.plan_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="计划编号已存在"
            )

        maintenance_plan = MaintenancePlan(
            plan_id=dto.plan_id,
            plan_name=dto.plan_name,
            project_id=dto.project_id,
            plan_type=dto.plan_type,
            equipment_id=dto.equipment_id,
            equipment_name=dto.equipment_name,
            equipment_model=dto.equipment_model,
            equipment_location=dto.equipment_location,
            plan_start_date=self._parse_date(dto.plan_start_date),
            plan_end_date=self._parse_date(dto.plan_end_date),
            execution_date=self._parse_date(dto.execution_date),
            next_maintenance_date=self._parse_date(dto.next_maintenance_date),
            responsible_person=dto.responsible_person,
            responsible_department=dto.responsible_department,
            contact_info=dto.contact_info,
            maintenance_content=dto.maintenance_content,
            maintenance_requirements=dto.maintenance_requirements,
            maintenance_standard=dto.maintenance_standard,
            plan_status=dto.plan_status,
            execution_status=dto.execution_status,
            completion_rate=dto.completion_rate,
            remarks=dto.remarks,
            inspection_items=dto.inspection_items
        )

        logger.info(f"📥 [Service] 准备保存到数据库: plan_id={maintenance_plan.plan_id}, plan_name={maintenance_plan.plan_name}")
        result = self.repository.create(maintenance_plan)
        logger.info(f"✅ [Service] 数据库保存成功: id={result.id}, plan_id={result.plan_id}")
        
        self._create_work_order_for_plan(result)
        
        return result
    
    def _create_work_order_for_plan(self, plan: MaintenancePlan) -> None:
        """
        根据维保计划自动创建对应的工单
        """
        try:
            from app.models.project_info import ProjectInfo
            
            project = self.repository.db.query(ProjectInfo).filter(
                ProjectInfo.project_id == plan.project_id
            ).first()
            
            client_name = project.client_name if project else plan.responsible_department
            
            inspection_id = f"XJ-{plan.project_id}-{plan.plan_start_date.strftime('%Y%m%d') if plan.plan_start_date else datetime.now().strftime('%Y%m%d')}"
            
            existing = self.repository.db.query(PeriodicInspection).filter(
                PeriodicInspection.inspection_id == inspection_id
            ).first()
            
            if existing:
                seq = 1
                while True:
                    inspection_id = f"XJ-{plan.project_id}-{plan.plan_start_date.strftime('%Y%m%d') if plan.plan_start_date else datetime.now().strftime('%Y%m%d')}-{seq:02d}"
                    if not self.repository.db.query(PeriodicInspection).filter(
                        PeriodicInspection.inspection_id == inspection_id
                    ).first():
                        break
                    seq += 1
            
            work_order = PeriodicInspection(
                inspection_id=inspection_id,
                plan_id=plan.plan_id,
                project_id=plan.project_id,
                project_name=plan.project_name or (project.project_name if project else ''),
                plan_start_date=plan.plan_start_date,
                plan_end_date=plan.plan_end_date,
                client_name=client_name,
                maintenance_personnel=plan.responsible_person,
                status='未进行',
                remarks=plan.remarks
            )
            
            self.repository.db.add(work_order)
            self.repository.db.commit()
            
            logger.info(f"✅ [Service] 自动创建工单成功: inspection_id={inspection_id}, plan_id={plan.plan_id}")
            
        except Exception as e:
            logger.error(f"❌ [Service] 创建工单失败: {str(e)}")
            self.repository.db.rollback()
    
    def update(self, id: int, dto: MaintenancePlanUpdate) -> MaintenancePlan:
        existing_plan = self.get_by_id(id)
        
        if existing_plan.plan_id != dto.plan_id and self.repository.exists_by_plan_id(dto.plan_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="计划编号已存在"
            )
        
        existing_plan.plan_id = dto.plan_id
        existing_plan.plan_name = dto.plan_name
        existing_plan.project_id = dto.project_id
        existing_plan.plan_type = dto.plan_type
        existing_plan.equipment_id = dto.equipment_id
        existing_plan.equipment_name = dto.equipment_name
        existing_plan.equipment_model = dto.equipment_model
        existing_plan.equipment_location = dto.equipment_location
        existing_plan.plan_start_date = self._parse_date(dto.plan_start_date)
        existing_plan.plan_end_date = self._parse_date(dto.plan_end_date)
        existing_plan.execution_date = self._parse_date(dto.execution_date)
        existing_plan.next_maintenance_date = self._parse_date(dto.next_maintenance_date)
        existing_plan.responsible_person = dto.responsible_person
        existing_plan.responsible_department = dto.responsible_department
        existing_plan.contact_info = dto.contact_info
        existing_plan.maintenance_content = dto.maintenance_content
        existing_plan.maintenance_requirements = dto.maintenance_requirements
        existing_plan.maintenance_standard = dto.maintenance_standard
        existing_plan.plan_status = dto.plan_status
        existing_plan.execution_status = dto.execution_status
        existing_plan.completion_rate = dto.completion_rate
        existing_plan.remarks = dto.remarks
        existing_plan.inspection_items = dto.inspection_items
        
        return self.repository.update(existing_plan)
    
    def delete(self, id: int) -> dict:
        """
        删除维保计划，并级联删除关联的工单数据
        返回删除统计信息
        """
        maintenance_plan = self.get_by_id(id)
        plan_id = maintenance_plan.plan_id
        
        logger.info(f"🗑️ [Service] 开始删除维保计划: id={id}, plan_id={plan_id}")
        
        deleted_stats = {
            'plan_id': plan_id,
            'periodic_inspections': 0,
            'temporary_repairs': 0,
            'spot_works': 0
        }
        
        try:
            deleted_stats['periodic_inspections'] = self.repository.db.query(PeriodicInspection).filter(
                PeriodicInspection.plan_id == plan_id
            ).delete(synchronize_session=False)
            
            deleted_stats['temporary_repairs'] = self.repository.db.query(TemporaryRepair).filter(
                TemporaryRepair.plan_id == plan_id
            ).delete(synchronize_session=False)
            
            deleted_stats['spot_works'] = self.repository.db.query(SpotWork).filter(
                SpotWork.plan_id == plan_id
            ).delete(synchronize_session=False)
            
            self.repository.delete(maintenance_plan)
            
            logger.info(f"✅ [Service] 维保计划删除成功: plan_id={plan_id}, "
                       f"定期巡检={deleted_stats['periodic_inspections']}, "
                       f"临时维修={deleted_stats['temporary_repairs']}, "
                       f"零星用工={deleted_stats['spot_works']}")
            
            return deleted_stats
            
        except Exception as e:
            logger.error(f"❌ [Service] 删除维保计划失败: plan_id={plan_id}, error={str(e)}")
            raise
    
    def update_execution_status(self, id: int, status: str) -> MaintenancePlan:
        maintenance_plan = self.repository.update_execution_status(id, status)
        if not maintenance_plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="维保计划不存在"
            )
        return maintenance_plan
    
    def update_completion_rate(self, id: int, rate: int) -> MaintenancePlan:
        if rate < 0 or rate > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="完成率必须在0-100之间"
            )
        maintenance_plan = self.repository.update_completion_rate(id, rate)
        if not maintenance_plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="维保计划不存在"
            )
        return maintenance_plan
    
    def get_all_unpaginated(self) -> List[MaintenancePlan]:
        return self.repository.find_all_unpaginated()

from typing import List, Optional, Union
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.work_plan import WorkPlan
from app.repositories.work_plan import WorkPlanRepository
from app.services.sync_service import SyncService
from pydantic import BaseModel


PLAN_TYPES = ['定期巡检', '临时维修', '零星用工']


class WorkPlanCreate(BaseModel):
    plan_id: str
    plan_type: str
    project_id: str
    project_name: str
    plan_start_date: Union[str, datetime]
    plan_end_date: Union[str, datetime]
    client_name: Optional[str] = None
    maintenance_personnel: Optional[str] = None
    status: Optional[str] = None
    filled_count: Optional[int] = 0
    remarks: Optional[str] = None


class WorkPlanUpdate(BaseModel):
    plan_id: str
    plan_type: str
    project_id: str
    project_name: str
    plan_start_date: Union[str, datetime]
    plan_end_date: Union[str, datetime]
    client_name: Optional[str] = None
    maintenance_personnel: Optional[str] = None
    status: str
    filled_count: Optional[int] = 0
    remarks: Optional[str] = None


class WorkPlanService:
    def __init__(self, db: Session):
        self.repository = WorkPlanRepository(db)
        self.sync_service = SyncService(db)
    
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
    
    def _get_date_value(self, date_field) -> Optional[datetime.date]:
        if date_field is None:
            return None
        if isinstance(date_field, datetime):
            return date_field.date()
        return date_field
    
    def get_all(
        self, 
        page: int = 0, 
        size: int = 10,
        plan_type: Optional[str] = None,
        project_name: Optional[str] = None,
        client_name: Optional[str] = None,
        status: Optional[str] = None,
        maintenance_personnel: Optional[str] = None
    ) -> tuple[List[WorkPlan], int]:
        return self.repository.find_all(
            page, size, plan_type, project_name, client_name, status, maintenance_personnel
        )
    
    def get_by_id(self, id: int) -> WorkPlan:
        work_plan = self.repository.find_by_id(id)
        if not work_plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="工作计划不存在"
            )
        return work_plan
    
    def get_by_plan_id(self, plan_id: str) -> WorkPlan:
        work_plan = self.repository.find_by_plan_id(plan_id)
        if not work_plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="工作计划不存在"
            )
        return work_plan
    
    def create(self, dto: WorkPlanCreate) -> WorkPlan:
        if dto.plan_type not in PLAN_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"工单类型必须是以下之一: {', '.join(PLAN_TYPES)}"
            )
        
        if self.repository.exists_by_plan_id(dto.plan_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="计划编号已存在"
            )
        
        work_plan = WorkPlan(
            plan_id=dto.plan_id,
            plan_type=dto.plan_type,
            project_id=dto.project_id,
            project_name=dto.project_name,
            plan_start_date=self._parse_date(dto.plan_start_date),
            plan_end_date=self._parse_date(dto.plan_end_date),
            client_name=dto.client_name,
            maintenance_personnel=dto.maintenance_personnel,
            status=dto.status or "未进行",
            filled_count=dto.filled_count or 0,
            remarks=dto.remarks
        )
        
        result = self.repository.create(work_plan)
        self.sync_service.sync_work_plan_to_order(result)
        return result
    
    def update(self, id: int, dto: WorkPlanUpdate) -> WorkPlan:
        existing_plan = self.get_by_id(id)
        
        if dto.plan_type not in PLAN_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"工单类型必须是以下之一: {', '.join(PLAN_TYPES)}"
            )
        
        if existing_plan.plan_id != dto.plan_id and self.repository.exists_by_plan_id(dto.plan_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="计划编号已存在"
            )
        
        existing_plan.plan_id = dto.plan_id
        existing_plan.plan_type = dto.plan_type
        existing_plan.project_id = dto.project_id
        existing_plan.project_name = dto.project_name
        existing_plan.plan_start_date = self._parse_date(dto.plan_start_date)
        existing_plan.plan_end_date = self._parse_date(dto.plan_end_date)
        existing_plan.client_name = dto.client_name
        existing_plan.maintenance_personnel = dto.maintenance_personnel
        existing_plan.status = dto.status
        existing_plan.filled_count = dto.filled_count or 0
        existing_plan.remarks = dto.remarks
        
        result = self.repository.update(existing_plan)
        self.sync_service.sync_work_plan_to_order(result)
        return result
    
    def delete(self, id: int) -> None:
        work_plan = self.get_by_id(id)
        self.sync_service.sync_work_plan_to_order(work_plan, is_delete=True)
        self.repository.delete(work_plan)
    
    def get_all_unpaginated(self, plan_type: Optional[str] = None) -> List[WorkPlan]:
        return self.repository.find_all_unpaginated(plan_type)
    
    def get_statistics(self, user_name: Optional[str] = None, is_manager: bool = False) -> dict:
        """
        获取统计数据
        
        临期工单：计划开始日期在未来7天内且未完成
        超期工单：计划结束日期已过且未完成
        """
        from app.repositories.periodic_inspection import PeriodicInspectionRepository
        from app.repositories.temporary_repair import TemporaryRepairRepository
        from app.repositories.spot_work import SpotWorkRepository
        
        today = datetime.now().date()
        year_start = datetime(today.year, 1, 1).date()
        
        inspection_repo = PeriodicInspectionRepository(self.repository.db)
        repair_repo = TemporaryRepairRepository(self.repository.db)
        spotwork_repo = SpotWorkRepository(self.repository.db)
        
        all_inspections = inspection_repo.find_all_unpaginated()
        all_repairs = repair_repo.find_all_unpaginated()
        all_spotworks = spotwork_repo.find_all_unpaginated()
        
        if not is_manager and user_name:
            all_inspections = [p for p in all_inspections if p.maintenance_personnel == user_name]
            all_repairs = [p for p in all_repairs if p.maintenance_personnel == user_name]
            all_spotworks = [p for p in all_spotworks if p.maintenance_personnel == user_name]
        
        expiring_soon = 0
        overdue = 0
        yearly_completed = 0
        
        all_orders = []
        for item in all_inspections:
            all_orders.append(('定期巡检', item))
        for item in all_repairs:
            all_orders.append(('临时维修', item))
        for item in all_spotworks:
            all_orders.append(('零星用工', item))
        
        for plan_type, order in all_orders:
            plan_start = self._get_date_value(order.plan_start_date)
            plan_end = self._get_date_value(order.plan_end_date)
            
            if order.status not in ['已完成', '已确认']:
                if plan_start:
                    if today <= plan_start <= today + timedelta(days=7):
                        expiring_soon += 1
                
                if plan_end:
                    if plan_end < today:
                        overdue += 1
            
            if order.status in ['已完成', '已确认'] and plan_end:
                if plan_end >= year_start:
                    yearly_completed += 1
        
        return {
            'expiringSoon': expiring_soon,
            'overdue': overdue,
            'yearlyCompleted': yearly_completed,
            'periodicInspection': len(all_inspections),
            'temporaryRepair': len(all_repairs),
            'spotWork': len(all_spotworks)
        }

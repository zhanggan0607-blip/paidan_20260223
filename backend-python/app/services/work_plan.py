from typing import List, Optional, Union
from fastapi import HTTPException, status
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.work_plan import WorkPlan
from app.repositories.work_plan import WorkPlanRepository
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
    remarks: Optional[str] = None


class WorkPlanService:
    def __init__(self, db: Session):
        self.repository = WorkPlanRepository(db)
    
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
        plan_type: Optional[str] = None,
        project_name: Optional[str] = None,
        client_name: Optional[str] = None,
        status: Optional[str] = None
    ) -> tuple[List[WorkPlan], int]:
        return self.repository.find_all(
            page, size, plan_type, project_name, client_name, status
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
                detail=f"计划类型必须是以下之一: {', '.join(PLAN_TYPES)}"
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
            remarks=dto.remarks
        )
        
        return self.repository.create(work_plan)
    
    def update(self, id: int, dto: WorkPlanUpdate) -> WorkPlan:
        existing_plan = self.get_by_id(id)
        
        if dto.plan_type not in PLAN_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"计划类型必须是以下之一: {', '.join(PLAN_TYPES)}"
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
        existing_plan.remarks = dto.remarks
        
        return self.repository.update(existing_plan)
    
    def delete(self, id: int) -> None:
        work_plan = self.get_by_id(id)
        self.repository.delete(work_plan)
    
    def get_all_unpaginated(self, plan_type: Optional[str] = None) -> List[WorkPlan]:
        return self.repository.find_all_unpaginated(plan_type)

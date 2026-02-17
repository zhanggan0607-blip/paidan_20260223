from typing import List, Optional, Union
from fastapi import HTTPException, status
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.spot_work import SpotWork
from app.repositories.spot_work import SpotWorkRepository
from app.utils.dictionary_helper import get_default_spot_work_status
from app.services.sync_service import SyncService, PLAN_TYPE_SPOTWORK
from pydantic import BaseModel


class SpotWorkCreate(BaseModel):
    work_id: str
    project_id: str
    project_name: str
    plan_start_date: Union[str, datetime]
    plan_end_date: Union[str, datetime]
    client_name: str
    maintenance_personnel: Optional[str] = None
    status: Optional[str] = None
    remarks: Optional[str] = None


class SpotWorkUpdate(BaseModel):
    work_id: str
    project_id: str
    project_name: str
    plan_start_date: Union[str, datetime]
    plan_end_date: Union[str, datetime]
    client_name: str
    maintenance_personnel: Optional[str] = None
    status: str
    remarks: Optional[str] = None


class SpotWorkService:
    def __init__(self, db: Session):
        self.repository = SpotWorkRepository(db)
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
    
    def get_all(
        self, 
        page: int = 0, 
        size: int = 10, 
        project_name: Optional[str] = None,
        client_name: Optional[str] = None,
        status: Optional[str] = None,
        maintenance_personnel: Optional[str] = None
    ) -> tuple[List[SpotWork], int]:
        return self.repository.find_all(
            page, size, project_name, client_name, status, maintenance_personnel
        )
    
    def get_by_id(self, id: int) -> SpotWork:
        work = self.repository.find_by_id(id)
        if not work:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用工单不存在"
            )
        return work
    
    def get_by_work_id(self, work_id: str) -> SpotWork:
        work = self.repository.find_by_work_id(work_id)
        if not work:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用工单不存在"
            )
        return work
    
    def create(self, dto: SpotWorkCreate) -> SpotWork:
        if self.repository.exists_by_work_id(dto.work_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用工单编号已存在"
            )
        
        default_status = get_default_spot_work_status(self.repository.db)
        
        work = SpotWork(
            work_id=dto.work_id,
            project_id=dto.project_id,
            project_name=dto.project_name,
            plan_start_date=self._parse_date(dto.plan_start_date),
            plan_end_date=self._parse_date(dto.plan_end_date),
            client_name=dto.client_name,
            maintenance_personnel=dto.maintenance_personnel,
            status=dto.status or default_status,
            remarks=dto.remarks
        )
        
        result = self.repository.create(work)
        self.sync_service.sync_order_to_work_plan(PLAN_TYPE_SPOTWORK, result)
        return result
    
    def update(self, id: int, dto: SpotWorkUpdate) -> SpotWork:
        existing_work = self.get_by_id(id)
        
        if existing_work.work_id != dto.work_id and self.repository.exists_by_work_id(dto.work_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用工单编号已存在"
            )
        
        existing_work.work_id = dto.work_id
        existing_work.project_id = dto.project_id
        existing_work.project_name = dto.project_name
        existing_work.plan_start_date = self._parse_date(dto.plan_start_date)
        existing_work.plan_end_date = self._parse_date(dto.plan_end_date)
        existing_work.client_name = dto.client_name
        existing_work.maintenance_personnel = dto.maintenance_personnel
        existing_work.status = dto.status
        existing_work.remarks = dto.remarks
        
        result = self.repository.update(existing_work)
        self.sync_service.sync_order_to_work_plan(PLAN_TYPE_SPOTWORK, result)
        return result
    
    def delete(self, id: int) -> None:
        work = self.get_by_id(id)
        self.sync_service.sync_order_to_work_plan(PLAN_TYPE_SPOTWORK, work, is_delete=True)
        self.repository.delete(work)
    
    def get_all_unpaginated(self) -> List[SpotWork]:
        return self.repository.find_all_unpaginated()

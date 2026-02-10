from typing import List, Optional, Union
from fastapi import HTTPException, status
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.periodic_inspection import PeriodicInspection
from app.repositories.periodic_inspection import PeriodicInspectionRepository
from app.schemas.periodic_inspection import PeriodicInspectionCreate, PeriodicInspectionUpdate


class PeriodicInspectionService:
    def __init__(self, db: Session):
        self.repository = PeriodicInspectionRepository(db)
    
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
        status: Optional[str] = None
    ) -> tuple[List[PeriodicInspection], int]:
        return self.repository.find_all(
            page, size, project_name, client_name, status
        )
    
    def get_by_id(self, id: int) -> PeriodicInspection:
        inspection = self.repository.find_by_id(id)
        if not inspection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="巡检单不存在"
            )
        return inspection
    
    def get_by_inspection_id(self, inspection_id: str) -> PeriodicInspection:
        inspection = self.repository.find_by_inspection_id(inspection_id)
        if not inspection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="巡检单不存在"
            )
        return inspection
    
    def create(self, dto: PeriodicInspectionCreate) -> PeriodicInspection:
        if self.repository.exists_by_inspection_id(dto.inspection_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="巡检单编号已存在"
            )
        
        inspection = PeriodicInspection(
            inspection_id=dto.inspection_id,
            project_id=dto.project_id,
            project_name=dto.project_name,
            plan_start_date=self._parse_date(dto.plan_start_date),
            plan_end_date=self._parse_date(dto.plan_end_date),
            client_name=dto.client_name,
            maintenance_personnel=dto.maintenance_personnel,
            status=dto.status,
            remarks=dto.remarks
        )
        
        return self.repository.create(inspection)
    
    def update(self, id: int, dto: PeriodicInspectionUpdate) -> PeriodicInspection:
        existing_inspection = self.get_by_id(id)
        
        if existing_inspection.inspection_id != dto.inspection_id and self.repository.exists_by_inspection_id(dto.inspection_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="巡检单编号已存在"
            )
        
        existing_inspection.inspection_id = dto.inspection_id
        existing_inspection.project_id = dto.project_id
        existing_inspection.project_name = dto.project_name
        existing_inspection.plan_start_date = self._parse_date(dto.plan_start_date)
        existing_inspection.plan_end_date = self._parse_date(dto.plan_end_date)
        existing_inspection.client_name = dto.client_name
        existing_inspection.maintenance_personnel = dto.maintenance_personnel
        existing_inspection.status = dto.status
        existing_inspection.remarks = dto.remarks
        
        return self.repository.update(existing_inspection)
    
    def delete(self, id: int) -> None:
        inspection = self.get_by_id(id)
        self.repository.delete(inspection)
    
    def get_all_unpaginated(self) -> List[PeriodicInspection]:
        return self.repository.find_all_unpaginated()

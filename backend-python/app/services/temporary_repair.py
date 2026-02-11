from typing import List, Optional, Union
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.temporary_repair import TemporaryRepair
from app.repositories.temporary_repair import TemporaryRepairRepository
from app.exceptions import NotFoundException, DuplicateException
from pydantic import BaseModel


class TemporaryRepairCreate(BaseModel):
    repair_id: str
    project_id: str
    project_name: str
    plan_start_date: Union[str, datetime]
    plan_end_date: Union[str, datetime]
    client_name: str
    maintenance_personnel: Optional[str] = None
    status: str = "未进行"
    remarks: Optional[str] = None


class TemporaryRepairUpdate(BaseModel):
    repair_id: str
    project_id: str
    project_name: str
    plan_start_date: Union[str, datetime]
    plan_end_date: Union[str, datetime]
    client_name: str
    maintenance_personnel: Optional[str] = None
    status: str
    remarks: Optional[str] = None


class TemporaryRepairService:
    def __init__(self, db: Session):
        self.repository = TemporaryRepairRepository(db)
    
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
    ) -> tuple[List[TemporaryRepair], int]:
        return self.repository.find_all(
            page, size, project_name, client_name, status
        )
    
    def get_by_id(self, id: int) -> TemporaryRepair:
        repair = self.repository.find_by_id(id)
        if not repair:
            raise NotFoundException("维修单不存在")
        return repair
    
    def get_by_repair_id(self, repair_id: str) -> TemporaryRepair:
        repair = self.repository.find_by_repair_id(repair_id)
        if not repair:
            raise NotFoundException("维修单不存在")
        return repair
    
    def create(self, dto: TemporaryRepairCreate) -> TemporaryRepair:
        if self.repository.exists_by_repair_id(dto.repair_id):
            raise DuplicateException("维修单编号已存在")
        
        repair = TemporaryRepair(
            repair_id=dto.repair_id,
            project_id=dto.project_id,
            project_name=dto.project_name,
            plan_start_date=self._parse_date(dto.plan_start_date),
            plan_end_date=self._parse_date(dto.plan_end_date),
            client_name=dto.client_name,
            maintenance_personnel=dto.maintenance_personnel,
            status=dto.status,
            remarks=dto.remarks
        )
        
        return self.repository.create(repair)
    
    def update(self, id: int, dto: TemporaryRepairUpdate) -> TemporaryRepair:
        existing_repair = self.get_by_id(id)
        
        if existing_repair.repair_id != dto.repair_id and self.repository.exists_by_repair_id(dto.repair_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="维修单编号已存在"
            )
        
        existing_repair.repair_id = dto.repair_id
        existing_repair.project_id = dto.project_id
        existing_repair.project_name = dto.project_name
        existing_repair.plan_start_date = self._parse_date(dto.plan_start_date)
        existing_repair.plan_end_date = self._parse_date(dto.plan_end_date)
        existing_repair.client_name = dto.client_name
        existing_repair.maintenance_personnel = dto.maintenance_personnel
        existing_repair.status = dto.status
        existing_repair.remarks = dto.remarks
        
        return self.repository.update(existing_repair)
    
    def delete(self, id: int) -> None:
        repair = self.get_by_id(id)
        self.repository.delete(repair)
    
    def get_all_unpaginated(self) -> List[TemporaryRepair]:
        return self.repository.find_all_unpaginated()

from typing import List, Optional, Union
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.temporary_repair import TemporaryRepair
from app.repositories.temporary_repair import TemporaryRepairRepository
from app.exceptions import NotFoundException, DuplicateException
from app.utils.dictionary_helper import get_default_temporary_repair_status
from app.services.sync_service import SyncService, PLAN_TYPE_REPAIR
from app.schemas.temporary_repair import TemporaryRepairCreate, TemporaryRepairUpdate
from app.utils.date_utils import parse_datetime
import json


class TemporaryRepairService:
    def __init__(self, db: Session):
        self.repository = TemporaryRepairRepository(db)
        self.sync_service = SyncService(db)
    
    def _parse_date(self, date_value: Union[str, datetime, None]) -> Optional[datetime]:
        return parse_datetime(date_value)
    
    def get_all(
        self, 
        page: int = 0, 
        size: int = 10, 
        project_name: Optional[str] = None,
        repair_id: Optional[str] = None,
        status: Optional[str] = None,
        maintenance_personnel: Optional[str] = None
    ) -> tuple[List[TemporaryRepair], int]:
        return self.repository.find_all(
            page, size, project_name, repair_id, status, maintenance_personnel
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
        
        default_status = get_default_temporary_repair_status(self.repository.db)
        
        repair = TemporaryRepair(
            repair_id=dto.repair_id,
            project_id=dto.project_id,
            project_name=dto.project_name,
            plan_start_date=self._parse_date(dto.plan_start_date),
            plan_end_date=self._parse_date(dto.plan_end_date),
            client_name=dto.client_name,
            maintenance_personnel=dto.maintenance_personnel,
            status=dto.status or default_status,
            remarks=dto.remarks
        )
        
        result = self.repository.create(repair)
        self.sync_service.sync_order_to_work_plan(PLAN_TYPE_REPAIR, result)
        return result
    
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
        existing_repair.fault_description = dto.fault_description
        existing_repair.solution = dto.solution
        existing_repair.photos = json.dumps(dto.photos) if dto.photos else None
        existing_repair.signature = dto.signature
        existing_repair.execution_date = self._parse_date(dto.execution_date)
        
        result = self.repository.update(existing_repair)
        self.sync_service.sync_order_to_work_plan(PLAN_TYPE_REPAIR, result)
        return result
    
    def partial_update(self, id: int, dto) -> TemporaryRepair:
        existing_repair = self.get_by_id(id)
        
        if dto.repair_id is not None:
            if existing_repair.repair_id != dto.repair_id and self.repository.exists_by_repair_id(dto.repair_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="维修单编号已存在"
                )
            existing_repair.repair_id = dto.repair_id
        if dto.project_id is not None:
            existing_repair.project_id = dto.project_id
        if dto.project_name is not None:
            existing_repair.project_name = dto.project_name
        if dto.plan_start_date is not None:
            existing_repair.plan_start_date = self._parse_date(dto.plan_start_date)
        if dto.plan_end_date is not None:
            existing_repair.plan_end_date = self._parse_date(dto.plan_end_date)
        if dto.client_name is not None:
            existing_repair.client_name = dto.client_name
        if dto.maintenance_personnel is not None:
            existing_repair.maintenance_personnel = dto.maintenance_personnel
        if dto.status is not None:
            existing_repair.status = dto.status
            if dto.status in ['已确认', '已完成'] and not existing_repair.actual_completion_date:
                existing_repair.actual_completion_date = datetime.now()
        if dto.remarks is not None:
            existing_repair.remarks = dto.remarks
        if hasattr(dto, 'fault_description') and dto.fault_description is not None:
            existing_repair.fault_description = dto.fault_description
        if hasattr(dto, 'solution') and dto.solution is not None:
            existing_repair.solution = dto.solution
        if hasattr(dto, 'photos') and dto.photos is not None:
            existing_repair.photos = json.dumps(dto.photos)
        if hasattr(dto, 'signature') and dto.signature is not None:
            existing_repair.signature = dto.signature
        if hasattr(dto, 'execution_date') and dto.execution_date is not None:
            existing_repair.execution_date = self._parse_date(dto.execution_date)
        
        result = self.repository.update(existing_repair)
        self.sync_service.sync_order_to_work_plan(PLAN_TYPE_REPAIR, result)
        return result
    
    def delete(self, id: int) -> None:
        repair = self.get_by_id(id)
        self.sync_service.sync_order_to_work_plan(PLAN_TYPE_REPAIR, repair, is_delete=True)
        self.repository.delete(repair)
    
    def get_all_unpaginated(self) -> List[TemporaryRepair]:
        return self.repository.find_all_unpaginated()

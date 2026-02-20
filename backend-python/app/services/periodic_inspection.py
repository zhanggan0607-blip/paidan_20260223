from typing import List, Optional, Union
from fastapi import HTTPException, status
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
import json
from app.models.periodic_inspection import PeriodicInspection
from app.models.periodic_inspection_record import PeriodicInspectionRecord
from app.models.maintenance_plan import MaintenancePlan
from app.repositories.periodic_inspection import PeriodicInspectionRepository
from app.schemas.periodic_inspection import PeriodicInspectionCreate, PeriodicInspectionUpdate, PeriodicInspectionPartialUpdate
from app.utils.dictionary_helper import get_default_periodic_inspection_status
from app.services.sync_service import SyncService, PLAN_TYPE_INSPECTION


class PeriodicInspectionService:
    def __init__(self, db: Session):
        self.repository = PeriodicInspectionRepository(db)
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
        inspection_id: Optional[str] = None,
        status: Optional[str] = None,
        maintenance_personnel: Optional[str] = None
    ) -> tuple[List[PeriodicInspection], int]:
        return self.repository.find_all(
            page, size, project_name, client_name, inspection_id, status, maintenance_personnel
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
        
        default_status = get_default_periodic_inspection_status(self.repository.db)
        
        inspection = PeriodicInspection(
            inspection_id=dto.inspection_id,
            project_id=dto.project_id,
            project_name=dto.project_name,
            plan_start_date=self._parse_date(dto.plan_start_date),
            plan_end_date=self._parse_date(dto.plan_end_date),
            client_name=dto.client_name,
            maintenance_personnel=dto.maintenance_personnel,
            status=dto.status or default_status,
            filled_count=dto.filled_count or 0,
            execution_result=dto.execution_result,
            remarks=dto.remarks
        )
        
        result = self.repository.create(inspection)
        self.sync_service.sync_order_to_work_plan(PLAN_TYPE_INSPECTION, result)
        return result
    
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
        existing_inspection.filled_count = dto.filled_count or 0
        existing_inspection.total_count = dto.total_count or 5
        existing_inspection.execution_result = dto.execution_result
        existing_inspection.remarks = dto.remarks
        if dto.signature is not None:
            existing_inspection.signature = dto.signature
        
        result = self.repository.update(existing_inspection)
        self.sync_service.sync_order_to_work_plan(PLAN_TYPE_INSPECTION, result)
        return result
    
    def delete(self, id: int) -> None:
        inspection = self.get_by_id(id)
        self.sync_service.sync_order_to_work_plan(PLAN_TYPE_INSPECTION, inspection, is_delete=True)
        self.repository.delete(inspection)
    
    def partial_update(self, id: int, dto: PeriodicInspectionPartialUpdate) -> PeriodicInspection:
        existing_inspection = self.get_by_id(id)
        
        if dto.signature is not None:
            if dto.signature == '':
                existing_inspection.signature = None
            else:
                existing_inspection.signature = dto.signature
        if dto.execution_result is not None:
            existing_inspection.execution_result = dto.execution_result
        if dto.remarks is not None:
            existing_inspection.remarks = dto.remarks
        if dto.status is not None:
            existing_inspection.status = dto.status
            if dto.status in ['已确认', '已完成'] and not existing_inspection.actual_completion_date:
                existing_inspection.actual_completion_date = datetime.now()
        
        result = self.repository.update(existing_inspection)
        self.sync_service.sync_order_to_work_plan(PLAN_TYPE_INSPECTION, result)
        return result
    
    def get_all_unpaginated(self) -> List[PeriodicInspection]:
        return self.repository.find_all_unpaginated()
    
    def get_inspection_counts(self, inspection_id: str, project_id: str, plan_start_date: datetime, plan_end_date: datetime) -> dict:
        """
        计算巡检单的已填写数量和总数量
        统计3级节点（inspection_content）的数量
        总数量：该巡检单对应的不同3级节点数量
        已填写数量：已处理的3级节点数量
        """
        db = self.repository.db
        
        records = db.query(PeriodicInspectionRecord).filter(
            PeriodicInspectionRecord.inspection_id == inspection_id
        ).all()
        
        if records:
            unique_items = {}
            for record in records:
                key = record.inspection_content or record.item_name
                if key not in unique_items:
                    unique_items[key] = {
                        'inspected': False
                    }
                if record.inspected:
                    unique_items[key]['inspected'] = True
            
            total_count = len(unique_items)
            filled_count = sum(1 for item in unique_items.values() if item['inspected'])
        else:
            total_count = self._get_total_count_from_plans(db, project_id, plan_start_date, plan_end_date)
            filled_count = 0
        
        return {
            'total_count': total_count,
            'filled_count': filled_count
        }
    
    def _get_total_count_from_plans(self, db: Session, project_id: str, plan_start_date: datetime, plan_end_date: datetime) -> int:
        """
        从维保计划中获取3级节点总数
        """
        if not project_id or not plan_start_date or not plan_end_date:
            return 0
        
        try:
            plans = db.query(MaintenancePlan).filter(
                MaintenancePlan.project_id == project_id
            ).all()
            
            order_start = plan_start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            order_end = plan_end_date.replace(hour=0, minute=0, second=0, microsecond=0)
            
            unique_items = set()
            for plan in plans:
                if not plan.plan_start_date or not plan.plan_end_date:
                    continue
                plan_start = plan.plan_start_date.replace(hour=0, minute=0, second=0, microsecond=0)
                plan_end = plan.plan_end_date.replace(hour=0, minute=0, second=0, microsecond=0)
                
                if order_start <= plan_end and order_end >= plan_start:
                    if plan.inspection_items:
                        try:
                            items = json.loads(plan.inspection_items)
                            for item in items:
                                inspection_content = item.get('inspection_content', '')
                                if inspection_content:
                                    unique_items.add(inspection_content)
                        except:
                            pass
            
            return len(unique_items)
        except Exception as e:
            print(f"Error getting total count from plans: {e}")
            return 0

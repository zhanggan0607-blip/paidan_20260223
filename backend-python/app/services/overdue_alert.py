from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.periodic_inspection import PeriodicInspection
from app.models.temporary_repair import TemporaryRepair
from app.models.spot_work import SpotWork
from app.models.maintenance_plan import MaintenancePlan
from app.repositories.periodic_inspection import PeriodicInspectionRepository
from app.config import OverdueAlertConfig


class OverdueAlertService:
    def __init__(self, db: Session):
        self.db = db
        self.periodic_inspection_repo = PeriodicInspectionRepository(db)
    
    def get_overdue_items(
        self,
        project_name: Optional[str] = None,
        client_name: Optional[str] = None,
        work_order_type: Optional[str] = None,
        page: int = 0,
        size: int = 10
    ) -> tuple[List[dict], int]:
        today = datetime.now()
        overdue_items = []
        
        if work_order_type is None or work_order_type == '定期巡检':
            periodic_inspections = self.periodic_inspection_repo.find_all(
                page=page,
                size=size,
                project_name=project_name,
                client_name=client_name,
                status=None
            )
            
            for inspection in periodic_inspections[0]:
                if inspection.status not in OverdueAlertConfig.VALID_STATUSES:
                    continue
                
                if inspection.plan_end_date and inspection.plan_end_date < today:
                    overdue_days = (today - inspection.plan_end_date).days
                    if overdue_days >= OverdueAlertConfig.OVERDUE_THRESHOLD_DAYS:
                        item = {
                            'id': str(inspection.id),
                            'workOrderNo': inspection.inspection_id,
                            'project_id': inspection.project_id,
                            'projectName': inspection.project_name,
                            'customerName': inspection.client_name,
                            'workOrderType': '定期巡检',
                            'planEndDate': inspection.plan_end_date.isoformat() if inspection.plan_end_date else None,
                            'workOrderStatus': inspection.status,
                            'overdueDays': overdue_days,
                            'executor': inspection.maintenance_personnel
                        }
                        overdue_items.append(item)
        
        if work_order_type is None or work_order_type == '临时维修':
            from app.repositories.temporary_repair import TemporaryRepairRepository
            temp_repo = TemporaryRepairRepository(self.db)
            temporary_repairs, _ = temp_repo.find_all(
                page=page,
                size=size,
                project_name=project_name,
                client_name=client_name,
                status=None
            )
            
            for repair in temporary_repairs:
                if repair.status not in OverdueAlertConfig.VALID_STATUSES:
                    continue
                
                if repair.plan_end_date and repair.plan_end_date < today:
                    overdue_days = (today - repair.plan_end_date).days
                    if overdue_days >= OverdueAlertConfig.OVERDUE_THRESHOLD_DAYS:
                        item = {
                            'id': str(repair.id),
                            'workOrderNo': repair.repair_id,
                            'project_id': repair.project_id,
                            'projectName': repair.project_name,
                            'customerName': repair.client_name,
                            'workOrderType': '临时维修',
                            'planEndDate': repair.plan_end_date.isoformat() if repair.plan_end_date else None,
                            'workOrderStatus': repair.status,
                            'overdueDays': overdue_days,
                            'executor': repair.maintenance_personnel
                        }
                        overdue_items.append(item)
        
        if work_order_type is None or work_order_type == '零星用工':
            from app.repositories.spot_work import SpotWorkRepository
            spot_repo = SpotWorkRepository(self.db)
            spot_works, _ = spot_repo.find_all(
                page=page,
                size=size,
                project_name=project_name,
                client_name=client_name,
                status=None
            )
            
            for work in spot_works:
                if work.status not in OverdueAlertConfig.VALID_STATUSES:
                    continue
                
                if work.plan_end_date and work.plan_end_date < today:
                    overdue_days = (today - work.plan_end_date).days
                    if overdue_days >= OverdueAlertConfig.OVERDUE_THRESHOLD_DAYS:
                        item = {
                            'id': str(work.id),
                            'workOrderNo': work.work_id,
                            'project_id': work.project_id,
                            'projectName': work.project_name,
                            'customerName': work.client_name,
                            'workOrderType': '零星用工',
                            'planEndDate': work.plan_end_date.isoformat() if work.plan_end_date else None,
                            'workOrderStatus': work.status,
                            'overdueDays': overdue_days,
                            'executor': work.maintenance_personnel
                        }
                        overdue_items.append(item)
        
        if work_order_type is None or work_order_type == '维保计划':
            from app.repositories.maintenance_plan import MaintenancePlanRepository
            maint_repo = MaintenancePlanRepository(self.db)
            maintenance_plans = maint_repo.find_all_unpaginated()
            
            for plan in maintenance_plans:
                if plan.plan_status not in OverdueAlertConfig.VALID_STATUSES:
                    continue
                
                if plan.plan_end_date and plan.plan_end_date < today:
                    overdue_days = (today - plan.plan_end_date).days
                    if overdue_days >= OverdueAlertConfig.OVERDUE_THRESHOLD_DAYS:
                        if project_name and project_name.lower() not in plan.plan_name.lower():
                            continue
                        item = {
                            'id': str(plan.id),
                            'workOrderNo': plan.plan_id,
                            'project_id': plan.project_id,
                            'projectName': plan.plan_name,
                            'customerName': plan.responsible_department,
                            'workOrderType': '维保计划',
                            'planEndDate': plan.plan_end_date.isoformat() if plan.plan_end_date else None,
                            'workOrderStatus': plan.plan_status,
                            'overdueDays': overdue_days,
                            'executor': plan.responsible_person
                        }
                        overdue_items.append(item)
        
        total = len(overdue_items)
        
        return overdue_items, total

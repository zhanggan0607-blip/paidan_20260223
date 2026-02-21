"""
工单与工作计划同步服务
实现三种工单表(PeriodicInspection, TemporaryRepair, SpotWork)与WorkPlan表之间的双向同步
同时实现MaintenancePlan与WorkPlan之间的双向同步
"""
from typing import Optional, Union
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.work_plan import WorkPlan
from app.models.maintenance_plan import MaintenancePlan
from app.models.periodic_inspection import PeriodicInspection
from app.models.temporary_repair import TemporaryRepair
from app.models.spot_work import SpotWork
from app.repositories.work_plan import WorkPlanRepository
from app.repositories.maintenance_plan import MaintenancePlanRepository
from app.repositories.periodic_inspection import PeriodicInspectionRepository
from app.repositories.temporary_repair import TemporaryRepairRepository
from app.repositories.spot_work import SpotWorkRepository
from app.utils.date_utils import parse_datetime
import logging

logger = logging.getLogger(__name__)

PLAN_TYPE_INSPECTION = '定期巡检'
PLAN_TYPE_REPAIR = '临时维修'
PLAN_TYPE_SPOTWORK = '零星用工'


class SyncService:
    """
    工单与工作计划同步服务
    负责维护三种工单表与WorkPlan表之间的数据一致性
    同时维护MaintenancePlan与WorkPlan之间的数据一致性
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.work_plan_repo = WorkPlanRepository(db)
        self.maintenance_plan_repo = MaintenancePlanRepository(db)
        self.inspection_repo = PeriodicInspectionRepository(db)
        self.repair_repo = TemporaryRepairRepository(db)
        self.spotwork_repo = SpotWorkRepository(db)
    
    def _parse_date(self, date_value: Union[str, datetime, None]) -> Optional[datetime]:
        """解析日期值"""
        return parse_datetime(date_value)
    
    def _get_plan_id_by_type(self, order_type: str, order) -> str:
        """根据工单类型获取工单编号"""
        if order_type == PLAN_TYPE_INSPECTION:
            return order.inspection_id
        elif order_type == PLAN_TYPE_REPAIR:
            return order.repair_id
        elif order_type == PLAN_TYPE_SPOTWORK:
            return order.work_id
        return ''
    
    def sync_order_to_work_plan(self, order_type: str, order, is_delete: bool = False) -> Optional[WorkPlan]:
        """
        将工单数据同步到WorkPlan表
        
        Args:
            order_type: 工单类型 (定期巡检/临时维修/零星用工)
            order: 工单对象 (PeriodicInspection/TemporaryRepair/SpotWork)
            is_delete: 是否为删除操作
        
        Returns:
            同步后的WorkPlan对象，删除操作返回None
        """
        plan_id = self._get_plan_id_by_type(order_type, order)
        
        if is_delete:
            existing_plan = self.work_plan_repo.find_by_plan_id(plan_id)
            if existing_plan:
                self.work_plan_repo.delete(existing_plan)
                logger.info(f"同步删除WorkPlan: plan_id={plan_id}, type={order_type}")
            return None
        
        existing_plan = self.work_plan_repo.find_by_plan_id(plan_id)
        
        if existing_plan:
            existing_plan.plan_type = order_type
            existing_plan.project_id = order.project_id
            existing_plan.project_name = order.project_name
            existing_plan.plan_start_date = order.plan_start_date
            existing_plan.plan_end_date = order.plan_end_date
            existing_plan.client_name = order.client_name
            existing_plan.maintenance_personnel = order.maintenance_personnel
            existing_plan.status = order.status
            existing_plan.filled_count = getattr(order, 'filled_count', 0) or 0
            existing_plan.total_count = getattr(order, 'total_count', 5) or 5
            existing_plan.remarks = order.remarks
            
            result = self.work_plan_repo.update(existing_plan)
            logger.info(f"同步更新WorkPlan: plan_id={plan_id}, type={order_type}")
            return result
        else:
            new_plan = WorkPlan(
                plan_id=plan_id,
                plan_type=order_type,
                project_id=order.project_id,
                project_name=order.project_name,
                plan_start_date=order.plan_start_date,
                plan_end_date=order.plan_end_date,
                client_name=order.client_name,
                maintenance_personnel=order.maintenance_personnel,
                status=order.status,
                filled_count=getattr(order, 'filled_count', 0) or 0,
                total_count=getattr(order, 'total_count', 5) or 5,
                remarks=order.remarks
            )
            
            result = self.work_plan_repo.create(new_plan)
            logger.info(f"同步创建WorkPlan: plan_id={plan_id}, type={order_type}")
            return result
    
    def sync_work_plan_to_order(self, work_plan: WorkPlan, is_delete: bool = False):
        """
        将WorkPlan数据同步到对应的工单表
        
        Args:
            work_plan: WorkPlan对象
            is_delete: 是否为删除操作
        
        Returns:
            同步后的工单对象，删除操作返回None
        """
        plan_type = work_plan.plan_type
        plan_id = work_plan.plan_id
        
        if is_delete:
            if plan_type == PLAN_TYPE_INSPECTION:
                existing = self.inspection_repo.find_by_inspection_id(plan_id)
                if existing:
                    self.inspection_repo.delete(existing)
                    logger.info(f"同步删除PeriodicInspection: inspection_id={plan_id}")
            elif plan_type == PLAN_TYPE_REPAIR:
                existing = self.repair_repo.find_by_repair_id(plan_id)
                if existing:
                    self.repair_repo.delete(existing)
                    logger.info(f"同步删除TemporaryRepair: repair_id={plan_id}")
            elif plan_type == PLAN_TYPE_SPOTWORK:
                existing = self.spotwork_repo.find_by_work_id(plan_id)
                if existing:
                    self.spotwork_repo.delete(existing)
                    logger.info(f"同步删除SpotWork: work_id={plan_id}")
            return None
        
        if plan_type == PLAN_TYPE_INSPECTION:
            return self._sync_to_inspection(work_plan)
        elif plan_type == PLAN_TYPE_REPAIR:
            return self._sync_to_repair(work_plan)
        elif plan_type == PLAN_TYPE_SPOTWORK:
            return self._sync_to_spotwork(work_plan)
        
        return None
    
    def _sync_to_inspection(self, work_plan: WorkPlan) -> PeriodicInspection:
        """同步到定期巡检表"""
        existing = self.inspection_repo.find_by_inspection_id(work_plan.plan_id)
        
        if existing:
            existing.project_id = work_plan.project_id
            existing.project_name = work_plan.project_name
            existing.plan_start_date = work_plan.plan_start_date
            existing.plan_end_date = work_plan.plan_end_date
            existing.client_name = work_plan.client_name
            existing.maintenance_personnel = work_plan.maintenance_personnel
            existing.status = work_plan.status
            existing.filled_count = work_plan.filled_count or 0
            existing.remarks = work_plan.remarks
            
            result = self.inspection_repo.update(existing)
            logger.info(f"同步更新PeriodicInspection: inspection_id={work_plan.plan_id}")
            return result
        else:
            new_inspection = PeriodicInspection(
                inspection_id=work_plan.plan_id,
                project_id=work_plan.project_id,
                project_name=work_plan.project_name,
                plan_start_date=work_plan.plan_start_date,
                plan_end_date=work_plan.plan_end_date,
                client_name=work_plan.client_name,
                maintenance_personnel=work_plan.maintenance_personnel,
                status=work_plan.status,
                filled_count=work_plan.filled_count or 0,
                remarks=work_plan.remarks
            )
            
            result = self.inspection_repo.create(new_inspection)
            logger.info(f"同步创建PeriodicInspection: inspection_id={work_plan.plan_id}")
            return result
    
    def _sync_to_repair(self, work_plan: WorkPlan) -> TemporaryRepair:
        """同步到临时维修表"""
        existing = self.repair_repo.find_by_repair_id(work_plan.plan_id)
        
        if existing:
            existing.project_id = work_plan.project_id
            existing.project_name = work_plan.project_name
            existing.plan_start_date = work_plan.plan_start_date
            existing.plan_end_date = work_plan.plan_end_date
            existing.client_name = work_plan.client_name
            existing.maintenance_personnel = work_plan.maintenance_personnel
            existing.status = work_plan.status
            existing.remarks = work_plan.remarks
            
            result = self.repair_repo.update(existing)
            logger.info(f"同步更新TemporaryRepair: repair_id={work_plan.plan_id}")
            return result
        else:
            new_repair = TemporaryRepair(
                repair_id=work_plan.plan_id,
                project_id=work_plan.project_id,
                project_name=work_plan.project_name,
                plan_start_date=work_plan.plan_start_date,
                plan_end_date=work_plan.plan_end_date,
                client_name=work_plan.client_name,
                maintenance_personnel=work_plan.maintenance_personnel,
                status=work_plan.status,
                remarks=work_plan.remarks
            )
            
            result = self.repair_repo.create(new_repair)
            logger.info(f"同步创建TemporaryRepair: repair_id={work_plan.plan_id}")
            return result
    
    def _sync_to_spotwork(self, work_plan: WorkPlan) -> SpotWork:
        """同步到零星用工表"""
        existing = self.spotwork_repo.find_by_work_id(work_plan.plan_id)
        
        if existing:
            existing.project_id = work_plan.project_id
            existing.project_name = work_plan.project_name
            existing.plan_start_date = work_plan.plan_start_date
            existing.plan_end_date = work_plan.plan_end_date
            existing.client_name = work_plan.client_name
            existing.maintenance_personnel = work_plan.maintenance_personnel
            existing.status = work_plan.status
            existing.remarks = work_plan.remarks
            
            result = self.spotwork_repo.update(existing)
            logger.info(f"同步更新SpotWork: work_id={work_plan.plan_id}")
            return result
        else:
            new_spotwork = SpotWork(
                work_id=work_plan.plan_id,
                project_id=work_plan.project_id,
                project_name=work_plan.project_name,
                plan_start_date=work_plan.plan_start_date,
                plan_end_date=work_plan.plan_end_date,
                client_name=work_plan.client_name,
                maintenance_personnel=work_plan.maintenance_personnel,
                status=work_plan.status,
                remarks=work_plan.remarks
            )
            
            result = self.spotwork_repo.create(new_spotwork)
            logger.info(f"同步创建SpotWork: work_id={work_plan.plan_id}")
            return result

    def sync_maintenance_plan_to_work_plan(self, maintenance_plan: MaintenancePlan, is_delete: bool = False) -> Optional[WorkPlan]:
        """
        将MaintenancePlan数据同步到WorkPlan表
        
        Args:
            maintenance_plan: MaintenancePlan对象
            is_delete: 是否为删除操作
        
        Returns:
            同步后的WorkPlan对象，删除操作返回None
        """
        plan_id = maintenance_plan.plan_id
        
        if is_delete:
            existing_plan = self.work_plan_repo.find_by_plan_id(plan_id)
            if existing_plan:
                self.work_plan_repo.delete(existing_plan)
                logger.info(f"同步删除WorkPlan (from MaintenancePlan): plan_id={plan_id}")
            return None
        
        existing_plan = self.work_plan_repo.find_by_plan_id(plan_id)
        
        if existing_plan:
            existing_plan.plan_name = maintenance_plan.plan_name
            existing_plan.plan_type = maintenance_plan.plan_type
            existing_plan.project_id = maintenance_plan.project_id
            existing_plan.project_name = maintenance_plan.project_name or existing_plan.project_name
            existing_plan.plan_start_date = maintenance_plan.plan_start_date
            existing_plan.plan_end_date = maintenance_plan.plan_end_date
            existing_plan.maintenance_personnel = maintenance_plan.maintenance_personnel
            existing_plan.status = maintenance_plan.status
            existing_plan.filled_count = maintenance_plan.filled_count or 0
            existing_plan.total_count = maintenance_plan.total_count or 5
            existing_plan.remarks = maintenance_plan.remarks
            
            result = self.work_plan_repo.update(existing_plan)
            logger.info(f"同步更新WorkPlan (from MaintenancePlan): plan_id={plan_id}")
            return result
        else:
            client_name = ''
            if maintenance_plan.project:
                client_name = maintenance_plan.project.client_name or ''
            
            new_plan = WorkPlan(
                plan_id=plan_id,
                plan_name=maintenance_plan.plan_name,
                plan_type=maintenance_plan.plan_type,
                project_id=maintenance_plan.project_id,
                project_name=maintenance_plan.project_name,
                plan_start_date=maintenance_plan.plan_start_date,
                plan_end_date=maintenance_plan.plan_end_date,
                client_name=client_name,
                maintenance_personnel=maintenance_plan.maintenance_personnel,
                status=maintenance_plan.status,
                filled_count=maintenance_plan.filled_count or 0,
                total_count=maintenance_plan.total_count or 5,
                remarks=maintenance_plan.remarks
            )
            
            result = self.work_plan_repo.create(new_plan)
            logger.info(f"同步创建WorkPlan (from MaintenancePlan): plan_id={plan_id}")
            return result

    def sync_work_plan_to_maintenance_plan(self, work_plan: WorkPlan, is_delete: bool = False) -> Optional[MaintenancePlan]:
        """
        将WorkPlan数据同步到MaintenancePlan表
        
        Args:
            work_plan: WorkPlan对象
            is_delete: 是否为删除操作
        
        Returns:
            同步后的MaintenancePlan对象，删除操作返回None
        """
        plan_id = work_plan.plan_id
        
        if is_delete:
            existing_plan = self.maintenance_plan_repo.find_by_plan_id(plan_id)
            if existing_plan:
                self.maintenance_plan_repo.delete(existing_plan)
                logger.info(f"同步删除MaintenancePlan (from WorkPlan): plan_id={plan_id}")
            return None
        
        existing_plan = self.maintenance_plan_repo.find_by_plan_id(plan_id)
        
        if existing_plan:
            existing_plan.plan_name = work_plan.plan_name or existing_plan.plan_name
            existing_plan.plan_type = work_plan.plan_type
            existing_plan.project_id = work_plan.project_id
            existing_plan.project_name = work_plan.project_name
            existing_plan.plan_start_date = work_plan.plan_start_date
            existing_plan.plan_end_date = work_plan.plan_end_date
            existing_plan.maintenance_personnel = work_plan.maintenance_personnel
            existing_plan.status = work_plan.status
            existing_plan.filled_count = work_plan.filled_count or 0
            existing_plan.total_count = work_plan.total_count or 5
            existing_plan.remarks = work_plan.remarks
            
            result = self.maintenance_plan_repo.update(existing_plan)
            logger.info(f"同步更新MaintenancePlan (from WorkPlan): plan_id={plan_id}")
            return result
        else:
            new_plan = MaintenancePlan(
                plan_id=plan_id,
                plan_name=work_plan.plan_name or work_plan.project_name,
                project_id=work_plan.project_id,
                project_name=work_plan.project_name,
                plan_type=work_plan.plan_type,
                equipment_id='DEFAULT',
                equipment_name='默认设备',
                plan_start_date=work_plan.plan_start_date,
                plan_end_date=work_plan.plan_end_date,
                maintenance_personnel=work_plan.maintenance_personnel,
                maintenance_content='待填写',
                plan_status='待执行',
                status=work_plan.status,
                filled_count=work_plan.filled_count or 0,
                total_count=work_plan.total_count or 5,
                remarks=work_plan.remarks
            )
            
            result = self.maintenance_plan_repo.create(new_plan)
            logger.info(f"同步创建MaintenancePlan (from WorkPlan): plan_id={plan_id}")
            return result

from typing import List, Optional
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.periodic_inspection import PeriodicInspection
from app.models.temporary_repair import TemporaryRepair
from app.models.spot_work import SpotWork
from app.config import OverdueAlertConfig
import logging

logger = logging.getLogger(__name__)


class ExpiringSoonService:
    """
    临期工单提醒服务
    查询所有计划开始日期在未来7天内且状态不是"已完成"的工单
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_expiring_items(
        self,
        project_name: Optional[str] = None,
        client_name: Optional[str] = None,
        work_order_type: Optional[str] = None,
        page: int = 0,
        size: int = 10,
        maintenance_personnel: Optional[str] = None
    ) -> tuple[List[dict], int]:
        """
        获取临期工单列表
        
        Args:
            project_name: 项目名称筛选
            client_name: 客户名称筛选
            work_order_type: 工单类型筛选
            page: 页码
            size: 每页数量
            maintenance_personnel: 运维人员筛选
            
        Returns:
            tuple: (临期工单列表, 总数)
        """
        today = date.today()
        expiring_items = []
        
        valid_statuses = OverdueAlertConfig.VALID_STATUSES
        end_date = today + timedelta(days=7)
        
        if work_order_type is None or work_order_type == '定期巡检':
            items = self._get_expiring_periodic_inspections(
                today=today,
                end_date=end_date,
                valid_statuses=valid_statuses,
                project_name=project_name,
                client_name=client_name,
                maintenance_personnel=maintenance_personnel
            )
            expiring_items.extend(items)
        
        if work_order_type is None or work_order_type == '临时维修':
            items = self._get_expiring_temporary_repairs(
                today=today,
                end_date=end_date,
                valid_statuses=valid_statuses,
                project_name=project_name,
                client_name=client_name,
                maintenance_personnel=maintenance_personnel
            )
            expiring_items.extend(items)
        
        if work_order_type is None or work_order_type == '零星用工':
            items = self._get_expiring_spot_works(
                today=today,
                end_date=end_date,
                valid_statuses=valid_statuses,
                project_name=project_name,
                client_name=client_name,
                maintenance_personnel=maintenance_personnel
            )
            expiring_items.extend(items)
        
        expiring_items.sort(key=lambda x: x['daysRemaining'])
        
        total = len(expiring_items)
        start = page * size
        end = start + size
        paginated_items = expiring_items[start:end]
        
        return paginated_items, total
    
    def _get_plan_date(self, record, field: str = 'plan_start_date') -> date:
        """
        获取计划日期，统一转换为date类型
        """
        date_value = getattr(record, field, None)
        if date_value is None:
            return None
        if isinstance(date_value, datetime):
            return date_value.date()
        return date_value
    
    def _get_expiring_periodic_inspections(
        self,
        today: date,
        end_date: date,
        valid_statuses: List[str],
        project_name: Optional[str] = None,
        client_name: Optional[str] = None,
        maintenance_personnel: Optional[str] = None
    ) -> List[dict]:
        """
        获取临期的定期巡检工单（基于计划开始日期）
        """
        try:
            today_datetime = datetime.combine(today, datetime.min.time())
            end_datetime = datetime.combine(end_date, datetime.min.time())
            
            query = self.db.query(PeriodicInspection).filter(
                and_(
                    PeriodicInspection.plan_start_date >= today_datetime,
                    PeriodicInspection.plan_start_date <= end_datetime,
                    PeriodicInspection.status.in_(valid_statuses)
                )
            )
            
            if project_name:
                query = query.filter(PeriodicInspection.project_name.like(f"%{project_name}%"))
            
            if client_name:
                query = query.filter(PeriodicInspection.client_name.like(f"%{client_name}%"))
            
            if maintenance_personnel:
                query = query.filter(PeriodicInspection.maintenance_personnel == maintenance_personnel)
            
            inspections = query.all()
            
            items = []
            for inspection in inspections:
                plan_start = self._get_plan_date(inspection, 'plan_start_date')
                if plan_start is None:
                    continue
                days_remaining = (plan_start - today).days
                items.append({
                    'id': str(inspection.id),
                    'workOrderNo': inspection.inspection_id,
                    'project_id': inspection.project_id,
                    'projectName': inspection.project_name,
                    'customerName': inspection.client_name,
                    'workOrderType': '定期巡检',
                    'planStartDate': plan_start.isoformat() if plan_start else None,
                    'planEndDate': self._get_plan_date(inspection, 'plan_end_date').isoformat() if self._get_plan_date(inspection, 'plan_end_date') else None,
                    'workOrderStatus': inspection.status,
                    'daysRemaining': days_remaining,
                    'executor': inspection.maintenance_personnel
                })
            
            return items
        except Exception as e:
            logger.error(f"查询临期定期巡检失败: {str(e)}")
            return []
    
    def _get_expiring_temporary_repairs(
        self,
        today: date,
        end_date: date,
        valid_statuses: List[str],
        project_name: Optional[str] = None,
        client_name: Optional[str] = None,
        maintenance_personnel: Optional[str] = None
    ) -> List[dict]:
        """
        获取临期的临时维修工单（基于计划开始日期）
        """
        try:
            today_datetime = datetime.combine(today, datetime.min.time())
            end_datetime = datetime.combine(end_date, datetime.min.time())
            
            query = self.db.query(TemporaryRepair).filter(
                and_(
                    TemporaryRepair.plan_start_date >= today_datetime,
                    TemporaryRepair.plan_start_date <= end_datetime,
                    TemporaryRepair.status.in_(valid_statuses)
                )
            )
            
            if project_name:
                query = query.filter(TemporaryRepair.project_name.like(f"%{project_name}%"))
            
            if client_name:
                query = query.filter(TemporaryRepair.client_name.like(f"%{client_name}%"))
            
            if maintenance_personnel:
                query = query.filter(TemporaryRepair.maintenance_personnel == maintenance_personnel)
            
            repairs = query.all()
            
            items = []
            for repair in repairs:
                plan_start = self._get_plan_date(repair, 'plan_start_date')
                if plan_start is None:
                    continue
                days_remaining = (plan_start - today).days
                items.append({
                    'id': str(repair.id),
                    'workOrderNo': repair.repair_id,
                    'project_id': repair.project_id,
                    'projectName': repair.project_name,
                    'customerName': repair.client_name,
                    'workOrderType': '临时维修',
                    'planStartDate': plan_start.isoformat() if plan_start else None,
                    'planEndDate': self._get_plan_date(repair, 'plan_end_date').isoformat() if self._get_plan_date(repair, 'plan_end_date') else None,
                    'workOrderStatus': repair.status,
                    'daysRemaining': days_remaining,
                    'executor': repair.maintenance_personnel
                })
            
            return items
        except Exception as e:
            logger.error(f"查询临期临时维修失败: {str(e)}")
            return []
    
    def _get_expiring_spot_works(
        self,
        today: date,
        end_date: date,
        valid_statuses: List[str],
        project_name: Optional[str] = None,
        client_name: Optional[str] = None,
        maintenance_personnel: Optional[str] = None
    ) -> List[dict]:
        """
        获取临期的零星用工工单（基于计划开始日期）
        """
        try:
            today_datetime = datetime.combine(today, datetime.min.time())
            end_datetime = datetime.combine(end_date, datetime.min.time())
            
            query = self.db.query(SpotWork).filter(
                and_(
                    SpotWork.plan_start_date >= today_datetime,
                    SpotWork.plan_start_date <= end_datetime,
                    SpotWork.status.in_(valid_statuses)
                )
            )
            
            if project_name:
                query = query.filter(SpotWork.project_name.like(f"%{project_name}%"))
            
            if client_name:
                query = query.filter(SpotWork.client_name.like(f"%{client_name}%"))
            
            if maintenance_personnel:
                query = query.filter(SpotWork.maintenance_personnel == maintenance_personnel)
            
            works = query.all()
            
            items = []
            for work in works:
                plan_start = self._get_plan_date(work, 'plan_start_date')
                if plan_start is None:
                    continue
                days_remaining = (plan_start - today).days
                items.append({
                    'id': str(work.id),
                    'workOrderNo': work.work_id,
                    'project_id': work.project_id,
                    'projectName': work.project_name,
                    'customerName': work.client_name,
                    'workOrderType': '零星用工',
                    'planStartDate': plan_start.isoformat() if plan_start else None,
                    'planEndDate': self._get_plan_date(work, 'plan_end_date').isoformat() if self._get_plan_date(work, 'plan_end_date') else None,
                    'workOrderStatus': work.status,
                    'daysRemaining': days_remaining,
                    'executor': work.maintenance_personnel
                })
            
            return items
        except Exception as e:
            logger.error(f"查询临期零星用工失败: {str(e)}")
            return []
    
    def get_expiring_count(self, maintenance_personnel: Optional[str] = None) -> int:
        """
        获取临期工单数量
        
        Args:
            maintenance_personnel: 运维人员筛选
            
        Returns:
            int: 临期工单数量
        """
        _, total = self.get_expiring_items(
            maintenance_personnel=maintenance_personnel,
            page=0,
            size=1
        )
        return total

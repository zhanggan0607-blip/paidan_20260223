from typing import List, Optional
from datetime import datetime, date
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func, cast, Date
from app.models.periodic_inspection import PeriodicInspection
from app.models.temporary_repair import TemporaryRepair
from app.models.spot_work import SpotWork
from app.config import OverdueAlertConfig
import logging

logger = logging.getLogger(__name__)


class OverdueAlertService:
    """
    超期工单提醒服务
    查询所有计划结束日期已过且状态不是"已完成"的工单
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_overdue_items(
        self,
        project_name: Optional[str] = None,
        client_name: Optional[str] = None,
        work_order_type: Optional[str] = None,
        page: int = 0,
        size: int = 10,
        maintenance_personnel: Optional[str] = None
    ) -> tuple[List[dict], int]:
        """
        获取超期工单列表
        
        Args:
            project_name: 项目名称筛选
            client_name: 客户名称筛选
            work_order_type: 工单类型筛选
            page: 页码
            size: 每页数量
            maintenance_personnel: 运维人员筛选
            
        Returns:
            tuple: (超期工单列表, 总数)
        """
        today = date.today()
        overdue_items = []
        
        valid_statuses = OverdueAlertConfig.VALID_STATUSES
        
        if work_order_type is None or work_order_type == '定期巡检':
            items = self._get_overdue_periodic_inspections(
                today=today,
                valid_statuses=valid_statuses,
                project_name=project_name,
                client_name=client_name,
                maintenance_personnel=maintenance_personnel
            )
            overdue_items.extend(items)
        
        if work_order_type is None or work_order_type == '临时维修':
            items = self._get_overdue_temporary_repairs(
                today=today,
                valid_statuses=valid_statuses,
                project_name=project_name,
                client_name=client_name,
                maintenance_personnel=maintenance_personnel
            )
            overdue_items.extend(items)
        
        if work_order_type is None or work_order_type == '零星用工':
            items = self._get_overdue_spot_works(
                today=today,
                valid_statuses=valid_statuses,
                project_name=project_name,
                client_name=client_name,
                maintenance_personnel=maintenance_personnel
            )
            overdue_items.extend(items)
        
        overdue_items.sort(key=lambda x: x['overdueDays'], reverse=True)
        
        total = len(overdue_items)
        start = page * size
        end = start + size
        paginated_items = overdue_items[start:end]
        
        return paginated_items, total
    
    def _get_plan_end_date(self, record) -> date:
        """
        获取计划结束日期，统一转换为date类型
        """
        plan_end_date = record.plan_end_date
        if plan_end_date is None:
            return None
        if isinstance(plan_end_date, datetime):
            return plan_end_date.date()
        return plan_end_date
    
    def _get_overdue_periodic_inspections(
        self,
        today: date,
        valid_statuses: List[str],
        project_name: Optional[str] = None,
        client_name: Optional[str] = None,
        maintenance_personnel: Optional[str] = None
    ) -> List[dict]:
        """
        获取超期的定期巡检工单
        """
        try:
            query = self.db.query(PeriodicInspection).filter(
                PeriodicInspection.plan_end_date < datetime.combine(today, datetime.min.time()),
                PeriodicInspection.status.in_(valid_statuses)
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
                plan_end = self._get_plan_end_date(inspection)
                if plan_end is None:
                    continue
                overdue_days = (today - plan_end).days
                items.append({
                    'id': str(inspection.id),
                    'workOrderNo': inspection.inspection_id,
                    'project_id': inspection.project_id,
                    'projectName': inspection.project_name,
                    'customerName': inspection.client_name,
                    'workOrderType': '定期巡检',
                    'planEndDate': plan_end.isoformat() if plan_end else None,
                    'workOrderStatus': inspection.status,
                    'overdueDays': overdue_days,
                    'executor': inspection.maintenance_personnel
                })
            
            return items
        except Exception as e:
            logger.error(f"查询超期定期巡检失败: {str(e)}")
            return []
    
    def _get_overdue_temporary_repairs(
        self,
        today: date,
        valid_statuses: List[str],
        project_name: Optional[str] = None,
        client_name: Optional[str] = None,
        maintenance_personnel: Optional[str] = None
    ) -> List[dict]:
        """
        获取超期的临时维修工单
        """
        try:
            query = self.db.query(TemporaryRepair).filter(
                TemporaryRepair.plan_end_date < datetime.combine(today, datetime.min.time()),
                TemporaryRepair.status.in_(valid_statuses)
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
                plan_end = self._get_plan_end_date(repair)
                if plan_end is None:
                    continue
                overdue_days = (today - plan_end).days
                items.append({
                    'id': str(repair.id),
                    'workOrderNo': repair.repair_id,
                    'project_id': repair.project_id,
                    'projectName': repair.project_name,
                    'customerName': repair.client_name,
                    'workOrderType': '临时维修',
                    'planEndDate': plan_end.isoformat() if plan_end else None,
                    'workOrderStatus': repair.status,
                    'overdueDays': overdue_days,
                    'executor': repair.maintenance_personnel
                })
            
            return items
        except Exception as e:
            logger.error(f"查询超期临时维修失败: {str(e)}")
            return []
    
    def _get_overdue_spot_works(
        self,
        today: date,
        valid_statuses: List[str],
        project_name: Optional[str] = None,
        client_name: Optional[str] = None,
        maintenance_personnel: Optional[str] = None
    ) -> List[dict]:
        """
        获取超期的零星用工工单
        """
        try:
            query = self.db.query(SpotWork).filter(
                SpotWork.plan_end_date < datetime.combine(today, datetime.min.time()),
                SpotWork.status.in_(valid_statuses)
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
                plan_end = self._get_plan_end_date(work)
                if plan_end is None:
                    continue
                overdue_days = (today - plan_end).days
                items.append({
                    'id': str(work.id),
                    'workOrderNo': work.work_id,
                    'project_id': work.project_id,
                    'projectName': work.project_name,
                    'customerName': work.client_name,
                    'workOrderType': '零星用工',
                    'planEndDate': plan_end.isoformat() if plan_end else None,
                    'workOrderStatus': work.status,
                    'overdueDays': overdue_days,
                    'executor': work.maintenance_personnel
                })
            
            return items
        except Exception as e:
            logger.error(f"查询超期零星用工失败: {str(e)}")
            return []
    
    def get_overdue_count(self, maintenance_personnel: Optional[str] = None) -> int:
        """
        获取超期工单数量
        
        Args:
            maintenance_personnel: 运维人员筛选
            
        Returns:
            int: 超期工单数量
        """
        _, total = self.get_overdue_items(
            maintenance_personnel=maintenance_personnel,
            page=0,
            size=1
        )
        return total

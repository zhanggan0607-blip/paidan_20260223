"""
定期巡检服务
提供定期巡检业务逻辑处理
"""
from typing import List, Optional, Union
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
import json
import logging

from app.models.periodic_inspection import PeriodicInspection
from app.models.periodic_inspection_record import PeriodicInspectionRecord
from app.models.maintenance_plan import MaintenancePlan
from app.repositories.periodic_inspection import PeriodicInspectionRepository
from app.repositories.personnel import PersonnelRepository
from app.schemas.periodic_inspection import PeriodicInspectionCreate, PeriodicInspectionUpdate, PeriodicInspectionPartialUpdate
from app.utils.dictionary_helper import get_default_periodic_inspection_status
from app.services.sync_service import SyncService, PLAN_TYPE_INSPECTION
from app.utils.date_utils import parse_datetime
from app.utils.work_order_id_generator import generate_inspection_id
from app.exceptions import NotFoundException, DuplicateException, ValidationException

logger = logging.getLogger(__name__)


class PeriodicInspectionService:
    """
    定期巡检服务
    提供定期巡检的增删改查等业务逻辑
    """
    
    def __init__(self, db: Session):
        self.repository = PeriodicInspectionRepository(db)
        self.personnel_repository = PersonnelRepository(db)
        self.sync_service = SyncService(db)
        self._db = db
    
    def _parse_date(self, date_value: Union[str, datetime, None]) -> Optional[datetime]:
        """解析日期"""
        return parse_datetime(date_value)
    
    def _validate_maintenance_personnel(self, personnel_name: str) -> None:
        """
        验证运维人员是否存在
        
        Args:
            personnel_name: 运维人员姓名
            
        Raises:
            ValidationException: 运维人员不存在
        """
        if personnel_name:
            if not self.personnel_repository.find_by_name(personnel_name):
                raise ValidationException(
                    f"运维人员'{personnel_name}'不存在于人员列表中，请先添加该人员"
                )
    
    def _create_operation_log(
        self,
        work_order_id: int,
        work_order_no: str,
        operator_name: str,
        operator_id: Optional[int],
        operation_type: str,
        operation_type_name: str,
        remark: str
    ) -> None:
        """
        创建操作日志
        
        Args:
            work_order_id: 工单ID
            work_order_no: 工单编号
            operator_name: 操作者名称
            operator_id: 操作者ID
            operation_type: 操作类型代码
            operation_type_name: 操作类型名称
            remark: 备注
        """
        from app.models.work_order_operation_log import WorkOrderOperationLog
        
        log = WorkOrderOperationLog(
            work_order_type='periodic_inspection',
            work_order_id=work_order_id,
            work_order_no=work_order_no,
            operator_name=operator_name,
            operator_id=operator_id,
            operation_type=operation_type,
            operation_type_code=operation_type,
            operation_type_name=operation_type_name,
            operation_remark=remark
        )
        self._db.add(log)
        self._db.commit()
    
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
        """
        分页获取定期巡检列表
        
        Args:
            page: 页码
            size: 每页数量
            project_name: 项目名称
            client_name: 客户名称
            inspection_id: 巡检单编号
            status: 状态
            maintenance_personnel: 运维人员
            
        Returns:
            (巡检单列表, 总数)
        """
        return self.repository.find_all(
            page, size, project_name, client_name, inspection_id, status, maintenance_personnel
        )
    
    def get_by_id(self, id: int) -> PeriodicInspection:
        """
        根据ID获取定期巡检
        
        Args:
            id: 巡检单ID
            
        Returns:
            巡检单对象
            
        Raises:
            NotFoundException: 巡检单不存在
        """
        inspection = self.repository.find_by_id(id)
        if not inspection:
            raise NotFoundException("巡检单不存在")
        return inspection
    
    def get_by_inspection_id(self, inspection_id: str) -> PeriodicInspection:
        """
        根据巡检单编号获取定期巡检
        
        Args:
            inspection_id: 巡检单编号
            
        Returns:
            巡检单对象
            
        Raises:
            NotFoundException: 巡检单不存在
        """
        inspection = self.repository.find_by_inspection_id(inspection_id)
        if not inspection:
            raise NotFoundException("巡检单不存在")
        return inspection
    
    def create(
        self, 
        dto: PeriodicInspectionCreate, 
        operator_id: Optional[int] = None, 
        operator_name: Optional[str] = None
    ) -> PeriodicInspection:
        """
        创建定期巡检
        
        Args:
            dto: 创建数据传输对象
            operator_id: 操作者ID
            operator_name: 操作者名称
            
        Returns:
            创建的巡检单对象
            
        Raises:
            DuplicateException: 巡检单编号已存在
            ValidationException: 运维人员不存在
        """
        if dto.maintenance_personnel:
            self._validate_maintenance_personnel(dto.maintenance_personnel)
        
        inspection_id = dto.inspection_id
        if inspection_id and self.repository.exists_by_inspection_id(inspection_id):
            raise DuplicateException("巡检单编号已存在")
        
        if not inspection_id:
            inspection_id = generate_inspection_id(self.repository.db, dto.project_id)
        
        default_status = get_default_periodic_inspection_status(self._db)
        
        inspection = PeriodicInspection(
            inspection_id=inspection_id,
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
        
        if operator_name and result.id:
            self._create_operation_log(
                work_order_id=result.id,
                work_order_no=result.inspection_id,
                operator_name=operator_name,
                operator_id=operator_id,
                operation_type='create',
                operation_type_name='创建',
                remark='创建定期巡检单'
            )
        
        return result
    
    def update(
        self, 
        id: int, 
        dto: PeriodicInspectionUpdate, 
        operator_id: Optional[int] = None, 
        operator_name: Optional[str] = None
    ) -> PeriodicInspection:
        """
        更新定期巡检
        
        Args:
            id: 巡检单ID
            dto: 更新数据传输对象
            operator_id: 操作者ID
            operator_name: 操作者名称
            
        Returns:
            更新后的巡检单对象
            
        Raises:
            NotFoundException: 巡检单不存在
            DuplicateException: 巡检单编号已存在
            ValidationException: 运维人员不存在
        """
        if dto.maintenance_personnel:
            self._validate_maintenance_personnel(dto.maintenance_personnel)
        
        existing_inspection = self.get_by_id(id)
        
        if existing_inspection.inspection_id != dto.inspection_id and self.repository.exists_by_inspection_id(dto.inspection_id):
            raise DuplicateException("巡检单编号已存在")
        
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
        
        if operator_name and result.id:
            self._create_operation_log(
                work_order_id=result.id,
                work_order_no=result.inspection_id,
                operator_name=operator_name,
                operator_id=operator_id,
                operation_type='update',
                operation_type_name='更新',
                remark='更新定期巡检单'
            )
        
        return result
    
    def delete(self, id: int, user_id: int = None, operator_name: str = None) -> None:
        """
        软删除定期巡检单
        
        Args:
            id: 巡检单ID
            user_id: 执行删除的用户ID
            operator_name: 操作者名称
            
        Raises:
            NotFoundException: 巡检单不存在
        """
        inspection = self.get_by_id(id)
        self.sync_service.sync_order_to_work_plan(PLAN_TYPE_INSPECTION, inspection, is_delete=True, user_id=user_id)
        
        if operator_name and inspection.id:
            self._create_operation_log(
                work_order_id=inspection.id,
                work_order_no=inspection.inspection_id,
                operator_name=operator_name,
                operator_id=user_id,
                operation_type='delete',
                operation_type_name='删除',
                remark=f'删除定期巡检单 {inspection.inspection_id}'
            )
        
        self.repository.soft_delete(inspection, user_id)
    
    def partial_update(
        self, 
        id: int, 
        dto: PeriodicInspectionPartialUpdate, 
        operator_id: Optional[int] = None, 
        operator_name: Optional[str] = None
    ) -> PeriodicInspection:
        """
        部分更新定期巡检
        
        Args:
            id: 巡检单ID
            dto: 部分更新数据传输对象
            operator_id: 操作者ID
            operator_name: 操作者名称
            
        Returns:
            更新后的巡检单对象
            
        Raises:
            NotFoundException: 巡检单不存在
            ValidationException: 运维人员不存在
        """
        if dto.maintenance_personnel:
            self._validate_maintenance_personnel(dto.maintenance_personnel)
        
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
        if dto.maintenance_personnel is not None:
            existing_inspection.maintenance_personnel = dto.maintenance_personnel
        if dto.status is not None:
            existing_inspection.status = dto.status
            if dto.status == '已完成' and not existing_inspection.actual_completion_date:
                existing_inspection.actual_completion_date = datetime.now()
        
        result = self.repository.update(existing_inspection)
        self.sync_service.sync_order_to_work_plan(PLAN_TYPE_INSPECTION, result)
        return result
    
    def get_all_unpaginated(self) -> List[PeriodicInspection]:
        """
        获取所有定期巡检（不分页）
        
        Returns:
            巡检单列表
        """
        return self.repository.find_all_unpaginated()
    
    def get_inspection_counts(self, inspection_id: str, project_id: str, plan_start_date: datetime, plan_end_date: datetime) -> dict:
        """
        计算巡检单的已填写数量和总数量
        统计3级节点（inspection_content）的数量
        总数量：该巡检单对应的不同3级节点数量
        已填写数量：已处理的3级节点数量
        """
        records = self._db.query(PeriodicInspectionRecord).filter(
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
            total_count = self._get_total_count_from_plans(project_id, plan_start_date, plan_end_date)
            filled_count = 0
        
        return {
            'total_count': total_count,
            'filled_count': filled_count
        }
    
    def get_inspection_counts_batch(self, inspections: List[PeriodicInspection]) -> dict:
        """
        批量计算多个巡检单的已填写数量和总数量
        避免N+1查询问题
        
        Args:
            inspections: 巡检单列表
            
        Returns:
            dict: {inspection_id: {'total_count': int, 'filled_count': int}}
        """
        if not inspections:
            return {}
        
        inspection_ids = [ins.inspection_id for ins in inspections]
        
        all_records = self._db.query(PeriodicInspectionRecord).filter(
            PeriodicInspectionRecord.inspection_id.in_(inspection_ids)
        ).all()
        
        records_by_inspection = {}
        for record in all_records:
            if record.inspection_id not in records_by_inspection:
                records_by_inspection[record.inspection_id] = []
            records_by_inspection[record.inspection_id].append(record)
        
        project_ids = list(set(ins.project_id for ins in inspections if ins.project_id))
        plans = []
        if project_ids:
            plans = self._db.query(MaintenancePlan).filter(
                MaintenancePlan.project_id.in_(project_ids)
            ).all()
        
        plans_by_project = {}
        for plan in plans:
            if plan.project_id not in plans_by_project:
                plans_by_project[plan.project_id] = []
            plans_by_project[plan.project_id].append(plan)
        
        result = {}
        for ins in inspections:
            records = records_by_inspection.get(ins.inspection_id, [])
            
            if records:
                unique_items = {}
                for record in records:
                    key = record.inspection_content or record.item_name
                    if key not in unique_items:
                        unique_items[key] = {'inspected': False}
                    if record.inspected:
                        unique_items[key]['inspected'] = True
                
                total_count = len(unique_items)
                filled_count = sum(1 for item in unique_items.values() if item['inspected'])
            else:
                project_plans = plans_by_project.get(ins.project_id, [])
                total_count = self._get_total_count_from_plans_cached(
                    project_plans, ins.plan_start_date, ins.plan_end_date
                )
                filled_count = 0
            
            result[ins.inspection_id] = {
                'total_count': total_count,
                'filled_count': filled_count
            }
        
        return result
    
    def _get_total_count_from_plans_cached(self, plans: list, plan_start_date: datetime, plan_end_date: datetime) -> int:
        """
        从缓存的维保计划列表中获取3级节点总数
        """
        if not plan_start_date or not plan_end_date:
            return 0
        
        try:
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
                        except (json.JSONDecodeError, TypeError):
                            pass
            
            return len(unique_items)
        except Exception as e:
            logger.error(f"Error getting total count from plans: {e}")
            return 0
    
    def _get_total_count_from_plans(self, project_id: str, plan_start_date: datetime, plan_end_date: datetime) -> int:
        """
        从维保计划中获取3级节点总数
        """
        if not project_id or not plan_start_date or not plan_end_date:
            return 0
        
        try:
            plans = self._db.query(MaintenancePlan).filter(
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
                        except (json.JSONDecodeError, TypeError):
                            pass
            
            return len(unique_items)
        except Exception as e:
            logger.error(f"Error getting total count from plans: {e}")
            return 0

"""
临时维修服务
提供临时维修业务逻辑处理
"""
from typing import List, Optional, Union
from datetime import datetime
from sqlalchemy.orm import Session
import json
import logging

from app.models.temporary_repair import TemporaryRepair
from app.repositories.temporary_repair import TemporaryRepairRepository
from app.repositories.personnel import PersonnelRepository
from app.exceptions import NotFoundException, DuplicateException, ValidationException
from app.utils.dictionary_helper import get_default_temporary_repair_status
from app.services.sync_service import SyncService, PLAN_TYPE_REPAIR
from app.schemas.temporary_repair import TemporaryRepairCreate, TemporaryRepairUpdate
from app.utils.date_utils import parse_datetime
from app.utils.work_order_id_generator import generate_repair_id

logger = logging.getLogger(__name__)


class TemporaryRepairService:
    """
    临时维修服务
    提供临时维修的增删改查等业务逻辑
    """
    
    def __init__(self, db: Session):
        self.repository = TemporaryRepairRepository(db)
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
            work_order_type='temporary_repair',
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
        repair_id: Optional[str] = None,
        status: Optional[str] = None,
        maintenance_personnel: Optional[str] = None
    ) -> tuple[List[TemporaryRepair], int]:
        """
        分页获取临时维修列表
        
        Args:
            page: 页码
            size: 每页数量
            project_name: 项目名称
            repair_id: 维修单编号
            status: 状态
            maintenance_personnel: 运维人员
            
        Returns:
            (维修单列表, 总数)
        """
        return self.repository.find_all(
            page, size, project_name, repair_id, status, maintenance_personnel
        )
    
    def get_by_id(self, id: int) -> TemporaryRepair:
        """
        根据ID获取临时维修
        
        Args:
            id: 维修单ID
            
        Returns:
            维修单对象
            
        Raises:
            NotFoundException: 维修单不存在
        """
        repair = self.repository.find_by_id(id)
        if not repair:
            raise NotFoundException("维修单不存在")
        return repair
    
    def get_by_repair_id(self, repair_id: str) -> TemporaryRepair:
        """
        根据维修单编号获取临时维修
        
        Args:
            repair_id: 维修单编号
            
        Returns:
            维修单对象
            
        Raises:
            NotFoundException: 维修单不存在
        """
        repair = self.repository.find_by_repair_id(repair_id)
        if not repair:
            raise NotFoundException("维修单不存在")
        return repair
    
    def create(
        self, 
        dto: TemporaryRepairCreate, 
        operator_id: Optional[int] = None, 
        operator_name: Optional[str] = None
    ) -> TemporaryRepair:
        """
        创建临时维修
        
        Args:
            dto: 创建数据传输对象
            operator_id: 操作者ID
            operator_name: 操作者名称
            
        Returns:
            创建的维修单对象
            
        Raises:
            DuplicateException: 维修单编号已存在
            ValidationException: 运维人员不存在
        """
        if dto.maintenance_personnel:
            self._validate_maintenance_personnel(dto.maintenance_personnel)
        
        repair_id = dto.repair_id
        if repair_id and self.repository.exists_by_repair_id(repair_id):
            raise DuplicateException("维修单编号已存在")
        
        if not repair_id:
            repair_id = generate_repair_id(self.repository.db, dto.project_id)
        
        default_status = get_default_temporary_repair_status(self._db)
        
        repair = TemporaryRepair(
            repair_id=repair_id,
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
        
        if operator_name and result.id:
            self._create_operation_log(
                work_order_id=result.id,
                work_order_no=result.repair_id,
                operator_name=operator_name,
                operator_id=operator_id,
                operation_type='create',
                operation_type_name='创建',
                remark='创建临时维修单'
            )
        
        return result
    
    def update(
        self, 
        id: int, 
        dto: TemporaryRepairUpdate, 
        operator_id: Optional[int] = None, 
        operator_name: Optional[str] = None
    ) -> TemporaryRepair:
        """
        更新临时维修
        
        Args:
            id: 维修单ID
            dto: 更新数据传输对象
            operator_id: 操作者ID
            operator_name: 操作者名称
            
        Returns:
            更新后的维修单对象
            
        Raises:
            NotFoundException: 维修单不存在
            DuplicateException: 维修单编号已存在
            ValidationException: 运维人员不存在
        """
        if dto.maintenance_personnel:
            self._validate_maintenance_personnel(dto.maintenance_personnel)
        
        existing_repair = self.get_by_id(id)
        
        if existing_repair.repair_id != dto.repair_id and self.repository.exists_by_repair_id(dto.repair_id):
            raise DuplicateException("维修单编号已存在")
        
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
        existing_repair.customer_signature = dto.customer_signature
        existing_repair.execution_date = self._parse_date(dto.execution_date)
        
        result = self.repository.update(existing_repair)
        self.sync_service.sync_order_to_work_plan(PLAN_TYPE_REPAIR, result)
        
        if operator_name and result.id:
            self._create_operation_log(
                work_order_id=result.id,
                work_order_no=result.repair_id,
                operator_name=operator_name,
                operator_id=operator_id,
                operation_type='update',
                operation_type_name='更新',
                remark='更新临时维修单'
            )
        
        return result
    
    def partial_update(
        self, 
        id: int, 
        dto, 
        operator_id: Optional[int] = None, 
        operator_name: Optional[str] = None
    ) -> TemporaryRepair:
        """
        部分更新临时维修
        
        Args:
            id: 维修单ID
            dto: 部分更新数据传输对象
            operator_id: 操作者ID
            operator_name: 操作者名称
            
        Returns:
            更新后的维修单对象
            
        Raises:
            NotFoundException: 维修单不存在
            DuplicateException: 维修单编号已存在
            ValidationException: 运维人员不存在
        """
        if dto.maintenance_personnel:
            self._validate_maintenance_personnel(dto.maintenance_personnel)
        
        existing_repair = self.get_by_id(id)
        
        if dto.repair_id is not None:
            if existing_repair.repair_id != dto.repair_id and self.repository.exists_by_repair_id(dto.repair_id):
                raise DuplicateException("维修单编号已存在")
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
            if dto.status == '已完成' and not existing_repair.actual_completion_date:
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
        if hasattr(dto, 'customer_signature') and dto.customer_signature is not None:
            existing_repair.customer_signature = dto.customer_signature
        if hasattr(dto, 'execution_date') and dto.execution_date is not None:
            existing_repair.execution_date = self._parse_date(dto.execution_date)
        
        result = self.repository.update(existing_repair)
        self.sync_service.sync_order_to_work_plan(PLAN_TYPE_REPAIR, result)
        return result
    
    def delete(self, id: int, user_id: int = None, operator_name: str = None) -> None:
        """
        软删除临时维修单
        
        Args:
            id: 维修单ID
            user_id: 执行删除的用户ID
            operator_name: 操作者名称
            
        Raises:
            NotFoundException: 维修单不存在
        """
        repair = self.get_by_id(id)
        self.sync_service.sync_order_to_work_plan(PLAN_TYPE_REPAIR, repair, is_delete=True, user_id=user_id)
        
        if operator_name and repair.id:
            self._create_operation_log(
                work_order_id=repair.id,
                work_order_no=repair.repair_id,
                operator_name=operator_name,
                operator_id=user_id,
                operation_type='delete',
                operation_type_name='删除',
                remark=f'删除临时维修单 {repair.repair_id}'
            )
        
        self.repository.soft_delete(repair, user_id)
    
    def get_all_unpaginated(self) -> List[TemporaryRepair]:
        """
        获取所有临时维修（不分页）
        
        Returns:
            维修单列表
        """
        return self.repository.find_all_unpaginated()

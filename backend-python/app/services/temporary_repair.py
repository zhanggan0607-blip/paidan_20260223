"""
临时维修服务
提供临时维修业务逻辑处理
"""
from typing import List, Optional, Union
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.temporary_repair import TemporaryRepair
from app.repositories.temporary_repair import TemporaryRepairRepository
from app.exceptions import NotFoundException, DuplicateException
from app.utils.dictionary_helper import get_default_temporary_repair_status
from app.services.sync_service import SyncService, PLAN_TYPE_REPAIR
from app.schemas.temporary_repair import TemporaryRepairCreate, TemporaryRepairUpdate
from app.utils.date_utils import parse_datetime
from app.utils.work_order_id_generator import generate_repair_id
import json


class TemporaryRepairService:
    """
    临时维修服务
    提供临时维修的增删改查等业务逻辑
    """
    
    def __init__(self, db: Session):
        self.repository = TemporaryRepairRepository(db)
        self.sync_service = SyncService(db)
    
    def _parse_date(self, date_value: Union[str, datetime, None]) -> Optional[datetime]:
        """解析日期"""
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
    
    def create(self, dto: TemporaryRepairCreate) -> TemporaryRepair:
        """
        创建临时维修
        
        Args:
            dto: 创建数据传输对象
            
        Returns:
            创建的维修单对象
            
        Raises:
            DuplicateException: 维修单编号已存在
        """
        repair_id = dto.repair_id
        if repair_id and self.repository.exists_by_repair_id(repair_id):
            raise DuplicateException("维修单编号已存在")
        
        if not repair_id:
            repair_id = generate_repair_id(self.repository.db, dto.project_id)
        
        default_status = get_default_temporary_repair_status(self.repository.db)
        
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
        return result
    
    def update(self, id: int, dto: TemporaryRepairUpdate) -> TemporaryRepair:
        """
        更新临时维修
        
        Args:
            id: 维修单ID
            dto: 更新数据传输对象
            
        Returns:
            更新后的维修单对象
            
        Raises:
            NotFoundException: 维修单不存在
            DuplicateException: 维修单编号已存在
        """
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
        return result
    
    def partial_update(self, id: int, dto) -> TemporaryRepair:
        """
        部分更新临时维修
        
        Args:
            id: 维修单ID
            dto: 部分更新数据传输对象
            
        Returns:
            更新后的维修单对象
            
        Raises:
            NotFoundException: 维修单不存在
            DuplicateException: 维修单编号已存在
        """
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
    
    def delete(self, id: int, user_id: int = None) -> None:
        """
        软删除临时维修单
        
        Args:
            id: 维修单ID
            user_id: 执行删除的用户ID
            
        Raises:
            NotFoundException: 维修单不存在
        """
        repair = self.get_by_id(id)
        self.sync_service.sync_order_to_work_plan(PLAN_TYPE_REPAIR, repair, is_delete=True, user_id=user_id)
        self.repository.soft_delete(repair, user_id)
    
    def get_all_unpaginated(self) -> List[TemporaryRepair]:
        """
        获取所有临时维修（不分页）
        
        Returns:
            维修单列表
        """
        return self.repository.find_all_unpaginated()

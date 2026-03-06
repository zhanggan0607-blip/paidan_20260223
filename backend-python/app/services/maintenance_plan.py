"""
维保计划服务
提供维保计划业务逻辑处理
"""
from typing import List, Optional, Union
import logging
from fastapi import HTTPException, status
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.maintenance_plan import MaintenancePlan
from app.models.periodic_inspection import PeriodicInspection
from app.models.temporary_repair import TemporaryRepair
from app.models.spot_work import SpotWork
from app.repositories.maintenance_plan import MaintenancePlanRepository
from app.schemas.maintenance_plan import MaintenancePlanCreate, MaintenancePlanUpdate
from app.services.sync_service import SyncService
from app.utils.date_utils import parse_datetime
from app.exceptions import NotFoundException, DuplicateException

logger = logging.getLogger(__name__)


class MaintenancePlanService:
    """
    维保计划服务
    提供维保计划的增删改查等业务逻辑
    """
    
    def __init__(self, db: Session):
        self.repository = MaintenancePlanRepository(db)
        self.sync_service = SyncService(db)
        self._db = db
    
    def _parse_date(self, date_value: Union[str, datetime, None]) -> Optional[datetime]:
        """解析日期"""
        return parse_datetime(date_value)
    
    def _create_operation_log(
        self,
        work_order_type: str,
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
            work_order_type: 工单类型
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
            work_order_type=work_order_type,
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
        plan_name: Optional[str] = None, 
        project_id: Optional[str] = None,
        equipment_name: Optional[str] = None,
        plan_status: Optional[str] = None,
        status: Optional[str] = None,
        maintenance_personnel: Optional[str] = None,
        project_name: Optional[str] = None,
        client_name: Optional[str] = None,
        plan_type: Optional[str] = None,
        maintenance_personnel_filter: Optional[str] = None
    ) -> tuple[List[MaintenancePlan], int]:
        """
        分页获取维保计划列表
        
        Args:
            page: 页码
            size: 每页数量
            plan_name: 计划名称
            project_id: 项目ID
            equipment_name: 设备名称
            plan_status: 计划状态
            status: 执行状态
            maintenance_personnel: 维保人员
            project_name: 项目名称
            client_name: 客户名称
            plan_type: 计划类型
            maintenance_personnel_filter: 权限过滤
            
        Returns:
            (维保计划列表, 总数)
        """
        return self.repository.find_all(
            page, size, plan_name, project_id, equipment_name, 
            plan_status, status, maintenance_personnel,
            project_name, client_name, plan_type, maintenance_personnel_filter
        )
    
    def get_by_id(self, id: int) -> MaintenancePlan:
        """
        根据ID获取维保计划
        
        Args:
            id: 维保计划ID
            
        Returns:
            维保计划对象
            
        Raises:
            NotFoundException: 维保计划不存在
        """
        maintenance_plan = self.repository.find_by_id(id)
        if not maintenance_plan:
            raise NotFoundException("维保计划不存在")
        return maintenance_plan
    
    def get_by_plan_id(self, plan_id: str) -> MaintenancePlan:
        """
        根据计划编号获取维保计划
        
        Args:
            plan_id: 计划编号
            
        Returns:
            维保计划对象
            
        Raises:
            NotFoundException: 维保计划不存在
        """
        maintenance_plan = self.repository.find_by_plan_id(plan_id)
        if not maintenance_plan:
            raise NotFoundException("维保计划不存在")
        return maintenance_plan
    
    def get_by_project_id(self, project_id: str) -> List[MaintenancePlan]:
        """
        根据项目ID获取维保计划列表
        
        Args:
            project_id: 项目ID
            
        Returns:
            维保计划列表
        """
        return self.repository.find_by_project_id_list(project_id)
    
    def get_upcoming_maintenance(self, days: int = 7) -> List[MaintenancePlan]:
        """
        获取即将到期的维保计划
        
        Args:
            days: 天数
            
        Returns:
            维保计划列表
        """
        return self.repository.find_upcoming_maintenance(days)
    
    def get_by_date_range(self, start_date, end_date) -> List[MaintenancePlan]:
        """
        根据日期范围获取维保计划
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            维保计划列表
        """
        return self.repository.find_by_date_range(start_date, end_date)
    
    def create(
        self, 
        dto: MaintenancePlanCreate, 
        operator_id: Optional[int] = None, 
        operator_name: Optional[str] = None
    ) -> MaintenancePlan:
        """
        创建维保计划
        
        Args:
            dto: 创建数据传输对象
            operator_id: 操作者ID
            operator_name: 操作者名称
            
        Returns:
            创建的维保计划对象
            
        Raises:
            DuplicateException: 计划编号已存在
        """
        logger.info(f"📥 [Service] 开始创建维保计划: plan_id={dto.plan_id}, plan_name={dto.plan_name}")

        if self.repository.exists_by_plan_id(dto.plan_id):
            logger.error(f"❌ [Service] 计划编号已存在: {dto.plan_id}")
            raise DuplicateException("计划编号已存在")

        maintenance_plan = MaintenancePlan(
            plan_id=dto.plan_id,
            plan_name=dto.plan_name,
            project_id=dto.project_id,
            plan_type=dto.plan_type,
            equipment_id=dto.equipment_id,
            equipment_name=dto.equipment_name,
            equipment_model=dto.equipment_model,
            equipment_location=dto.equipment_location,
            plan_start_date=self._parse_date(dto.plan_start_date),
            plan_end_date=self._parse_date(dto.plan_end_date),
            execution_date=self._parse_date(dto.execution_date),
            next_maintenance_date=self._parse_date(dto.next_maintenance_date),
            maintenance_personnel=dto.maintenance_personnel,
            responsible_department=dto.responsible_department,
            contact_info=dto.contact_info,
            maintenance_content=dto.maintenance_content,
            maintenance_requirements=dto.maintenance_requirements,
            maintenance_standard=dto.maintenance_standard,
            plan_status=dto.plan_status,
            status=dto.status,
            completion_rate=dto.completion_rate,
            filled_count=dto.filled_count or 0,
            total_count=dto.total_count or 5,
            remarks=dto.remarks,
            inspection_items=dto.inspection_items
        )

        logger.info(f"📥 [Service] 准备保存到数据库: plan_id={maintenance_plan.plan_id}, plan_name={maintenance_plan.plan_name}")
        result = self.repository.create(maintenance_plan)
        logger.info(f"✅ [Service] 数据库保存成功: id={result.id}, plan_id={result.plan_id}")
        
        self._create_work_order_for_plan(result)
        
        self.sync_service.sync_maintenance_plan_to_work_plan(result)
        logger.info(f"✅ [Service] 同步到WorkPlan成功: plan_id={result.plan_id}")
        
        if operator_name and result.id:
            self._create_operation_log(
                work_order_type='maintenance_plan',
                work_order_id=result.id,
                work_order_no=result.plan_id,
                operator_name=operator_name,
                operator_id=operator_id,
                operation_type='create',
                operation_type_name='创建',
                remark='创建维保计划'
            )
        
        return result
    
    def _create_work_order_for_plan(self, plan: MaintenancePlan) -> None:
        """
        根据维保计划自动创建对应的工单
        """
        try:
            from app.models.project_info import ProjectInfo
            
            project = self._db.query(ProjectInfo).filter(
                ProjectInfo.project_id == plan.project_id
            ).first()
            
            client_name = project.client_name if project else plan.responsible_department
            
            inspection_id = f"XJ-{plan.project_id}-{plan.plan_start_date.strftime('%Y%m%d') if plan.plan_start_date else datetime.now().strftime('%Y%m%d')}"
            
            existing = self._db.query(PeriodicInspection).filter(
                PeriodicInspection.inspection_id == inspection_id
            ).first()
            
            if existing:
                max_retries = 100
                for seq in range(1, max_retries + 1):
                    inspection_id = f"XJ-{plan.project_id}-{plan.plan_start_date.strftime('%Y%m%d') if plan.plan_start_date else datetime.now().strftime('%Y%m%d')}-{seq:02d}"
                    if not self._db.query(PeriodicInspection).filter(
                        PeriodicInspection.inspection_id == inspection_id
                    ).first():
                        break
                else:
                    logger.error(f"无法生成唯一工单编号，已达到最大重试次数: {max_retries}")
                    raise Exception(f"无法生成唯一工单编号，请检查数据是否存在重复")
            
            work_order = PeriodicInspection(
                inspection_id=inspection_id,
                plan_id=plan.plan_id,
                project_id=plan.project_id,
                project_name=plan.project_name or (project.project_name if project else ''),
                plan_start_date=plan.plan_start_date,
                plan_end_date=plan.plan_end_date,
                client_name=client_name,
                maintenance_personnel=plan.maintenance_personnel,
                status='执行中',
                remarks=plan.remarks
            )
            
            self._db.add(work_order)
            self._db.commit()
            
            logger.info(f"✅ [Service] 自动创建工单成功: inspection_id={inspection_id}, plan_id={plan.plan_id}")
            
        except Exception as e:
            logger.error(f"❌ [Service] 创建工单失败: {str(e)}")
            self._db.rollback()
    
    def update(
        self, 
        id: int, 
        dto: MaintenancePlanUpdate, 
        operator_id: Optional[int] = None, 
        operator_name: Optional[str] = None
    ) -> MaintenancePlan:
        """
        更新维保计划
        
        Args:
            id: 维保计划ID
            dto: 更新数据传输对象
            operator_id: 操作者ID
            operator_name: 操作者名称
            
        Returns:
            更新后的维保计划对象
            
        Raises:
            NotFoundException: 维保计划不存在
            DuplicateException: 计划编号已存在
        """
        existing_plan = self.get_by_id(id)
        
        if existing_plan.plan_id != dto.plan_id and self.repository.exists_by_plan_id(dto.plan_id):
            raise DuplicateException("计划编号已存在")
        
        existing_plan.plan_id = dto.plan_id
        existing_plan.plan_name = dto.plan_name
        existing_plan.project_id = dto.project_id
        existing_plan.plan_type = dto.plan_type
        existing_plan.equipment_id = dto.equipment_id
        existing_plan.equipment_name = dto.equipment_name
        existing_plan.equipment_model = dto.equipment_model
        existing_plan.equipment_location = dto.equipment_location
        existing_plan.plan_start_date = self._parse_date(dto.plan_start_date)
        existing_plan.plan_end_date = self._parse_date(dto.plan_end_date)
        existing_plan.execution_date = self._parse_date(dto.execution_date)
        existing_plan.next_maintenance_date = self._parse_date(dto.next_maintenance_date)
        existing_plan.maintenance_personnel = dto.maintenance_personnel
        existing_plan.responsible_department = dto.responsible_department
        existing_plan.contact_info = dto.contact_info
        existing_plan.maintenance_content = dto.maintenance_content
        existing_plan.maintenance_requirements = dto.maintenance_requirements
        existing_plan.maintenance_standard = dto.maintenance_standard
        existing_plan.plan_status = dto.plan_status
        existing_plan.status = dto.status
        existing_plan.completion_rate = dto.completion_rate
        existing_plan.filled_count = dto.filled_count or 0
        existing_plan.total_count = dto.total_count or 5
        existing_plan.remarks = dto.remarks
        existing_plan.inspection_items = dto.inspection_items
        
        result = self.repository.update(existing_plan)
        
        self.sync_service.sync_maintenance_plan_to_work_plan(result)
        logger.info(f"✅ [Service] 同步更新WorkPlan成功: plan_id={result.plan_id}")
        
        if operator_name and result.id:
            self._create_operation_log(
                work_order_type='maintenance_plan',
                work_order_id=result.id,
                work_order_no=result.plan_id,
                operator_name=operator_name,
                operator_id=operator_id,
                operation_type='update',
                operation_type_name='更新',
                remark='更新维保计划'
            )
        
        return result
    
    def delete(self, id: int, user_id: int = None, operator_name: str = None) -> dict:
        """
        软删除维保计划，并级联软删除关联的工单数据
        
        Args:
            id: 维保计划ID
            user_id: 执行删除的用户ID
            operator_name: 操作者名称
            
        Returns:
            删除统计信息
            
        Raises:
            NotFoundException: 维保计划不存在
        """
        maintenance_plan = self.get_by_id(id)
        plan_id = maintenance_plan.plan_id
        
        logger.info(f"🗑️ [Service] 开始软删除维保计划: id={id}, plan_id={plan_id}")
        
        deleted_stats = {
            'plan_id': plan_id,
            'periodic_inspections': 0,
            'temporary_repairs': 0,
            'spot_works': 0,
            'work_plan': False
        }
        
        try:
            periodic_inspections = self._db.query(PeriodicInspection).filter(
                PeriodicInspection.plan_id == plan_id,
                PeriodicInspection.is_deleted == False
            ).all()
            for insp in periodic_inspections:
                insp.soft_delete(user_id)
                deleted_stats['periodic_inspections'] += 1
            
            temporary_repairs = self._db.query(TemporaryRepair).filter(
                TemporaryRepair.plan_id == plan_id,
                TemporaryRepair.is_deleted == False
            ).all()
            for repair in temporary_repairs:
                repair.soft_delete(user_id)
                deleted_stats['temporary_repairs'] += 1
            
            spot_works = self._db.query(SpotWork).filter(
                SpotWork.plan_id == plan_id,
                SpotWork.is_deleted == False
            ).all()
            for work in spot_works:
                work.soft_delete(user_id)
                deleted_stats['spot_works'] += 1
            
            self.sync_service.sync_maintenance_plan_to_work_plan(maintenance_plan, is_delete=True, user_id=user_id)
            deleted_stats['work_plan'] = True
            
            self.repository.soft_delete(maintenance_plan, user_id)
            
            if operator_name and maintenance_plan.id:
                self._create_operation_log(
                    work_order_type='maintenance_plan',
                    work_order_id=maintenance_plan.id,
                    work_order_no=maintenance_plan.plan_id,
                    operator_name=operator_name,
                    operator_id=user_id,
                    operation_type='delete',
                    operation_type_name='删除',
                    remark=f'删除维保计划 {maintenance_plan.plan_id}'
                )
            
            logger.info(f"✅ [Service] 维保计划软删除成功: plan_id={plan_id}, "
                       f"定期巡检={deleted_stats['periodic_inspections']}, "
                       f"临时维修={deleted_stats['temporary_repairs']}, "
                       f"零星用工={deleted_stats['spot_works']}")
            
            return deleted_stats
            
        except Exception as e:
            logger.error(f"❌ [Service] 软删除维保计划失败: plan_id={plan_id}, error={str(e)}")
            raise
    
    def update_status(self, id: int, status: str) -> MaintenancePlan:
        """
        更新计划状态
        
        Args:
            id: 维保计划ID
            status: 新状态
            
        Returns:
            更新后的维保计划对象
        """
        maintenance_plan = self.repository.update_status(id, status)
        if not maintenance_plan:
            raise NotFoundException("维保计划不存在")
        self.sync_service.sync_maintenance_plan_to_work_plan(maintenance_plan)
        return maintenance_plan
    
    def update_execution_status(
        self, 
        id: int, 
        status: str, 
        operator_id: Optional[int] = None, 
        operator_name: Optional[str] = None
    ) -> MaintenancePlan:
        """
        更新执行状态
        
        Args:
            id: 维保计划ID
            status: 新执行状态
            operator_id: 操作者ID
            operator_name: 操作者名称
            
        Returns:
            更新后的维保计划对象
        """
        maintenance_plan = self.repository.update_status(id, status)
        if not maintenance_plan:
            raise NotFoundException("维保计划不存在")
        self.sync_service.sync_maintenance_plan_to_work_plan(maintenance_plan)
        
        if operator_name and maintenance_plan.id:
            self._create_operation_log(
                work_order_type='maintenance_plan',
                work_order_id=maintenance_plan.id,
                work_order_no=maintenance_plan.plan_id,
                operator_name=operator_name,
                operator_id=operator_id,
                operation_type='status_change',
                operation_type_name='状态变更',
                remark=f'执行状态变更为: {status}'
            )
        
        return maintenance_plan
    
    def update_completion_rate(self, id: int, rate: int) -> MaintenancePlan:
        """
        更新完成率
        
        Args:
            id: 维保计划ID
            rate: 完成率 (0-100)
            
        Returns:
            更新后的维保计划对象
            
        Raises:
            ValidationException: 完成率不在有效范围内
        """
        if rate < 0 or rate > 100:
            from app.exceptions import ValidationException
            raise ValidationException("完成率必须在0-100之间")
        maintenance_plan = self.repository.update_completion_rate(id, rate)
        if not maintenance_plan:
            raise NotFoundException("维保计划不存在")
        self.sync_service.sync_maintenance_plan_to_work_plan(maintenance_plan)
        return maintenance_plan
    
    def get_all_unpaginated(self) -> List[MaintenancePlan]:
        """
        获取所有维保计划（不分页）
        
        Returns:
            维保计划列表
        """
        return self.repository.find_all_unpaginated()

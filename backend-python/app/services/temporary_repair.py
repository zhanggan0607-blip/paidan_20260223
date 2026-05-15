"""
临时维修服务
提供临时维修业务逻辑处理

权限说明：
- 部门经理创建临时维修工单，选择项目后，工单自动分配给该项目的运维人员
- 运维人员可以看到和操作自己负责项目的工单
- 管理员和部门经理可以看到所有工单
"""
import json
from app.utils.logging_config import get_logger
from datetime import datetime

from sqlalchemy.orm import Session

from app.services.base import BaseService
from app.exceptions import DuplicateException, NotFoundException, ValidationException
from app.models.temporary_repair import TemporaryRepair
from app.repositories.personnel import PersonnelRepository
from app.repositories.project_info import ProjectInfoRepository
from app.repositories.temporary_repair import TemporaryRepairRepository
from app.schemas.temporary_repair import TemporaryRepairCreate, TemporaryRepairUpdate
from app.services.sync_service import PLAN_TYPE_REPAIR, SyncService
from app.utils.date_utils import parse_datetime
from app.utils.dictionary_helper import get_default_temporary_repair_status
from app.utils.work_order_id_generator import generate_repair_id

logger = get_logger(__name__)


class TemporaryRepairService(BaseService):
    """
    临时维修服务
    提供临时维修的增删改查等业务逻辑
    """

    def __init__(self, db: Session):
        self.repository = TemporaryRepairRepository(db)
        self.personnel_repository = PersonnelRepository(db)
        self.project_repository = ProjectInfoRepository(db)
        self.sync_service = SyncService(db)
        super().__init__(db)

    def _validate_maintenance_personnel(self, personnel_name: str) -> None:
        """
        验证运维人员是否存在

        Args:
            personnel_name: 运维人员姓名

        Raises:
            ValidationException: 运维人员不存在
        """
        if personnel_name and not self.personnel_repository.find_by_name(personnel_name):
            raise ValidationException(
                f"运维人员'{personnel_name}'不存在于人员列表中，请先添加该人员"
            )

    def get_all(
        self,
        page: int = 0,
        size: int = 10,
        project_name: str | None = None,
        repair_id: str | None = None,
        status: str | None = None,
        maintenance_personnel: str | None = None,
        statuses: list[str] | None = None,
        created_by: str | None = None
    ) -> tuple[list[TemporaryRepair], int]:
        return self.repository.find_all(
            page, size, project_name, repair_id, status, maintenance_personnel,
            statuses=statuses, created_by=created_by
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
        operator_id: int | None = None,
        operator_name: str | None = None
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
        maintenance_personnel = dto.maintenance_personnel

        if not maintenance_personnel and dto.project_id:
            project = self.project_repository.find_by_project_id(dto.project_id)
            if project and project.project_manager:
                maintenance_personnel = project.project_manager
                logger.info(f"[临时维修创建] 从项目信息获取运维人员: project_id={dto.project_id}, project_manager={maintenance_personnel}")

        if maintenance_personnel:
            self._validate_maintenance_personnel(maintenance_personnel)

        repair_id = dto.repair_id
        if repair_id and self.repository.exists_by_repair_id(repair_id, include_deleted=True):
            raise DuplicateException("维修单编号已存在")

        if not repair_id:
            repair_id = generate_repair_id(self.repository.db, dto.project_id)

        default_status = get_default_temporary_repair_status(self._db)

        repair = TemporaryRepair(
            repair_id=repair_id,
            project_id=dto.project_id,
            project_name=dto.project_name,
            plan_start_date=parse_datetime(dto.plan_start_date),
            plan_end_date=parse_datetime(dto.plan_end_date),
            client_name=dto.client_name,
            client_contact=dto.client_contact if hasattr(dto, 'client_contact') else None,
            client_contact_info=dto.client_contact_info if hasattr(dto, 'client_contact_info') else None,
            maintenance_personnel=maintenance_personnel,
            created_by=operator_name,
            status=dto.status or default_status,
            remarks=dto.remarks,
            photos=dto.photos,
            fault_description=dto.fault_description,
            solution=dto.solution,
            signature=dto.signature,
            customer_signature=dto.customer_signature if hasattr(dto, 'customer_signature') else None,
            execution_date=parse_datetime(dto.execution_date) if dto.execution_date else None,
        )

        result = self.repository.create(repair)
        self.sync_service.sync_order_to_work_plan(PLAN_TYPE_REPAIR, result)

        if operator_name and result.id:
            self._create_operation_log(
                work_order_type='temporary_repair',
                work_order_id=result.id,
                work_order_no=result.repair_id,
                operator_name=operator_name,
                operator_id=operator_id,
                operation_type='create',
                operation_type_name='创建',
                remark=f'创建临时维修单，分配给运维人员: {maintenance_personnel or "未指定"}'
            )

        self._db.commit()
        return result

    def update(
        self,
        id: int,
        dto: TemporaryRepairUpdate,
        operator_id: int | None = None,
        operator_name: str | None = None
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
        existing_repair.plan_start_date = parse_datetime(dto.plan_start_date)
        existing_repair.plan_end_date = parse_datetime(dto.plan_end_date)
        existing_repair.client_name = dto.client_name
        existing_repair.client_contact = dto.client_contact if hasattr(dto, 'client_contact') else existing_repair.client_contact
        existing_repair.client_contact_info = dto.client_contact_info if hasattr(dto, 'client_contact_info') else existing_repair.client_contact_info
        existing_repair.maintenance_personnel = dto.maintenance_personnel
        existing_repair.status = dto.status
        existing_repair.remarks = dto.remarks
        existing_repair.fault_description = dto.fault_description
        existing_repair.solution = dto.solution
        existing_repair.photos = dto.photos if dto.photos is not None else None
        existing_repair.signature = dto.signature
        existing_repair.customer_signature = dto.customer_signature
        existing_repair.execution_date = parse_datetime(dto.execution_date)

        result = self.repository.update(existing_repair)
        self.sync_service.sync_order_to_work_plan(PLAN_TYPE_REPAIR, result)

        if operator_name and result.id:
            self._create_operation_log(
                work_order_type='temporary_repair',
                work_order_id=result.id,
                work_order_no=result.repair_id,
                operator_name=operator_name,
                operator_id=operator_id,
                operation_type='update',
                operation_type_name='更新',
                remark='更新临时维修单'
            )

        self._db.commit()
        return result

    def partial_update(
        self,
        id: int,
        dto,
        operator_id: int | None = None,
        operator_name: str | None = None
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
            existing_repair.plan_start_date = parse_datetime(dto.plan_start_date)
        if dto.plan_end_date is not None:
            existing_repair.plan_end_date = parse_datetime(dto.plan_end_date)
        if dto.client_name is not None:
            existing_repair.client_name = dto.client_name
        if hasattr(dto, 'client_contact') and dto.client_contact is not None:
            existing_repair.client_contact = dto.client_contact
        if hasattr(dto, 'client_contact_info') and dto.client_contact_info is not None:
            existing_repair.client_contact_info = dto.client_contact_info
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
            existing_repair.photos = dto.photos
        if hasattr(dto, 'signature') and dto.signature is not None:
            existing_repair.signature = dto.signature
        if hasattr(dto, 'customer_signature') and dto.customer_signature is not None:
            existing_repair.customer_signature = dto.customer_signature
        if hasattr(dto, 'execution_date') and dto.execution_date is not None:
            existing_repair.execution_date = parse_datetime(dto.execution_date)

        result = self.repository.update(existing_repair)
        self.sync_service.sync_order_to_work_plan(PLAN_TYPE_REPAIR, result)
        self._db.commit()
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
                work_order_type='temporary_repair',
                work_order_id=repair.id,
                work_order_no=repair.repair_id,
                operator_name=operator_name,
                operator_id=user_id,
                operation_type='delete',
                operation_type_name='删除',
                remark=f'删除临时维修单 {repair.repair_id}'
            )

        self.repository.soft_delete(repair, user_id)
        self._db.commit()

    def get_all_unpaginated(self) -> list[TemporaryRepair]:
        """
        获取所有临时维修（不分页）

        Returns:
            维修单列表
        """
        return self.repository.find_all_unpaginated()

    def get_user_project_ids(self, user_name: str) -> list[str]:
        """
        获取用户负责的项目编号列表

        Args:
            user_name: 用户名

        Returns:
            项目编号列表
        """
        projects = self._db.query(self.project_repository.model).filter(
            self.project_repository.model.project_manager == user_name
        ).all()
        return [p.project_id for p in projects]

    def filter_by_user_access(
        self,
        items: list[TemporaryRepair],
        user_name: str,
        is_manager: bool
    ) -> list[TemporaryRepair]:
        """
        根据用户权限过滤工单列表

        管理员可以看到所有工单
        运维人员只能看到自己负责项目的工单（maintenance_personnel匹配）

        Args:
            items: 工单列表
            user_name: 用户名
            is_manager: 是否为管理员

        Returns:
            过滤后的工单列表
        """
        if is_manager:
            return items

        return [item for item in items if item.maintenance_personnel == user_name]

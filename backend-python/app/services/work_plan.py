"""
工作计划服务
提供工作计划业务逻辑处理
"""
from datetime import date, datetime, timedelta

from sqlalchemy.orm import Session

from app.exceptions import DuplicateException, NotFoundException, ValidationException
from app.models.work_plan import WorkPlan
from app.repositories.work_plan import WorkPlanRepository
from app.schemas.work_plan import WorkPlanCreate, WorkPlanUpdate
from app.services.sync_service import SyncService
from app.utils.date_utils import parse_date, parse_datetime

PLAN_TYPES = ['定期巡检', '临时维修', '零星用工']


class WorkPlanService:
    """
    工作计划服务类
    提供工作计划的增删改查和统计功能
    """

    def __init__(self, db: Session):
        """
        初始化工作计划服务

        Args:
            db: 数据库会话对象
        """
        self.repository = WorkPlanRepository(db)
        self.sync_service = SyncService(db)
        self._db = db

    def _parse_date_field(self, date_value: str | datetime | None) -> datetime | None:
        """
        解析日期字符串为datetime对象

        Args:
            date_value: 日期值，可以是字符串或datetime对象

        Returns:
            解析后的datetime对象，解析失败返回None
        """
        return parse_datetime(date_value)

    def _get_date_value(self, date_field) -> date | None:
        """
        获取日期字段的date值

        Args:
            date_field: 日期字段，可以是datetime或date对象

        Returns:
            date对象
        """
        return parse_date(date_field)

    def _create_operation_log(
        self,
        work_order_id: int,
        work_order_no: str,
        operator_name: str,
        operator_id: int | None,
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
            work_order_type='work_plan',
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
        plan_type: str | None = None,
        project_name: str | None = None,
        client_name: str | None = None,
        status: str | None = None,
        maintenance_personnel: str | None = None
    ) -> tuple[list[WorkPlan], int]:
        """
        分页获取工作计划列表

        Args:
            page: 页码，从0开始
            size: 每页大小
            plan_type: 计划类型筛选
            project_name: 项目名称模糊查询
            client_name: 客户名称筛选
            status: 状态筛选
            maintenance_personnel: 维保人员筛选

        Returns:
            (工作计划列表, 总数) 元组
        """
        return self.repository.find_all(
            page, size, plan_type, project_name, client_name, status, maintenance_personnel
        )

    def get_by_id(self, id: int) -> WorkPlan:
        """
        根据ID获取工作计划

        Args:
            id: 工作计划ID

        Returns:
            工作计划对象

        Raises:
            NotFoundException: 工作计划不存在
        """
        work_plan = self.repository.find_by_id(id)
        if not work_plan:
            raise NotFoundException("工作计划不存在")
        return work_plan

    def get_by_plan_id(self, plan_id: str) -> WorkPlan:
        """
        根据计划编号获取工作计划

        Args:
            plan_id: 计划编号

        Returns:
            工作计划对象

        Raises:
            NotFoundException: 工作计划不存在
        """
        work_plan = self.repository.find_by_plan_id(plan_id)
        if not work_plan:
            raise NotFoundException("工作计划不存在")
        return work_plan

    def create(
        self,
        dto: WorkPlanCreate,
        operator_id: int | None = None,
        operator_name: str | None = None
    ) -> WorkPlan:
        """
        创建新工作计划
        创建后会同步到对应的工单表和维保计划表

        Args:
            dto: 工作计划创建数据传输对象
            operator_id: 操作者ID
            operator_name: 操作者名称

        Returns:
            创建成功的工作计划对象

        Raises:
            ValidationException: 计划类型无效
            DuplicateException: 计划编号已存在
        """
        if dto.plan_type not in PLAN_TYPES:
            raise ValidationException(f"工单类型必须是以下之一: {', '.join(PLAN_TYPES)}")

        if self.repository.exists_by_plan_id(dto.plan_id):
            raise DuplicateException("计划编号已存在")

        work_plan = WorkPlan(
            plan_id=dto.plan_id,
            plan_name=dto.plan_name,
            plan_type=dto.plan_type,
            project_id=dto.project_id,
            project_name=dto.project_name,
            plan_start_date=self._parse_date_field(dto.plan_start_date),
            plan_end_date=self._parse_date_field(dto.plan_end_date),
            client_name=dto.client_name,
            maintenance_personnel=dto.maintenance_personnel,
            status=dto.status or "执行中",
            filled_count=dto.filled_count or 0,
            total_count=dto.total_count or 5,
            remarks=dto.remarks
        )

        result = self.repository.create(work_plan)
        self.sync_service.sync_work_plan_to_order(result)
        self.sync_service.sync_work_plan_to_maintenance_plan(result)

        if operator_name and result.id:
            self._create_operation_log(
                work_order_id=result.id,
                work_order_no=result.plan_id,
                operator_name=operator_name,
                operator_id=operator_id,
                operation_type='create',
                operation_type_name='创建',
                remark='创建工作计划'
            )

        return result

    def update(
        self,
        id: int,
        dto: WorkPlanUpdate,
        operator_id: int | None = None,
        operator_name: str | None = None
    ) -> WorkPlan:
        """
        更新工作计划
        更新后会同步到对应的工单表和维保计划表

        Args:
            id: 工作计划ID
            dto: 工作计划更新数据传输对象
            operator_id: 操作者ID
            operator_name: 操作者名称

        Returns:
            更新后的工作计划对象

        Raises:
            NotFoundException: 工作计划不存在
            ValidationException: 计划类型无效
            DuplicateException: 计划编号已存在
        """
        existing_plan = self.get_by_id(id)

        if dto.plan_type not in PLAN_TYPES:
            raise ValidationException(f"工单类型必须是以下之一: {', '.join(PLAN_TYPES)}")

        if existing_plan.plan_id != dto.plan_id and self.repository.exists_by_plan_id(dto.plan_id):
            raise DuplicateException("计划编号已存在")

        existing_plan.plan_id = dto.plan_id
        existing_plan.plan_name = dto.plan_name
        existing_plan.plan_type = dto.plan_type
        existing_plan.project_id = dto.project_id
        existing_plan.project_name = dto.project_name
        existing_plan.plan_start_date = self._parse_date_field(dto.plan_start_date)
        existing_plan.plan_end_date = self._parse_date_field(dto.plan_end_date)
        existing_plan.client_name = dto.client_name
        existing_plan.maintenance_personnel = dto.maintenance_personnel
        existing_plan.status = dto.status
        existing_plan.filled_count = dto.filled_count or 0
        existing_plan.total_count = dto.total_count or 5
        existing_plan.remarks = dto.remarks

        result = self.repository.update(existing_plan)
        self.sync_service.sync_work_plan_to_order(result)
        self.sync_service.sync_work_plan_to_maintenance_plan(result)

        if operator_name and result.id:
            self._create_operation_log(
                work_order_id=result.id,
                work_order_no=result.plan_id,
                operator_name=operator_name,
                operator_id=operator_id,
                operation_type='update',
                operation_type_name='更新',
                remark='更新工作计划'
            )

        return result

    def delete(self, id: int, user_id: int = None, operator_name: str = None) -> None:
        """
        软删除工作计划
        删除前会同步软删除关联的工单和维保计划

        Args:
            id: 工作计划ID
            user_id: 执行删除的用户ID
            operator_name: 操作者名称
        """
        work_plan = self.get_by_id(id)

        if operator_name and work_plan.id:
            self._create_operation_log(
                work_order_id=work_plan.id,
                work_order_no=work_plan.plan_id,
                operator_name=operator_name,
                operator_id=user_id,
                operation_type='delete',
                operation_type_name='删除',
                remark=f'删除工作计划 {work_plan.plan_id}'
            )

        self.sync_service.sync_work_plan_to_order(work_plan, is_delete=True, user_id=user_id)
        self.sync_service.sync_work_plan_to_maintenance_plan(work_plan, is_delete=True, user_id=user_id)
        self.repository.soft_delete(work_plan, user_id)

    def get_all_unpaginated(self, plan_type: str | None = None) -> list[WorkPlan]:
        """
        获取所有工作计划（不分页）

        Args:
            plan_type: 计划类型筛选

        Returns:
            工作计划列表
        """
        return self.repository.find_all_unpaginated(plan_type)

    def get_statistics(self, user_name: str | None = None, is_manager: bool = False) -> dict:
        """
        获取统计数据

        临期工单：计划开始日期在未来7天内且未完成
        超期工单：计划结束日期已过且未完成

        Args:
            user_name: 用户名（用于权限过滤）
            is_manager: 是否为管理员

        Returns:
            统计数据字典
        """
        from app.config import OverdueAlertConfig
        from app.repositories.periodic_inspection import PeriodicInspectionRepository
        from app.repositories.spot_work import SpotWorkRepository
        from app.repositories.temporary_repair import TemporaryRepairRepository

        today = datetime.now().date()
        year_start = datetime(today.year, 1, 1).date()
        year_end = datetime(today.year, 12, 31).date()

        valid_statuses = OverdueAlertConfig.VALID_STATUSES

        inspection_repo = PeriodicInspectionRepository(self.repository.db)
        repair_repo = TemporaryRepairRepository(self.repository.db)
        spotwork_repo = SpotWorkRepository(self.repository.db)

        all_inspections = inspection_repo.find_all_unpaginated()
        all_repairs = repair_repo.find_all_unpaginated()
        all_spotworks = spotwork_repo.find_all_unpaginated()

        if not is_manager and user_name:
            all_inspections = [p for p in all_inspections if p.maintenance_personnel == user_name]
            all_repairs = [p for p in all_repairs if p.maintenance_personnel == user_name]
            all_spotworks = [p for p in all_spotworks if p.maintenance_personnel == user_name]

        expiring_soon = 0
        overdue = 0
        yearly_completed = 0
        periodic_inspection_count = 0
        temporary_repair_count = 0
        spot_work_count = 0

        all_orders = []
        for item in all_inspections:
            all_orders.append(('定期巡检', item))
            plan_start = self._get_date_value(item.plan_start_date)
            if plan_start and year_start <= plan_start <= year_end:
                if item.status in valid_statuses:
                    periodic_inspection_count += 1
        for item in all_repairs:
            all_orders.append(('临时维修', item))
            plan_start = self._get_date_value(item.plan_start_date)
            if plan_start and year_start <= plan_start <= year_end:
                if item.status in valid_statuses:
                    temporary_repair_count += 1
        for item in all_spotworks:
            all_orders.append(('零星用工', item))
            plan_start = self._get_date_value(item.plan_start_date)
            if plan_start and year_start <= plan_start <= year_end:
                if item.status in valid_statuses:
                    spot_work_count += 1

        for _plan_type, order in all_orders:
            plan_start = self._get_date_value(order.plan_start_date)
            plan_end = self._get_date_value(order.plan_end_date)
            actual_completion = self._get_date_value(order.actual_completion_date)

            if order.status in valid_statuses:
                if plan_start and today <= plan_start <= today + timedelta(days=7):
                    expiring_soon += 1

                if plan_end and plan_end < today:
                    overdue += 1

            if order.status in OverdueAlertConfig.COMPLETED_STATUSES and actual_completion:
                if year_start <= actual_completion <= year_end:
                    yearly_completed += 1

        return {
            'expiringSoon': expiring_soon,
            'overdue': overdue,
            'yearlyCompleted': yearly_completed,
            'periodicInspection': periodic_inspection_count,
            'temporaryRepair': temporary_repair_count,
            'spotWork': spot_work_count
        }

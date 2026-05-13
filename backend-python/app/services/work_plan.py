"""
工作计划服务
提供工作计划业务逻辑处理
"""
from datetime import date, datetime, timedelta

from sqlalchemy import and_, case, func
from sqlalchemy.orm import Session

from app.exceptions import DuplicateException, NotFoundException, ValidationException
from app.models.work_plan import WorkPlan
from app.repositories.work_plan import WorkPlanRepository
from app.schemas.work_plan import WorkPlanCreate, WorkPlanUpdate
from app.services.base import BaseService
from app.services.sync_service import SyncService
from app.utils.date_utils import parse_date, parse_datetime

PLAN_TYPES = ['定期巡检', '临时维修', '零星用工']


class WorkPlanService(BaseService):

    def __init__(self, db: Session):
        super().__init__(db)
        self.repository = WorkPlanRepository(db)
        self.sync_service = SyncService(db)

    def _get_date_value(self, date_field) -> date | None:
        return parse_date(date_field)

    def get_all(
        self,
        page: int = 0,
        size: int = 10,
        plan_type: str | None = None,
        project_name: str | None = None,
        client_name: str | None = None,
        status: str | None = None,
        maintenance_personnel: str | None = None,
        plan_id: str | None = None
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
            plan_id: 计划编号模糊查询

        Returns:
            (工作计划列表, 总数) 元组
        """
        return self.repository.find_all(
            page, size, plan_type, project_name, client_name, status, maintenance_personnel, plan_id
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
            plan_start_date=parse_datetime(dto.plan_start_date),
            plan_end_date=parse_datetime(dto.plan_end_date),
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
                work_order_type='work_plan',
                work_order_id=result.id,
                work_order_no=result.plan_id,
                operator_name=operator_name,
                operator_id=operator_id,
                operation_type='create',
                operation_type_name='创建',
                remark='创建工作计划'
            )

        self.commit()
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
        existing_plan.plan_start_date = parse_datetime(dto.plan_start_date)
        existing_plan.plan_end_date = parse_datetime(dto.plan_end_date)
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
                work_order_type='work_plan',
                work_order_id=result.id,
                work_order_no=result.plan_id,
                operator_name=operator_name,
                operator_id=operator_id,
                operation_type='update',
                operation_type_name='更新',
                remark='更新工作计划'
            )

        self.commit()
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
                work_order_type='work_plan',
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
        self.commit()

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
        from app.config import OverdueAlertConfig
        from app.models.periodic_inspection import PeriodicInspection
        from app.models.temporary_repair import TemporaryRepair
        from app.models.spot_work import SpotWork

        today = datetime.now().date()
        today_start = datetime.combine(today, datetime.min.time())
        week_end = datetime.combine(today + timedelta(days=7), datetime.max.time())
        year_start = datetime(today.year, 1, 1)
        year_end = datetime(today.year, 12, 31, 23, 59, 59)

        valid_statuses = OverdueAlertConfig.VALID_STATUSES
        completed_statuses = OverdueAlertConfig.COMPLETED_STATUSES

        def _count_by_model(model):
            query = self._db.query(
                func.sum(case(
                    (and_(
                        model.plan_start_date.between(today_start, week_end),
                        model.status.in_(valid_statuses)
                    ), 1), else_=0
                )).label('expiring_soon'),
                func.sum(case(
                    (and_(
                        model.plan_end_date < today_start,
                        model.status.in_(valid_statuses)
                    ), 1), else_=0
                )).label('overdue'),
                func.sum(case(
                    (and_(
                        model.status.in_(completed_statuses),
                        model.actual_completion_date.between(year_start, year_end)
                    ), 1), else_=0
                )).label('yearly_completed'),
                func.sum(case(
                    (and_(
                        model.plan_start_date.between(year_start, year_end),
                        model.status.in_(valid_statuses)
                    ), 1), else_=0
                )).label('active_count'),
            ).filter(model.is_deleted == False)

            if not is_manager and user_name:
                query = query.filter(model.maintenance_personnel == user_name)

            return query.one()

        insp = _count_by_model(PeriodicInspection)
        repair = _count_by_model(TemporaryRepair)
        spot = _count_by_model(SpotWork)

        return {
            'expiringSoon': int((insp.expiring_soon or 0) + (repair.expiring_soon or 0) + (spot.expiring_soon or 0)),
            'overdue': int((insp.overdue or 0) + (repair.overdue or 0) + (spot.overdue or 0)),
            'yearlyCompleted': int((insp.yearly_completed or 0) + (repair.yearly_completed or 0) + (spot.yearly_completed or 0)),
            'periodicInspection': int(insp.active_count or 0),
            'temporaryRepair': int(repair.active_count or 0),
            'spotWork': int(spot.active_count or 0),
        }

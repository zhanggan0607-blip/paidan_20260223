from typing import List, Optional, Union
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.work_plan import WorkPlan
from app.repositories.work_plan import WorkPlanRepository
from app.services.sync_service import SyncService
from app.schemas.work_plan import WorkPlanCreate, WorkPlanUpdate
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
        @param db: 数据库会话对象
        """
        self.repository = WorkPlanRepository(db)
        self.sync_service = SyncService(db)
    
    def _parse_date_field(self, date_value: Union[str, datetime, None]) -> Optional[datetime]:
        """
        解析日期字符串为datetime对象
        @param date_value: 日期值，可以是字符串或datetime对象
        @return: 解析后的datetime对象，解析失败返回None
        """
        return parse_datetime(date_value)
    
    def _get_date_value(self, date_field) -> Optional[datetime.date]:
        """
        获取日期字段的date值
        @param date_field: 日期字段，可以是datetime或date对象
        @return: date对象
        """
        return parse_date(date_field)
    
    def get_all(
        self, 
        page: int = 0, 
        size: int = 10,
        plan_type: Optional[str] = None,
        project_name: Optional[str] = None,
        client_name: Optional[str] = None,
        status: Optional[str] = None,
        maintenance_personnel: Optional[str] = None
    ) -> tuple[List[WorkPlan], int]:
        """
        分页获取工作计划列表
        @param page: 页码，从0开始
        @param size: 每页大小
        @param plan_type: 计划类型筛选
        @param project_name: 项目名称模糊查询
        @param client_name: 客户名称筛选
        @param status: 状态筛选
        @param maintenance_personnel: 维保人员筛选
        @return: (工作计划列表, 总数) 元组
        """
        return self.repository.find_all(
            page, size, plan_type, project_name, client_name, status, maintenance_personnel
        )
    
    def get_by_id(self, id: int) -> WorkPlan:
        """
        根据ID获取工作计划
        @param id: 工作计划ID
        @return: 工作计划对象
        @raises HTTPException: 工作计划不存在时抛出404异常
        """
        work_plan = self.repository.find_by_id(id)
        if not work_plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="工作计划不存在"
            )
        return work_plan
    
    def get_by_plan_id(self, plan_id: str) -> WorkPlan:
        """
        根据计划编号获取工作计划
        @param plan_id: 计划编号
        @return: 工作计划对象
        @raises HTTPException: 工作计划不存在时抛出404异常
        """
        work_plan = self.repository.find_by_plan_id(plan_id)
        if not work_plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="工作计划不存在"
            )
        return work_plan
    
    def create(self, dto: WorkPlanCreate) -> WorkPlan:
        """
        创建新工作计划
        创建后会同步到对应的工单表和维保计划表
        @param dto: 工作计划创建数据传输对象
        @return: 创建成功的工作计划对象
        @raises HTTPException: 计划类型无效或编号重复时抛出400异常
        """
        if dto.plan_type not in PLAN_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"工单类型必须是以下之一: {', '.join(PLAN_TYPES)}"
            )
        
        if self.repository.exists_by_plan_id(dto.plan_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="计划编号已存在"
            )
        
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
            status=dto.status or "未进行",
            filled_count=dto.filled_count or 0,
            total_count=dto.total_count or 5,
            remarks=dto.remarks
        )
        
        result = self.repository.create(work_plan)
        self.sync_service.sync_work_plan_to_order(result)
        self.sync_service.sync_work_plan_to_maintenance_plan(result)
        return result
    
    def update(self, id: int, dto: WorkPlanUpdate) -> WorkPlan:
        """
        更新工作计划
        更新后会同步到对应的工单表和维保计划表
        @param id: 工作计划ID
        @param dto: 工作计划更新数据传输对象
        @return: 更新后的工作计划对象
        @raises HTTPException: 计划类型无效或编号重复时抛出400异常
        """
        existing_plan = self.get_by_id(id)
        
        if dto.plan_type not in PLAN_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"工单类型必须是以下之一: {', '.join(PLAN_TYPES)}"
            )
        
        if existing_plan.plan_id != dto.plan_id and self.repository.exists_by_plan_id(dto.plan_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="计划编号已存在"
            )
        
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
        return result
    
    def delete(self, id: int) -> None:
        """
        删除工作计划
        删除前会同步删除关联的工单和维保计划
        @param id: 工作计划ID
        """
        work_plan = self.get_by_id(id)
        self.sync_service.sync_work_plan_to_order(work_plan, is_delete=True)
        self.sync_service.sync_work_plan_to_maintenance_plan(work_plan, is_delete=True)
        self.repository.delete(work_plan)
    
    def get_all_unpaginated(self, plan_type: Optional[str] = None) -> List[WorkPlan]:
        """
        获取所有工作计划（不分页）
        @param plan_type: 计划类型筛选
        @return: 工作计划列表
        """
        return self.repository.find_all_unpaginated(plan_type)
    
    def get_statistics(self, user_name: Optional[str] = None, is_manager: bool = False) -> dict:
        """
        获取统计数据
        
        临期工单：计划开始日期在未来7天内且未完成
        超期工单：计划结束日期已过且未完成
        
        TODO: 这个方法太长了，需要拆分
        FIXME: 性能问题：全量查询后过滤，数据量大时会很慢
        """
        from app.repositories.periodic_inspection import PeriodicInspectionRepository
        from app.repositories.temporary_repair import TemporaryRepairRepository
        from app.repositories.spot_work import SpotWorkRepository
        from app.config import OverdueAlertConfig
        
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
                periodic_inspection_count += 1
        for item in all_repairs:
            all_orders.append(('临时维修', item))
            plan_start = self._get_date_value(item.plan_start_date)
            if plan_start and year_start <= plan_start <= year_end:
                temporary_repair_count += 1
        for item in all_spotworks:
            all_orders.append(('零星用工', item))
            plan_start = self._get_date_value(item.plan_start_date)
            if plan_start and year_start <= plan_start <= year_end:
                spot_work_count += 1
        
        for plan_type, order in all_orders:
            plan_start = self._get_date_value(order.plan_start_date)
            plan_end = self._get_date_value(order.plan_end_date)
            actual_completion = self._get_date_value(order.actual_completion_date)
            
            if order.status in valid_statuses:
                if plan_start:
                    if today <= plan_start <= today + timedelta(days=7):
                        expiring_soon += 1
                
                if plan_end:
                    if plan_end < today:
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

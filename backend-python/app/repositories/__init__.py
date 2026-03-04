"""
Repository层统一导出
提供所有Repository的统一入口
"""
from app.repositories.base import BaseRepository
from app.repositories.spot_work import SpotWorkRepository
from app.repositories.periodic_inspection import PeriodicInspectionRepository
from app.repositories.temporary_repair import TemporaryRepairRepository
from app.repositories.periodic_inspection_record import PeriodicInspectionRecordRepository
from app.repositories.work_order_operation_log import WorkOrderOperationLogRepository
from app.repositories.customer import CustomerRepository
from app.repositories.dictionary import DictionaryRepository
from app.repositories.inspection_item import InspectionItemRepository
from app.repositories.maintenance_plan import MaintenancePlanRepository
from app.repositories.personnel import PersonnelRepository
from app.repositories.project_info import ProjectInfoRepository
from app.repositories.spare_parts_usage import SparePartsUsageRepository
from app.repositories.user_dashboard_config import UserDashboardConfigRepository
from app.repositories.weekly_report import WeeklyReportRepository
from app.repositories.work_plan import WorkPlanRepository

__all__ = [
    'BaseRepository',
    'SpotWorkRepository',
    'PeriodicInspectionRepository',
    'TemporaryRepairRepository',
    'PeriodicInspectionRecordRepository',
    'WorkOrderOperationLogRepository',
    'CustomerRepository',
    'DictionaryRepository',
    'InspectionItemRepository',
    'MaintenancePlanRepository',
    'PersonnelRepository',
    'ProjectInfoRepository',
    'SparePartsUsageRepository',
    'UserDashboardConfigRepository',
    'WeeklyReportRepository',
    'WorkPlanRepository',
]

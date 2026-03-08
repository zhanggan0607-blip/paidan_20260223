"""
服务层统一导出
提供所有服务的统一入口
"""
from app.services.customer import CustomerService
from app.services.dictionary import DictionaryService
from app.services.expiring_soon import ExpiringSoonService
from app.services.inspection_item import InspectionItemService
from app.services.maintenance_plan import MaintenancePlanService
from app.services.overdue_alert import OverdueAlertService
from app.services.periodic_inspection import PeriodicInspectionService
from app.services.periodic_inspection_record import PeriodicInspectionRecordService
from app.services.personnel import PersonnelService
from app.services.project_info import ProjectInfoService
from app.services.spare_parts_usage import SparePartsUsageService
from app.services.spot_work import SpotWorkService
from app.services.sync_service import SyncService
from app.services.temporary_repair import TemporaryRepairService
from app.services.weekly_report import WeeklyReportService
from app.services.work_order_operation_log import WorkOrderOperationLogService
from app.services.work_plan import WorkPlanService

__all__ = [
    'SpotWorkService',
    'PeriodicInspectionService',
    'TemporaryRepairService',
    'PeriodicInspectionRecordService',
    'WorkOrderOperationLogService',
    'CustomerService',
    'DictionaryService',
    'ExpiringSoonService',
    'InspectionItemService',
    'MaintenancePlanService',
    'OverdueAlertService',
    'PersonnelService',
    'ProjectInfoService',
    'SparePartsUsageService',
    'SyncService',
    'WeeklyReportService',
    'WorkPlanService',
]

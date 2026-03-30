/**
 * 业务模型类型定义统一导出
 */

export type {
  SpotWork,
  SpotWorkWorker,
  SpotWorkCreate,
  SpotWorkUpdate,
  SpotWorkQueryParams,
  QuickFillRequest,
  WorkersSaveRequest
} from './spotWork'

export type {
  StatisticsOverview,
  WorkByPerson,
  TopProject
} from './statistics'

export type {
  ProjectInfo,
  ProjectInfoCreate,
  ProjectInfoUpdate,
  ProjectInfoQueryParams
} from './projectInfo'

export type {
  Personnel,
  PersonnelCreate,
  PersonnelUpdate,
  PersonnelQueryParams
} from './personnel'

export type {
  PeriodicInspection,
  PeriodicInspectionRecord,
  PeriodicInspectionCreate,
  PeriodicInspectionUpdate,
  PeriodicInspectionQueryParams
} from './periodicInspection'

export type {
  TemporaryRepair,
  TemporaryRepairCreate,
  TemporaryRepairUpdate,
  TemporaryRepairQueryParams
} from './temporaryRepair'

export type {
  SparePartsStock,
  SparePartsUsage,
  SparePartsInbound,
  SparePartsIssueRequest,
  SparePartsReturnRequest,
  SparePartsInboundRequest,
  SparePartsStockQueryParams,
  SparePartsUsageQueryParams
} from './spareParts'

export type {
  MaintenancePlan,
  InspectionItem,
  WeeklyReport,
  MaintenanceLog,
  OperationLog,
  OverdueAlertItem,
  OnlineUser,
  OnlineCount,
  OnlineStatistics,
  DictionaryItem,
  Customer,
  IDCardOCRResult
} from './common'

export type {
  WorkOrderItem,
  WorkOrderQueryParams
} from './workOrder'

export type {
  WorkPlan,
  WorkPlanQueryParams,
  WorkPlanCreate,
  WorkPlanUpdate,
  WorkPlanStatistics
} from './workPlan'

export type {
  WeeklyReportQueryParams,
  WeeklyReportCreate,
  WeeklyReportUpdate
} from './weeklyReport'

export type {
  MaintenanceLogQueryParams,
  MaintenanceLogCreate,
  MaintenanceLogUpdate
} from './maintenanceLog'

export type {
  RepairToolsStock,
  RepairToolsUsage,
  RepairToolsIssueRequest,
  RepairToolsReturnRequest,
  RepairToolsStockQueryParams,
  RepairToolsUsageQueryParams
} from './repairTools'

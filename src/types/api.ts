export type {
  ApiResponse,
  PaginatedData,
  PaginatedResponse,
  QueryParams,
  ApiError,
  User,
  UserInfo,
  TokenPayload,
  LoginRequest,
  LoginResponse,
  RefreshTokenResponse,
  SpotWork,
  SpotWorkWorker,
  StatisticsOverview,
  WorkByPerson,
  TopProject,
  ProjectInfo,
  ProjectInfoCreate,
  ProjectInfoUpdate,
  Personnel,
  PersonnelCreate,
  PersonnelUpdate,
  PeriodicInspection,
  TemporaryRepair,
  SparePartsStock,
  SparePartsUsage,
  SparePartsInbound,
  InspectionItem,
  MaintenancePlan,
  OperationLog,
} from '@sstcp/shared'

export interface SparePartsStockQueryParams {
  page: number
  pageSize: number
  product?: string
  user?: string
}

export interface TreeNode {
  id: number
  label: string
  level: number
  parent_id?: number
  check_requirement?: string
  children?: TreeNode[]
}

/**
 * PC端类型定义
 * 从shared包导入共享类型，保留PC端特有的类型
 */

export type {
  ApiResponse,
  PaginatedData,
  PaginatedResponse,
  LegacyPaginatedResponse,
  QueryParams,
  ListQueryParams,
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
  MaintenancePlan
} from '@sstcp/shared'

export interface SparePartsIssueQueryParams {
  page: number
  pageSize: number
  user?: string
  product?: string
  project?: string
}

export interface SparePartsStockQueryParams {
  page: number
  pageSize: number
  product?: string
  user?: string
}

export interface DashboardItem {
  id: string
  visible: boolean
  position: number
}

export interface DashboardConfig {
  cards: DashboardItem[]
  charts: DashboardItem[]
}

export interface DragItem {
  id: string
  visible: boolean
  position: number
}

export interface TreeNode {
  id: number
  label: string
  level: number
  parent_id?: number
  check_requirement?: string
  children?: TreeNode[]
}

export interface ToastState {
  visible: boolean
  message: string
  type: 'success' | 'error' | 'warning' | 'info'
}

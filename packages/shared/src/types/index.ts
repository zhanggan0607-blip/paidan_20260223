/**
 * 类型定义统一导出
 */

// 导出所有类型（interface 和 type）
export type {
  UserRole,
  RoleCodeType,
  RoleConfig,
  PermissionConfig
} from './permission'

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
  RefreshTokenResponse
} from './api'

// 导出业务模型类型
export type {
  SpotWork,
  SpotWorkWorker,
  SpotWorkCreate,
  SpotWorkUpdate,
  SpotWorkQueryParams,
  QuickFillRequest,
  WorkersSaveRequest
} from './models/spotWork'

// 导出所有值（const 和 function）
export {
  RoleCode,
  ADMIN_ROLES,
  ALL_ROLES,
  MANAGER_ROLES,
  PROJECT_MANAGEMENT_ROLES,
  PERSONNEL_MANAGEMENT_ROLES,
  SPARE_PARTS_MANAGEMENT_ROLES,
  WORK_ORDER_VIEW_ROLES,
  WORK_ORDER_APPROVE_ROLES,
  STATISTICS_VIEW_ROLES,
  MAINTENANCE_LOG_FILL_ROLES,
  MAINTENANCE_LOG_VIEW_ROLES,
  WEEKLY_REPORT_FILL_ROLES,
  WEEKLY_REPORT_VIEW_ROLES,
  ROLE_CONFIGS,
  isAdminRole,
  isManagerRole,
  isMaterialManager,
  canViewAllWorkOrders,
  canManagePersonnel,
  canManageProjects,
  canManagePlans,
  canApproveWorkOrders,
  canViewStatistics,
  canManageSpareParts,
  canViewSpareParts,
  canViewWorkOrder,
  canViewSignature,
  getRoleLevel,
  hasPermission,
  getAllowedPermissions
} from './permission'

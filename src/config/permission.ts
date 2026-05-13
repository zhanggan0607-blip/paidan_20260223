import type { PermissionConfig } from '@sstcp/shared'
import {
  RoleCode,
  COMMON_PERMISSION_CONFIGS,
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
  isAdminRole,
  isManagerRole,
  canDeleteWorkOrder,
  hasPermission as sharedHasPermission,
} from '@sstcp/shared'

export { RoleCode, isAdminRole, isManagerRole, canDeleteWorkOrder }
export type { UserRole, RoleCodeType, PermissionConfig } from '@sstcp/shared'

const PERMISSION_CONFIGS: Record<string, PermissionConfig> = {
  ...COMMON_PERMISSION_CONFIGS,
}

const MENU_PERMISSION_MAP: Record<string, string> = {
  statistics: 'view_statistics',
  'project-info': 'view_project_management',
  'maintenance-plan': 'view_project_management',
  'overdue-alert': 'view_alerts',
  'near-expiry-alert': 'view_alerts',
  personnel: 'view_personnel',
  customer: 'view_system_management',
  'inspection-item': 'view_system_management',
  'work-plan': 'view_work_order',
  'temporary-repair': 'view_work_order',
  'spot-work': 'view_work_order',
  'spare-parts-stock': 'view_spare_parts_stock',
  'spare-parts-issue': 'view_spare_parts_issue',
  'spare-parts-return': 'view_spare_parts_issue',
  'repair-tools-inbound': 'view_repair_tools_stock',
  'repair-tools-issue': 'view_repair_tools_issue',
  'repair-tools-return': 'view_repair_tools_issue',
  'maintenance-log-fill': 'fill_maintenance_log',
  'maintenance-log-list': 'view_maintenance_log',
  'weekly-report-fill': 'fill_weekly_report',
  'weekly-report-list': 'view_weekly_report',
}

const DEFAULT_ROUTE_ORDER = [
  'statistics',
  'project-info',
  'maintenance-plan',
  'overdue-alert',
  'near-expiry-alert',
  'personnel',
  'customer',
  'inspection-item',
  'work-plan',
  'temporary-repair',
  'spot-work',
  'spare-parts-stock',
  'spare-parts-issue',
  'spare-parts-return',
  'repair-tools-inbound',
  'repair-tools-issue',
  'repair-tools-return',
  'maintenance-log-fill',
  'maintenance-log-list',
  'weekly-report-fill',
  'weekly-report-list',
]

const MENU_PATH_MAP: Record<string, string> = {
  statistics: '/statistics',
  'project-info': '/project-info',
  'maintenance-plan': '/maintenance-plan',
  'overdue-alert': '/overdue-alert',
  'near-expiry-alert': '/near-expiry-alert',
  personnel: '/personnel',
  customer: '/customer',
  'inspection-item': '/inspection-item',
  'work-plan': '/work-plan',
  'temporary-repair': '/work-order/temporary-repair',
  'spot-work': '/work-order/spot-work',
  'spare-parts-stock': '/spare-parts/stock',
  'spare-parts-issue': '/spare-parts/issue',
  'spare-parts-return': '/spare-parts/return',
  'repair-tools-inbound': '/repair-tools/inbound',
  'repair-tools-issue': '/repair-tools/issue',
  'repair-tools-return': '/repair-tools/return',
  'maintenance-log-fill': '/maintenance-log/fill',
  'maintenance-log-list': '/maintenance-log/list',
  'weekly-report-fill': '/weekly-report/fill',
  'weekly-report-list': '/weekly-report/list',
}

export function getDefaultPath(role: string | undefined | null): string {
  if (!role) return '/login'
  for (const menuId of DEFAULT_ROUTE_ORDER) {
    if (canShowMenu(menuId, role)) {
      return MENU_PATH_MAP[menuId] || `/${menuId}`
    }
  }
  return '/login'
}

export function hasPermission(role: string | undefined | null, permissionId: string): boolean {
  return sharedHasPermission(role, permissionId, PERMISSION_CONFIGS)
}

export function canShowMenu(menuId: string, role: string | undefined | null): boolean {
  if (!role) return false
  const permissionId = MENU_PERMISSION_MAP[menuId]
  if (!permissionId) return false
  return hasPermission(role, permissionId)
}

import type { PermissionConfig } from '@sstcp/shared'
import {
  RoleCode,
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
} from '@sstcp/shared'

export { RoleCode, isAdminRole, isManagerRole, canDeleteWorkOrder }
export type { UserRole, RoleCodeType, RoleConfig, PermissionConfig } from '@sstcp/shared'

const PERMISSION_CONFIGS: Record<string, PermissionConfig> = {
  view_statistics: {
    id: 'view_statistics',
    name: '查看统计',
    description: '查看统计分析数据',
    allowedRoles: STATISTICS_VIEW_ROLES,
  },
  view_project_management: {
    id: 'view_project_management',
    name: '项目管理',
    description: '查看和管理项目信息、维保计划',
    allowedRoles: PROJECT_MANAGEMENT_ROLES,
  },
  view_personnel: {
    id: 'view_personnel',
    name: '人员管理',
    description: '查看和管理人员信息',
    allowedRoles: PERSONNEL_MANAGEMENT_ROLES,
  },
  view_spare_parts_stock: {
    id: 'view_spare_parts_stock',
    name: '备件库存',
    description: '查看和管理备品备件库存',
    allowedRoles: SPARE_PARTS_MANAGEMENT_ROLES,
  },
  view_spare_parts_issue: {
    id: 'view_spare_parts_issue',
    name: '备件领用',
    description: '领用备品备件',
    allowedRoles: [...SPARE_PARTS_MANAGEMENT_ROLES, RoleCode.EMPLOYEE],
  },
  view_repair_tools_stock: {
    id: 'view_repair_tools_stock',
    name: '工具库存',
    description: '查看和管理维修工具库存',
    allowedRoles: SPARE_PARTS_MANAGEMENT_ROLES,
  },
  view_repair_tools_issue: {
    id: 'view_repair_tools_issue',
    name: '工具领用',
    description: '领用维修工具',
    allowedRoles: [...SPARE_PARTS_MANAGEMENT_ROLES, RoleCode.EMPLOYEE],
  },
  view_work_order: {
    id: 'view_work_order',
    name: '工单查看',
    description: '查看工单列表和详情',
    allowedRoles: WORK_ORDER_VIEW_ROLES,
  },
  approve_periodic_inspection: {
    id: 'approve_periodic_inspection',
    name: '审批巡检单',
    description: '审批定期巡检工单',
    allowedRoles: WORK_ORDER_APPROVE_ROLES,
  },
  approve_temporary_repair: {
    id: 'approve_temporary_repair',
    name: '审批维修单',
    description: '审批临时维修工单',
    allowedRoles: WORK_ORDER_APPROVE_ROLES,
  },
  approve_spot_work: {
    id: 'approve_spot_work',
    name: '审批零星用工单',
    description: '审批零星用工工单',
    allowedRoles: WORK_ORDER_APPROVE_ROLES,
  },
  fill_maintenance_log: {
    id: 'fill_maintenance_log',
    name: '填写维保日志',
    description: '填写维保日志',
    allowedRoles: MAINTENANCE_LOG_FILL_ROLES,
  },
  view_maintenance_log: {
    id: 'view_maintenance_log',
    name: '查看维保日志',
    description: '查看维保日志',
    allowedRoles: MAINTENANCE_LOG_VIEW_ROLES,
  },
  view_all_maintenance_log: {
    id: 'view_all_maintenance_log',
    name: '查看所有维保日志',
    description: '查看所有人的维保日志',
    allowedRoles: PROJECT_MANAGEMENT_ROLES,
  },
  fill_weekly_report: {
    id: 'fill_weekly_report',
    name: '填写周报',
    description: '填写部门周报',
    allowedRoles: WEEKLY_REPORT_FILL_ROLES,
  },
  view_weekly_report: {
    id: 'view_weekly_report',
    name: '查看周报',
    description: '查看部门周报',
    allowedRoles: WEEKLY_REPORT_VIEW_ROLES,
  },
  view_alerts: {
    id: 'view_alerts',
    name: '查看提醒',
    description: '查看超期/临期提醒',
    allowedRoles: STATISTICS_VIEW_ROLES,
  },
  view_system_management: {
    id: 'view_system_management',
    name: '系统管理',
    description: '系统管理功能（客户、巡检事项等）',
    allowedRoles: PROJECT_MANAGEMENT_ROLES,
  },
  delete_personnel: {
    id: 'delete_personnel',
    name: '删除人员',
    description: '删除人员信息',
    allowedRoles: [RoleCode.ADMIN],
  },
  edit_personnel_role: {
    id: 'edit_personnel_role',
    name: '修改人员角色',
    description: '修改人员角色',
    allowedRoles: [RoleCode.ADMIN],
  },
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

export function getDefaultPath(role: string | undefined | null): string {
  if (!role) return '/login'
  for (const menuId of DEFAULT_ROUTE_ORDER) {
    if (canShowMenu(menuId, role)) {
      return `/${menuId}`
    }
  }
  return '/login'
}

export function hasPermission(role: string | undefined | null, permissionId: string): boolean {
  if (!role) return false
  const permission = PERMISSION_CONFIGS[permissionId]
  if (!permission) return false
  return permission.allowedRoles.includes(role)
}

export function canShowMenu(menuId: string, role: string | undefined | null): boolean {
  if (!role) return false
  const permissionId = MENU_PERMISSION_MAP[menuId]
  if (!permissionId) return false
  return hasPermission(role, permissionId)
}

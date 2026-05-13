/**
 * 用户角色类型定义和权限辅助函数
 */
export type UserRole = '管理员' | '部门经理' | '主管' | '材料员' | '运维人员'

export const RoleCode = {
  ADMIN: '管理员',
  DEPARTMENT_MANAGER: '部门经理',
  SUPERVISOR: '主管',
  MATERIAL_MANAGER: '材料员',
  EMPLOYEE: '运维人员',
} as const

export type RoleCodeType = (typeof RoleCode)[keyof typeof RoleCode]

export const ADMIN_ROLES: UserRole[] = ['管理员', '部门经理', '主管']

export const ALL_ROLES: UserRole[] = ['管理员', '部门经理', '主管', '运维人员', '材料员']

export const PROJECT_MANAGEMENT_ROLES: string[] = ['管理员', '部门经理']

export const PERSONNEL_MANAGEMENT_ROLES: string[] = ['管理员', '部门经理']

export const SPARE_PARTS_MANAGEMENT_ROLES: string[] = ['管理员', '部门经理', '材料员']

export const WORK_ORDER_VIEW_ROLES: string[] = ['管理员', '部门经理', '主管', '运维人员']

export const WORK_ORDER_APPROVE_ROLES: string[] = ['管理员', '部门经理']

export const STATISTICS_VIEW_ROLES: string[] = ['管理员', '部门经理', '主管', '运维人员']

export const MAINTENANCE_LOG_FILL_ROLES: string[] = ['管理员', '部门经理', '主管', '运维人员']

export const MAINTENANCE_LOG_VIEW_ROLES: string[] = ['管理员', '部门经理', '主管', '运维人员']

export const WEEKLY_REPORT_FILL_ROLES: string[] = ['管理员', '部门经理']

export const WEEKLY_REPORT_VIEW_ROLES: string[] = ['管理员', '部门经理']

export interface PermissionConfig {
  id: string
  name: string
  description: string
  allowedRoles: string[]
}

export const MANAGER_ROLES: UserRole[] = ['管理员', '部门经理', '主管']

export function isAdminRole(role: string | undefined | null): boolean {
  if (!role) return false
  return ADMIN_ROLES.includes(role as UserRole)
}

export function isManagerRole(role: string | undefined | null): boolean {
  if (!role) return false
  return MANAGER_ROLES.includes(role as UserRole)
}

export function isMaterialManager(role: string | undefined | null): boolean {
  return role === RoleCode.MATERIAL_MANAGER
}

export function canDeleteWorkOrder(role: string | undefined | null): boolean {
  if (!role) return false
  return role === RoleCode.ADMIN || role === RoleCode.DEPARTMENT_MANAGER
}

export const COMMON_PERMISSION_CONFIGS: Record<string, PermissionConfig> = {
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

export function hasPermission(role: string | undefined | null, permissionId: string, configs: Record<string, PermissionConfig> = COMMON_PERMISSION_CONFIGS): boolean {
  if (!role) return false
  const permission = configs[permissionId]
  if (!permission) return false
  return permission.allowedRoles.includes(role)
}

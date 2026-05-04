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

export const WORK_ORDER_VIEW_ROLES: string[] = ['管理员', '部门经理', '运维人员']

export const WORK_ORDER_APPROVE_ROLES: string[] = ['管理员', '部门经理']

export const STATISTICS_VIEW_ROLES: string[] = ['管理员', '部门经理', '运维人员']

export const MAINTENANCE_LOG_FILL_ROLES: string[] = ['管理员', '部门经理', '运维人员']

export const MAINTENANCE_LOG_VIEW_ROLES: string[] = ['管理员', '部门经理', '运维人员']

export const WEEKLY_REPORT_FILL_ROLES: string[] = ['管理员', '部门经理']

export const WEEKLY_REPORT_VIEW_ROLES: string[] = ['管理员', '部门经理']

export interface PermissionConfig {
  id: string
  name: string
  description: string
  allowedRoles: string[]
}

export const MANAGER_ROLES: UserRole[] = ['管理员', '部门经理']

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

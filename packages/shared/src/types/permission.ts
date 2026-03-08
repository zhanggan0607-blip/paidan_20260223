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

export const MANAGER_ROLES: UserRole[] = ['管理员', '部门经理', '主管']

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

export interface RoleConfig {
  code: string
  name: string
  level: number
  description: string
}

export const ROLE_CONFIGS: Record<string, RoleConfig> = {
  [RoleCode.ADMIN]: {
    code: RoleCode.ADMIN,
    name: '管理员',
    level: 100,
    description: '系统管理员，拥有所有权限',
  },
  [RoleCode.DEPARTMENT_MANAGER]: {
    code: RoleCode.DEPARTMENT_MANAGER,
    name: '部门经理',
    level: 70,
    description: '部门经理，可管理项目和人员',
  },
  [RoleCode.SUPERVISOR]: {
    code: RoleCode.SUPERVISOR,
    name: '主管',
    level: 60,
    description: '主管，可审批工单',
  },
  [RoleCode.MATERIAL_MANAGER]: {
    code: RoleCode.MATERIAL_MANAGER,
    name: '材料员',
    level: 50,
    description: '材料管理员，管理备品备件',
  },
  [RoleCode.EMPLOYEE]: {
    code: RoleCode.EMPLOYEE,
    name: '运维人员',
    level: 10,
    description: '普通员工，执行维保任务',
  },
}

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

export function canViewAllWorkOrders(role: string | undefined): boolean {
  return isAdminRole(role)
}

export function canManagePersonnel(role: string | undefined): boolean {
  return isAdminRole(role)
}

export function canManageProjects(role: string | undefined): boolean {
  return isAdminRole(role)
}

export function canManagePlans(role: string | undefined): boolean {
  return isAdminRole(role)
}

export function canApproveWorkOrders(role: string | undefined): boolean {
  return isAdminRole(role)
}

export function canViewStatistics(role: string | undefined): boolean {
  return isAdminRole(role)
}

export function canManageSpareParts(role: string | undefined): boolean {
  return isAdminRole(role) || role === '材料员'
}

export function canViewSpareParts(_role: string | undefined): boolean {
  return true
}

export function canViewWorkOrder(role: string | undefined | null): boolean {
  return !isMaterialManager(role)
}

export function canViewSignature(role: string | undefined | null): boolean {
  return !isMaterialManager(role)
}

export function getRoleLevel(role: string | undefined | null): number {
  if (!role) return 0
  const config = ROLE_CONFIGS[role]
  return config ? config.level : 0
}

export interface PermissionConfig {
  id: string
  name: string
  description: string
  allowedRoles: string[]
}

export function hasPermission(
  role: string | undefined | null,
  permissionId: string,
  permissionConfigs: Record<string, PermissionConfig>
): boolean {
  if (!role) return false
  const permission = permissionConfigs[permissionId]
  if (!permission) return false
  return permission.allowedRoles.includes(role)
}

export function getAllowedPermissions(
  role: string,
  permissionConfigs: Record<string, PermissionConfig>
): string[] {
  return Object.entries(permissionConfigs)
    .filter(([_, config]) => config.allowedRoles.includes(role))
    .map(([id]) => id)
}

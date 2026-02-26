/**
 * 统一权限配置模块 (H5端)
 * 集中管理所有角色、权限和菜单配置
 */

/**
 * 角色代码枚举
 */
export const RoleCode = {
  ADMIN: '管理员',
  DEPARTMENT_MANAGER: '部门经理',
  MATERIAL_MANAGER: '材料员',
  EMPLOYEE: '运维人员'
} as const

export type RoleCodeType = typeof RoleCode[keyof typeof RoleCode]

/**
 * 角色配置接口
 */
export interface RoleConfig {
  code: string
  name: string
  level: number
  description: string
}

/**
 * 角色配置映射
 */
export const ROLE_CONFIGS: Record<string, RoleConfig> = {
  [RoleCode.ADMIN]: {
    code: RoleCode.ADMIN,
    name: '管理员',
    level: 100,
    description: '系统管理员，拥有所有权限'
  },
  [RoleCode.DEPARTMENT_MANAGER]: {
    code: RoleCode.DEPARTMENT_MANAGER,
    name: '部门经理',
    level: 70,
    description: '部门经理，可管理项目和人员'
  },
  [RoleCode.MATERIAL_MANAGER]: {
    code: RoleCode.MATERIAL_MANAGER,
    name: '材料员',
    level: 50,
    description: '材料管理员，管理备品备件'
  },
  [RoleCode.EMPLOYEE]: {
    code: RoleCode.EMPLOYEE,
    name: '运维人员',
    level: 10,
    description: '普通员工，执行维保任务'
  }
}

/**
 * 所有角色列表
 */
export const ALL_ROLES: string[] = Object.keys(ROLE_CONFIGS)

/**
 * 管理层角色
 */
export const MANAGER_ROLES: string[] = [
  RoleCode.ADMIN,
  RoleCode.DEPARTMENT_MANAGER
]

/**
 * 管理员角色
 */
export const ADMIN_ROLES: string[] = [RoleCode.ADMIN]

/**
 * 项目管理角色
 */
export const PROJECT_MANAGEMENT_ROLES: string[] = [
  RoleCode.ADMIN,
  RoleCode.DEPARTMENT_MANAGER
]

/**
 * 人员管理角色
 */
export const PERSONNEL_MANAGEMENT_ROLES: string[] = [
  RoleCode.ADMIN,
  RoleCode.DEPARTMENT_MANAGER
]

/**
 * 备件管理角色
 */
export const SPARE_PARTS_MANAGEMENT_ROLES: string[] = [
  RoleCode.ADMIN,
  RoleCode.DEPARTMENT_MANAGER,
  RoleCode.MATERIAL_MANAGER
]

/**
 * 工单查看角色
 */
export const WORK_ORDER_VIEW_ROLES: string[] = [
  RoleCode.ADMIN,
  RoleCode.DEPARTMENT_MANAGER,
  RoleCode.EMPLOYEE
]

/**
 * 工单审批角色
 */
export const WORK_ORDER_APPROVE_ROLES: string[] = [
  RoleCode.ADMIN,
  RoleCode.DEPARTMENT_MANAGER
]

/**
 * 统计查看角色
 */
export const STATISTICS_VIEW_ROLES: string[] = [
  RoleCode.ADMIN,
  RoleCode.DEPARTMENT_MANAGER,
  RoleCode.EMPLOYEE
]

/**
 * 维保日志填写角色
 */
export const MAINTENANCE_LOG_FILL_ROLES: string[] = [
  RoleCode.ADMIN,
  RoleCode.DEPARTMENT_MANAGER,
  RoleCode.EMPLOYEE
]

/**
 * 维保日志查看角色
 */
export const MAINTENANCE_LOG_VIEW_ROLES: string[] = [
  RoleCode.ADMIN,
  RoleCode.DEPARTMENT_MANAGER,
  RoleCode.EMPLOYEE
]

/**
 * 周报填写角色
 */
export const WEEKLY_REPORT_FILL_ROLES: string[] = [
  RoleCode.ADMIN,
  RoleCode.DEPARTMENT_MANAGER
]

/**
 * 周报查看角色
 */
export const WEEKLY_REPORT_VIEW_ROLES: string[] = [
  RoleCode.ADMIN,
  RoleCode.DEPARTMENT_MANAGER
]

/**
 * 权限配置接口
 */
export interface PermissionConfig {
  id: string
  name: string
  description: string
  allowedRoles: string[]
}

/**
 * 权限配置映射
 */
export const PERMISSION_CONFIGS: Record<string, PermissionConfig> = {
  view_statistics: {
    id: 'view_statistics',
    name: '查看统计',
    description: '查看统计分析数据',
    allowedRoles: STATISTICS_VIEW_ROLES
  },
  view_project_management: {
    id: 'view_project_management',
    name: '项目管理',
    description: '查看和管理项目信息、维保计划',
    allowedRoles: PROJECT_MANAGEMENT_ROLES
  },
  manage_personnel: {
    id: 'manage_personnel',
    name: '人员管理',
    description: '管理项目人员',
    allowedRoles: PERSONNEL_MANAGEMENT_ROLES
  },
  manage_projects: {
    id: 'manage_projects',
    name: '项目管理',
    description: '管理项目信息',
    allowedRoles: PROJECT_MANAGEMENT_ROLES
  },
  manage_spare_parts: {
    id: 'manage_spare_parts',
    name: '备件管理',
    description: '管理备品备件',
    allowedRoles: SPARE_PARTS_MANAGEMENT_ROLES
  },
  view_all_work_orders: {
    id: 'view_all_work_orders',
    name: '查看所有工单',
    description: '查看所有人的工单',
    allowedRoles: PROJECT_MANAGEMENT_ROLES
  },
  view_personnel: {
    id: 'view_personnel',
    name: '查看人员',
    description: '查看人员列表',
    allowedRoles: PERSONNEL_MANAGEMENT_ROLES
  },
  view_spare_parts_inventory: {
    id: 'view_spare_parts_inventory',
    name: '备件库存',
    description: '查看备品备件库存',
    allowedRoles: SPARE_PARTS_MANAGEMENT_ROLES
  },
  view_spare_parts_stock: {
    id: 'view_spare_parts_stock',
    name: '备件库存',
    description: '查看备品备件库存',
    allowedRoles: SPARE_PARTS_MANAGEMENT_ROLES
  },
  view_spare_parts_issue: {
    id: 'view_spare_parts_issue',
    name: '备件领用',
    description: '领用备品备件',
    allowedRoles: [...SPARE_PARTS_MANAGEMENT_ROLES, RoleCode.EMPLOYEE]
  },
  view_repair_tools_stock: {
    id: 'view_repair_tools_stock',
    name: '工具库存',
    description: '查看维修工具库存',
    allowedRoles: SPARE_PARTS_MANAGEMENT_ROLES
  },
  view_repair_tools_inbound: {
    id: 'view_repair_tools_inbound',
    name: '工具入库',
    description: '维修工具入库',
    allowedRoles: SPARE_PARTS_MANAGEMENT_ROLES
  },
  view_repair_tools_issue: {
    id: 'view_repair_tools_issue',
    name: '工具领用',
    description: '领用维修工具',
    allowedRoles: [...SPARE_PARTS_MANAGEMENT_ROLES, RoleCode.EMPLOYEE]
  },
  view_alerts: {
    id: 'view_alerts',
    name: '查看提醒',
    description: '查看超期/临期提醒',
    allowedRoles: STATISTICS_VIEW_ROLES
  },
  view_system_management: {
    id: 'view_system_management',
    name: '系统管理',
    description: '系统管理功能',
    allowedRoles: PROJECT_MANAGEMENT_ROLES
  },
  view_periodic_inspection: {
    id: 'view_periodic_inspection',
    name: '巡检单',
    description: '查看定期巡检单',
    allowedRoles: WORK_ORDER_VIEW_ROLES
  },
  approve_periodic_inspection: {
    id: 'approve_periodic_inspection',
    name: '审批巡检单',
    description: '审批定期巡检工单',
    allowedRoles: WORK_ORDER_APPROVE_ROLES
  },
  approve_temporary_repair: {
    id: 'approve_temporary_repair',
    name: '审批维修单',
    description: '审批临时维修工单',
    allowedRoles: WORK_ORDER_APPROVE_ROLES
  },
  approve_spot_work: {
    id: 'approve_spot_work',
    name: '审批零星用工单',
    description: '审批零星用工工单',
    allowedRoles: WORK_ORDER_APPROVE_ROLES
  },
  view_temporary_repair: {
    id: 'view_temporary_repair',
    name: '维修单',
    description: '查看临时维修单',
    allowedRoles: WORK_ORDER_VIEW_ROLES
  },
  view_spot_work: {
    id: 'view_spot_work',
    name: '零星用工单',
    description: '查看零星用工单',
    allowedRoles: WORK_ORDER_VIEW_ROLES
  },
  apply_spot_work: {
    id: 'apply_spot_work',
    name: '申请零星用工',
    description: '申请零星用工',
    allowedRoles: WORK_ORDER_VIEW_ROLES
  },
  view_project_info: {
    id: 'view_project_info',
    name: '项目信息',
    description: '查看项目信息',
    allowedRoles: ALL_ROLES
  },
  quick_fill_spot_work: {
    id: 'quick_fill_spot_work',
    name: '快速填写零星用工',
    description: '快速填写零星用工单',
    allowedRoles: WORK_ORDER_VIEW_ROLES
  },
  view_maintenance_log: {
    id: 'view_maintenance_log',
    name: '查看维保日志',
    description: '查看维保日志',
    allowedRoles: MAINTENANCE_LOG_VIEW_ROLES
  },
  view_maintenance_log_detail: {
    id: 'view_maintenance_log_detail',
    name: '查看日志详情',
    description: '查看维保日志详情',
    allowedRoles: MAINTENANCE_LOG_VIEW_ROLES
  },
  fill_maintenance_log: {
    id: 'fill_maintenance_log',
    name: '填写维保日志',
    description: '填写维保日志',
    allowedRoles: MAINTENANCE_LOG_FILL_ROLES
  },
  view_all_maintenance_log: {
    id: 'view_all_maintenance_log',
    name: '查看所有日志',
    description: '查看所有人的维保日志',
    allowedRoles: PROJECT_MANAGEMENT_ROLES
  },
  view_department_weekly_report: {
    id: 'view_department_weekly_report',
    name: '部门周报',
    description: '查看部门周报',
    allowedRoles: [RoleCode.ADMIN, RoleCode.DEPARTMENT_MANAGER, RoleCode.EMPLOYEE]
  },
  view_all_weekly_report: {
    id: 'view_all_weekly_report',
    name: '查看所有周报',
    description: '查看所有部门周报',
    allowedRoles: WEEKLY_REPORT_VIEW_ROLES
  },
  approve_weekly_report: {
    id: 'approve_weekly_report',
    name: '审批周报',
    description: '审批部门周报',
    allowedRoles: WEEKLY_REPORT_VIEW_ROLES
  },
  view_work_list: {
    id: 'view_work_list',
    name: '工作列表',
    description: '查看工作列表',
    allowedRoles: WORK_ORDER_VIEW_ROLES
  },
  view_signature: {
    id: 'view_signature',
    name: '签名功能',
    description: '使用签名功能',
    allowedRoles: WORK_ORDER_VIEW_ROLES
  },
  create_temporary_repair: {
    id: 'create_temporary_repair',
    name: '创建维修单',
    description: '创建临时维修单',
    allowedRoles: [RoleCode.ADMIN, RoleCode.DEPARTMENT_MANAGER, RoleCode.EMPLOYEE]
  },
  fill_weekly_report: {
    id: 'fill_weekly_report',
    name: '填写周报',
    description: '填写部门周报',
    allowedRoles: WEEKLY_REPORT_FILL_ROLES
  }
}

/**
 * 检查角色是否有指定权限
 * @param role 用户角色
 * @param permissionId 权限ID
 * @returns 是否有权限
 */
export function hasPermission(role: string | undefined | null, permissionId: string): boolean {
  if (!role) return false
  
  const permission = PERMISSION_CONFIGS[permissionId]
  if (!permission) return false
  
  return permission.allowedRoles.includes(role)
}

/**
 * 获取角色的所有权限
 * @param role 用户角色
 * @returns 权限ID列表
 */
export function getAllowedPermissions(role: string): string[] {
  return Object.entries(PERMISSION_CONFIGS)
    .filter(([_, config]) => config.allowedRoles.includes(role))
    .map(([id]) => id)
}

/**
 * 检查是否为管理层角色
 * @param role 用户角色
 * @returns 是否为管理层
 */
export function isManagerRole(role: string | undefined | null): boolean {
  if (!role) return false
  return MANAGER_ROLES.includes(role)
}

/**
 * 检查是否为管理员角色
 * @param role 用户角色
 * @returns 是否为管理员
 */
export function isAdminRole(role: string | undefined | null): boolean {
  if (!role) return false
  return ADMIN_ROLES.includes(role)
}

/**
 * 获取角色级别
 * @param role 用户角色
 * @returns 角色级别，级别越高权限越大
 */
export function getRoleLevel(role: string | undefined | null): number {
  if (!role) return 0
  const config = ROLE_CONFIGS[role]
  return config ? config.level : 0
}

/**
 * 检查是否为材料员（H5端特殊逻辑）
 * @param role 用户角色
 * @returns 是否为材料员
 */
export function isMaterialManager(role: string | undefined | null): boolean {
  return role === RoleCode.MATERIAL_MANAGER
}

/**
 * 检查是否可以查看工单（排除材料员）
 * @param role 用户角色
 * @returns 是否可以查看工单
 */
export function canViewWorkOrder(role: string | undefined | null): boolean {
  return !isMaterialManager(role)
}

/**
 * 检查是否可以查看签名功能（排除材料员）
 * @param role 用户角色
 * @returns 是否可以查看签名
 */
export function canViewSignature(role: string | undefined | null): boolean {
  return !isMaterialManager(role)
}

/**
 * 统一权限配置模块 (H5端)
 * 从共享包导入基础权限配置，保留H5端特有的权限配置
 */

// 类型导出（编译时擦除，需要使用 export type）
export type { UserRole, RoleCodeType, PermissionConfig } from '@sstcp/shared'

// 值导出（运行时存在的常量和函数）
export {
  RoleCode,
  ADMIN_ROLES,
  ALL_ROLES,
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
  isMaterialManager,
} from '@sstcp/shared'

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
  MAINTENANCE_LOG_VIEW_ROLES,
  WEEKLY_REPORT_VIEW_ROLES,
  WEEKLY_REPORT_FILL_ROLES,
  MAINTENANCE_LOG_FILL_ROLES,
  ALL_ROLES,
  hasPermission as sharedHasPermission,
} from '@sstcp/shared'

export const PERMISSION_CONFIGS: Record<string, PermissionConfig> = {
  ...COMMON_PERMISSION_CONFIGS,
  manage_personnel: {
    id: 'manage_personnel',
    name: '人员管理',
    description: '管理项目人员',
    allowedRoles: PERSONNEL_MANAGEMENT_ROLES,
  },
  manage_projects: {
    id: 'manage_projects',
    name: '项目管理',
    description: '管理项目信息',
    allowedRoles: PROJECT_MANAGEMENT_ROLES,
  },
  manage_spare_parts: {
    id: 'manage_spare_parts',
    name: '备件管理',
    description: '管理备品备件',
    allowedRoles: SPARE_PARTS_MANAGEMENT_ROLES,
  },
  view_all_work_orders: {
    id: 'view_all_work_orders',
    name: '查看所有工单',
    description: '查看所有人的工单',
    allowedRoles: PROJECT_MANAGEMENT_ROLES,
  },
  view_spare_parts_inventory: {
    id: 'view_spare_parts_inventory',
    name: '备件库存',
    description: '查看备品备件库存',
    allowedRoles: SPARE_PARTS_MANAGEMENT_ROLES,
  },
  view_repair_tools_inbound: {
    id: 'view_repair_tools_inbound',
    name: '工具入库',
    description: '维修工具入库',
    allowedRoles: SPARE_PARTS_MANAGEMENT_ROLES,
  },
  view_periodic_inspection: {
    id: 'view_periodic_inspection',
    name: '巡检单',
    description: '查看定期巡检单',
    allowedRoles: WORK_ORDER_VIEW_ROLES,
  },
  view_temporary_repair: {
    id: 'view_temporary_repair',
    name: '维修单',
    description: '查看临时维修单',
    allowedRoles: WORK_ORDER_VIEW_ROLES,
  },
  view_spot_work: {
    id: 'view_spot_work',
    name: '零星用工单',
    description: '查看零星用工单',
    allowedRoles: WORK_ORDER_VIEW_ROLES,
  },
  apply_spot_work: {
    id: 'apply_spot_work',
    name: '申请零星用工',
    description: '申请零星用工',
    allowedRoles: WORK_ORDER_VIEW_ROLES,
  },
  view_project_info: {
    id: 'view_project_info',
    name: '项目信息',
    description: '查看项目信息',
    allowedRoles: ALL_ROLES,
  },
  quick_fill_spot_work: {
    id: 'quick_fill_spot_work',
    name: '快速填写零星用工',
    description: '快速填写零星用工单',
    allowedRoles: WORK_ORDER_VIEW_ROLES,
  },
  view_maintenance_log_detail: {
    id: 'view_maintenance_log_detail',
    name: '查看日志详情',
    description: '查看维保日志详情',
    allowedRoles: MAINTENANCE_LOG_VIEW_ROLES,
  },
  view_department_weekly_report: {
    id: 'view_department_weekly_report',
    name: '部门周报',
    description: '查看部门周报',
    allowedRoles: [RoleCode.ADMIN, RoleCode.DEPARTMENT_MANAGER, RoleCode.EMPLOYEE],
  },
  view_all_weekly_report: {
    id: 'view_all_weekly_report',
    name: '查看所有周报',
    description: '查看所有部门周报',
    allowedRoles: WEEKLY_REPORT_VIEW_ROLES,
  },
  approve_weekly_report: {
    id: 'approve_weekly_report',
    name: '审批周报',
    description: '审批部门周报',
    allowedRoles: WEEKLY_REPORT_VIEW_ROLES,
  },
  view_work_list: {
    id: 'view_work_list',
    name: '工作列表',
    description: '查看工作列表',
    allowedRoles: WORK_ORDER_VIEW_ROLES,
  },
  view_signature: {
    id: 'view_signature',
    name: '签名功能',
    description: '使用签名功能',
    allowedRoles: WORK_ORDER_VIEW_ROLES,
  },
  create_temporary_repair: {
    id: 'create_temporary_repair',
    name: '创建维修单',
    description: '创建临时维修单',
    allowedRoles: [RoleCode.ADMIN, RoleCode.DEPARTMENT_MANAGER, RoleCode.EMPLOYEE],
  },
}

export function hasPermission(role: string | undefined | null, permissionId: string): boolean {
  return sharedHasPermission(role, permissionId, PERMISSION_CONFIGS)
}

export function getAllowedPermissions(role: string): string[] {
  return Object.entries(PERMISSION_CONFIGS)
    .filter(([_, config]) => config.allowedRoles.includes(role))
    .map(([id]) => id)
}

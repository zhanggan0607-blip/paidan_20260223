/**
 * 共享常量定义
 * 统一管理 PC 端和 H5 端的常量配置
 */

/**
 * API 配置
 */
export const API_CONFIG = {
  get BASE_URL(): string {
    if (typeof import.meta !== 'undefined' && import.meta.env?.PROD) {
      return '/api/v1'
    }
    if (typeof import.meta !== 'undefined' && import.meta.env?.VITE_API_BASE_URL) {
      return import.meta.env.VITE_API_BASE_URL
    }
    return '/api/v1'
  },
  TIMEOUT: 60000,
}

/**
 * 权限定义
 */
export const PERMISSIONS = {
  VIEW_WORK_ORDER: 'view_work_order',
  CREATE_WORK_ORDER: 'create_work_order',
  EDIT_WORK_ORDER: 'edit_work_order',
  DELETE_WORK_ORDER: 'delete_work_order',
  
  VIEW_PLAN: 'view_plan',
  CREATE_PLAN: 'create_plan',
  EDIT_PLAN: 'edit_plan',
  DELETE_PLAN: 'delete_plan',
  
  VIEW_PERSONNEL: 'view_personnel',
  MANAGE_PERSONNEL: 'manage_personnel',
  
  VIEW_SPARE_PARTS: 'view_spare_parts',
  MANAGE_SPARE_PARTS: 'manage_spare_parts',
  
  ADMIN_SETTINGS: 'admin_settings',
  VIEW_STATISTICS: 'view_statistics',
} as const

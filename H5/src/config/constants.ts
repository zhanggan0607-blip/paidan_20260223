/**
 * H5端常量配置
 * 从shared包导入共享的常量定义，保留H5端特有的配置
 */

// 从shared包导入共享常量
export {
  PLAN_TYPES,
  PLAN_TYPE_LIST,
  WORK_STATUS,
  WORK_STATUS_LIST,
  USER_ROLES,
  USER_ROLE_LIST,
  GENDER_OPTIONS,
  GENDER_LIST,
  DATE_FORMAT,
  STATUS_IN_PROGRESS,
  STATUS_PENDING_CONFIRM,
  STATUS_COMPLETED,
  STATUS_REJECTED,
  ALL_STATUSES,
  getStatusType,
  getStatusColor,
  getStatusClass,
  getDisplayStatus,
  isCompletedStatus,
  isInProgressStatus,
  isPendingConfirmStatus,
  isRejectedStatus,
  isPendingStatus,
  BASE_WORK_TABS,
  APPROVAL_TAB
} from '@sstcp/shared'

export {
  formatDate,
  formatDateTime,
  formatDateForInput
} from '@sstcp/shared'

/**
 * H5端API配置
 * 支持开发和生产环境的不同配置
 */
export const API_CONFIG = {
  get BASE_URL() {
    if (import.meta.env.PROD) {
      return '/api/v1'
    }
    return import.meta.env.VITE_API_BASE_URL || '/api/v1'
  },
  TIMEOUT: 60000
}

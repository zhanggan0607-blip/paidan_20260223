/**
 * PC端常量配置
 * 从shared包导入共享的常量定义
 */
export {
  API_CONFIG,
  PLAN_TYPES,
  PLAN_TYPE_LIST,
  WORK_STATUS,
  WORK_STATUS_LIST,
  EXECUTION_STATUS,
  SPARE_PARTS_STATUS,
  SPARE_PARTS_STATUS_LIST,
  REPAIR_TOOLS_STATUS,
  REPAIR_TOOLS_STATUS_LIST,
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

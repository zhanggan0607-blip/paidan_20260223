export const API_CONFIG = {
  get BASE_URL() {
    return import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1'
  },
  TIMEOUT: 60000
}

export const PLAN_TYPES = {
  PERIODIC_INSPECTION: '定期巡检',
  TEMPORARY_REPAIR: '临时维修',
  SPOT_WORK: '零星用工',
  PERIODIC_MAINTENANCE: '定期维保'
} as const

export const PLAN_TYPE_LIST = [
  PLAN_TYPES.PERIODIC_INSPECTION,
  PLAN_TYPES.TEMPORARY_REPAIR,
  PLAN_TYPES.SPOT_WORK
] as const

export const WORK_STATUS = {
  NOT_STARTED: '待执行',
  PENDING_CONFIRM: '待确认',
  CONFIRMED: '已确认',
  IN_PROGRESS: '执行中',
  COMPLETED: '已完成',
  CANCELLED: '已取消',
  RETURNED: '已退回'
} as const

export const WORK_STATUS_LIST = [
  WORK_STATUS.NOT_STARTED,
  WORK_STATUS.PENDING_CONFIRM,
  WORK_STATUS.CONFIRMED,
  WORK_STATUS.IN_PROGRESS,
  WORK_STATUS.COMPLETED,
  WORK_STATUS.CANCELLED
] as const

export const MAINTENANCE_STATUS = {
  PENDING: '待执行',
  IN_PROGRESS: '执行中',
  COMPLETED: '已完成',
  CANCELLED: '已取消',
  DELAYED: '已延期'
} as const

export const EXECUTION_STATUS = {
  NOT_STARTED: '未开始',
  IN_PROGRESS: '待确认',
  COMPLETED: '已完成',
  CANCELLED: '已取消',
  ABNORMAL: '异常'
} as const

export const USER_ROLES = {
  ADMIN: '管理员',
  DEPARTMENT_MANAGER: '部门经理',
  MATERIAL_MANAGER: '材料员',
  EMPLOYEE: '运维人员'
} as const

export const USER_ROLE_LIST = [
  USER_ROLES.ADMIN,
  USER_ROLES.DEPARTMENT_MANAGER,
  USER_ROLES.MATERIAL_MANAGER,
  USER_ROLES.EMPLOYEE
] as const

export const GENDER_OPTIONS = {
  MALE: '男',
  FEMALE: '女',
  OTHER: '其他'
} as const

export const GENDER_LIST = [
  GENDER_OPTIONS.MALE,
  GENDER_OPTIONS.FEMALE,
  GENDER_OPTIONS.OTHER
] as const

export const DATE_FORMAT = 'YYYY-MM-DD'

export const formatDate = (dateStr: string | Date | null | undefined): string => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  if (isNaN(date.getTime())) return '-'
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

export const formatDateTime = (dateStr: string | Date | null | undefined): string => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  if (isNaN(date.getTime())) return '-'
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  return `${year}-${month}-${day} ${hours}:${minutes}`
}

export const formatDateForInput = (dateStr: string | Date | null | undefined): string => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  if (isNaN(date.getTime())) return ''
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

export const API_CONFIG = {
  get BASE_URL() {
    return import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080/api/v1'
  },
  TIMEOUT: 60000
}

export const PLAN_TYPES = {
  PERIODIC_INSPECTION: '定期巡检',
  TEMPORARY_REPAIR: '临时维修',
  SPOT_WORK: '零星用工',
  PERIODIC_MAINTENANCE: '定期维保'
} as const

export const WORK_STATUS = {
  NOT_STARTED: '待执行',
  PENDING_CONFIRM: '待确认',
  CONFIRMED: '已确认',
  IN_PROGRESS: '执行中',
  COMPLETED: '已完成',
  CANCELLED: '已取消',
  RETURNED: '已退回'
} as const

export const USER_ROLES = {
  ADMIN: '管理员',
  DEPARTMENT_MANAGER: '部门经理',
  MATERIAL_MANAGER: '材料员',
  EMPLOYEE: '员工'
} as const

export const formatDate = (dateStr: string | Date | null | undefined): string => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  if (isNaN(date.getTime())) return '-'
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

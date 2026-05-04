export const STATUS_IN_PROGRESS = '执行中'
export const STATUS_PENDING_CONFIRM = '待确认'
export const STATUS_COMPLETED = '已完成'
export const STATUS_REJECTED = '已退回'

export const ALL_STATUSES = [STATUS_IN_PROGRESS, STATUS_PENDING_CONFIRM, STATUS_COMPLETED, STATUS_REJECTED]

export const WORK_STATUS = {
  IN_PROGRESS: STATUS_IN_PROGRESS,
  PENDING_CONFIRM: STATUS_PENDING_CONFIRM,
  COMPLETED: STATUS_COMPLETED,
  RETURNED: STATUS_REJECTED
} as const

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

export const USER_ROLES = {
  ADMIN: '管理员',
  DEPARTMENT_MANAGER: '部门经理',
  MATERIAL_MANAGER: '材料员',
  EMPLOYEE: '运维人员'
} as const

export const getStatusType = (status: string): 'success' | 'danger' | 'warning' | 'default' | 'primary' => {
  switch (status) {
    case STATUS_IN_PROGRESS:
      return 'primary'
    case STATUS_PENDING_CONFIRM:
      return 'warning'
    case STATUS_COMPLETED:
      return 'success'
    case STATUS_REJECTED:
      return 'default'
    default:
      return 'default'
  }
}

export const getDisplayStatus = (status: string): string => {
  if (ALL_STATUSES.includes(status)) {
    return status
  }
  return status
}

export const BASE_WORK_TABS = [
  { key: STATUS_IN_PROGRESS, title: STATUS_IN_PROGRESS, statuses: [STATUS_IN_PROGRESS, STATUS_REJECTED], color: '#00bcd4' },
  { key: STATUS_PENDING_CONFIRM, title: STATUS_PENDING_CONFIRM, statuses: [STATUS_PENDING_CONFIRM], color: '#ff976a' },
  { key: STATUS_COMPLETED, title: STATUS_COMPLETED, statuses: [STATUS_COMPLETED], color: '#07c160' }
]

export const APPROVAL_TAB = { key: '审批', title: '审批', statuses: [STATUS_PENDING_CONFIRM], color: '#1989fa' }

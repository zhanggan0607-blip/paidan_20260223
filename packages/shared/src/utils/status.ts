/**
 * 状态相关常量和工具函数
 * 统一管理状态类型判断和显示文本转换
 * 适用于PC端和H5端
 */

/** 执行中状态 */
export const STATUS_IN_PROGRESS = '执行中'

/** 待确认状态 */
export const STATUS_PENDING_CONFIRM = '待确认'

/** 已完成状态 */
export const STATUS_COMPLETED = '已完成'

/** 已退回状态 */
export const STATUS_REJECTED = '已退回'

/** 所有有效状态 */
export const ALL_STATUSES = [STATUS_IN_PROGRESS, STATUS_PENDING_CONFIRM, STATUS_COMPLETED, STATUS_REJECTED]

/**
 * 工单状态
 */
export const WORK_STATUS = {
  IN_PROGRESS: STATUS_IN_PROGRESS,
  PENDING_CONFIRM: STATUS_PENDING_CONFIRM,
  COMPLETED: STATUS_COMPLETED,
  RETURNED: STATUS_REJECTED
} as const

export const WORK_STATUS_LIST = [
  WORK_STATUS.IN_PROGRESS,
  WORK_STATUS.PENDING_CONFIRM,
  WORK_STATUS.COMPLETED,
  WORK_STATUS.RETURNED
] as const

/**
 * 执行状态
 */
export const EXECUTION_STATUS = {
  IN_PROGRESS: '执行中',
  COMPLETED: '已完成',
  CANCELLED: '已取消',
  ABNORMAL: '异常'
} as const

/**
 * 计划类型
 */
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

/**
 * 备件状态
 */
export const SPARE_PARTS_STATUS = {
  IN_STOCK: '在库',
  USED: '已使用',
  OUT_OF_STOCK: '缺货'
} as const

export const SPARE_PARTS_STATUS_LIST = [
  SPARE_PARTS_STATUS.IN_STOCK,
  SPARE_PARTS_STATUS.USED,
  SPARE_PARTS_STATUS.OUT_OF_STOCK
] as const

/**
 * 维修工具状态
 */
export const REPAIR_TOOLS_STATUS = {
  RETURNED: '已归还',
  ISSUED: '已领用',
  DAMAGED: '已损坏'
} as const

export const REPAIR_TOOLS_STATUS_LIST = [
  REPAIR_TOOLS_STATUS.RETURNED,
  REPAIR_TOOLS_STATUS.ISSUED,
  REPAIR_TOOLS_STATUS.DAMAGED
] as const

/**
 * 用户角色
 */
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

/**
 * 性别选项
 */
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

/**
 * 日期格式
 */
export const DATE_FORMAT = 'YYYY-MM-DD'

/**
 * API配置
 */
export const API_CONFIG = {
  get BASE_URL() {
    return '/api/v1'
  },
  TIMEOUT: 60000
}

/**
 * 获取状态对应的标签类型（用于Vant组件）
 * @param status 状态字符串
 * @returns Vant Tag 组件的 type 值
 */
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

/**
 * 获取状态对应的自定义颜色
 * @param status 状态字符串
 * @returns CSS 颜色值
 */
export const getStatusColor = (status: string): string => {
  switch (status) {
    case STATUS_IN_PROGRESS:
      return '#00bcd4'
    case STATUS_PENDING_CONFIRM:
      return '#ff976a'
    case STATUS_COMPLETED:
      return '#07c160'
    case STATUS_REJECTED:
      return '#969799'
    default:
      return '#969799'
  }
}

/**
 * 获取状态对应的CSS类名（用于PC端Element Plus）
 * @param status 状态字符串
 * @returns CSS类名
 */
export const getStatusClass = (status: string): string => {
  switch (status) {
    case STATUS_IN_PROGRESS:
      return 'status-in-progress'
    case STATUS_PENDING_CONFIRM:
      return 'status-waiting'
    case STATUS_COMPLETED:
      return 'status-completed'
    case STATUS_REJECTED:
      return 'status-returned'
    default:
      return ''
  }
}

/**
 * 获取状态的显示文本
 * @param status 状态字符串
 * @returns 用于显示的状态文本
 */
export const getDisplayStatus = (status: string): string => {
  if (ALL_STATUSES.includes(status)) {
    return status
  }
  return status
}

/**
 * 判断状态是否为完成状态
 * @param status 状态字符串
 * @returns 是否为完成状态
 */
export const isCompletedStatus = (status: string): boolean => {
  return status === STATUS_COMPLETED
}

/**
 * 判断状态是否为执行中状态
 * @param status 状态字符串
 * @returns 是否为执行中状态
 */
export const isInProgressStatus = (status: string): boolean => {
  return status === STATUS_IN_PROGRESS
}

/**
 * 判断状态是否为待确认状态
 * @param status 状态字符串
 * @returns 是否为待确认状态
 */
export const isPendingConfirmStatus = (status: string): boolean => {
  return status === STATUS_PENDING_CONFIRM
}

/**
 * 判断状态是否为已退回状态
 * @param status 状态字符串
 * @returns 是否为已退回状态
 */
export const isRejectedStatus = (status: string): boolean => {
  return status === STATUS_REJECTED
}

/**
 * 判断状态是否为待处理状态（包含执行中和已退回）
 * @param status 状态字符串
 * @returns 是否为待处理状态
 */
export const isPendingStatus = (status: string): boolean => {
  return status === STATUS_IN_PROGRESS || status === STATUS_REJECTED
}

/**
 * 工单列表页面的基础 Tabs 配置
 */
export const BASE_WORK_TABS = [
  { key: STATUS_IN_PROGRESS, title: STATUS_IN_PROGRESS, statuses: [STATUS_IN_PROGRESS, STATUS_REJECTED], color: '#00bcd4' },
  { key: STATUS_PENDING_CONFIRM, title: STATUS_PENDING_CONFIRM, statuses: [STATUS_PENDING_CONFIRM], color: '#ff976a' },
  { key: STATUS_COMPLETED, title: STATUS_COMPLETED, statuses: [STATUS_COMPLETED], color: '#07c160' }
]

/**
 * 审批 Tab 配置
 */
export const APPROVAL_TAB = { key: '审批', title: '审批', statuses: [STATUS_PENDING_CONFIRM], color: '#1989fa' }

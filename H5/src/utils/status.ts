/**
 * 状态相关工具函数
 * 统一管理状态类型判断和显示文本转换
 */

/**
 * 状态分组定义
 * - 未下发、待执行 → 未进行（红色）
 * - 执行中（青色）
 * - 待审批、待确认 → 待确认（橙色）
 * - 已确认、已审批 → 已完成（绿色）
 * - 已退回（灰色）
 */

/** 未进行状态组 */
export const NOT_STARTED_STATUSES = ['未下发', '待执行', '未进行']

/** 执行中状态组 */
export const IN_PROGRESS_STATUSES = ['执行中']

/** 待确认状态组 */
export const PENDING_CONFIRM_STATUSES = ['待审批', '待确认']

/** 已完成状态组 */
export const COMPLETED_STATUSES = ['已确认', '已审批', '已完成']

/** 已退回状态组 */
export const REJECTED_STATUSES = ['已退回']

/**
 * 获取状态对应的标签类型
 * @param status 状态字符串
 * @returns Vant Tag 组件的 type 值
 */
export const getStatusType = (status: string): 'success' | 'danger' | 'warning' | 'default' | 'primary' => {
  if (NOT_STARTED_STATUSES.includes(status)) {
    return 'danger'
  }
  if (IN_PROGRESS_STATUSES.includes(status)) {
    return 'primary'
  }
  if (PENDING_CONFIRM_STATUSES.includes(status)) {
    return 'warning'
  }
  if (COMPLETED_STATUSES.includes(status)) {
    return 'success'
  }
  if (REJECTED_STATUSES.includes(status)) {
    return 'default'
  }
  return 'default'
}

/**
 * 获取状态对应的自定义颜色
 * @param status 状态字符串
 * @returns CSS 颜色值
 */
export const getStatusColor = (status: string): string => {
  if (NOT_STARTED_STATUSES.includes(status)) {
    return '#ee0a24'
  }
  if (IN_PROGRESS_STATUSES.includes(status)) {
    return '#00bcd4'
  }
  if (PENDING_CONFIRM_STATUSES.includes(status)) {
    return '#ff976a'
  }
  if (COMPLETED_STATUSES.includes(status)) {
    return '#07c160'
  }
  if (REJECTED_STATUSES.includes(status)) {
    return '#969799'
  }
  return '#969799'
}

/**
 * 获取状态的显示文本
 * @param status 状态字符串
 * @returns 用于显示的状态文本
 */
export const getDisplayStatus = (status: string): string => {
  if (NOT_STARTED_STATUSES.includes(status)) {
    return '未进行'
  }
  if (IN_PROGRESS_STATUSES.includes(status)) {
    return '执行中'
  }
  if (PENDING_CONFIRM_STATUSES.includes(status)) {
    return '待确认'
  }
  if (COMPLETED_STATUSES.includes(status)) {
    return '已完成'
  }
  if (REJECTED_STATUSES.includes(status)) {
    return '已退回'
  }
  return status
}

/**
 * 判断状态是否为完成状态
 * @param status 状态字符串
 * @returns 是否为完成状态
 */
export const isCompletedStatus = (status: string): boolean => {
  return COMPLETED_STATUSES.includes(status)
}

/**
 * 判断状态是否为未进行状态
 * @param status 状态字符串
 * @returns 是否为未进行状态
 */
export const isNotStartedStatus = (status: string): boolean => {
  return NOT_STARTED_STATUSES.includes(status)
}

/**
 * 判断状态是否为执行中状态
 * @param status 状态字符串
 * @returns 是否为执行中状态
 */
export const isInProgressStatus = (status: string): boolean => {
  return IN_PROGRESS_STATUSES.includes(status)
}

/**
 * 判断状态是否为待确认状态
 * @param status 状态字符串
 * @returns 是否为待确认状态
 */
export const isPendingConfirmStatus = (status: string): boolean => {
  return PENDING_CONFIRM_STATUSES.includes(status)
}

/**
 * 判断状态是否为已退回状态
 * @param status 状态字符串
 * @returns 是否为已退回状态
 */
export const isRejectedStatus = (status: string): boolean => {
  return REJECTED_STATUSES.includes(status)
}

/**
 * 判断状态是否为待处理状态（包含未进行和已退回）
 * @param status 状态字符串
 * @returns 是否为待处理状态
 */
export const isPendingStatus = (status: string): boolean => {
  return NOT_STARTED_STATUSES.includes(status) || REJECTED_STATUSES.includes(status)
}

/**
 * 判断状态是否为待确认状态（兼容旧接口）
 * @param status 状态字符串
 * @returns 是否为待确认状态
 */
export const isConfirmingStatus = (status: string): boolean => {
  return PENDING_CONFIRM_STATUSES.includes(status)
}

/**
 * 工单列表页面的基础 Tabs 配置
 */
export const BASE_WORK_TABS = [
  { key: '未进行', title: '未进行', statuses: [...NOT_STARTED_STATUSES, ...REJECTED_STATUSES] as string[], color: '#ee0a24' },
  { key: '执行中', title: '执行中', statuses: [...IN_PROGRESS_STATUSES] as string[], color: '#00bcd4' },
  { key: '待确认', title: '待确认', statuses: [...PENDING_CONFIRM_STATUSES] as string[], color: '#ff976a' },
  { key: '已完成', title: '已完成', statuses: [...COMPLETED_STATUSES] as string[], color: '#07c160' }
]

/**
 * 审批 Tab 配置
 */
export const APPROVAL_TAB = { key: '审批', title: '审批', statuses: [...PENDING_CONFIRM_STATUSES] as string[], color: '#1989fa' }

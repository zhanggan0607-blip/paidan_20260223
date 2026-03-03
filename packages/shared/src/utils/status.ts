/**
 * 状态相关工具函数
 * 统一管理状态类型判断和显示文本转换
 * 适用于PC端和H5端
 */

/**
 * 状态定义
 * 系统只使用4种状态：
 * - 执行中（青色）
 * - 待确认（橙色）
 * - 已完成（绿色）
 * - 已退回（灰色）
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

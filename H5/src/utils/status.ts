/**
 * 状态相关工具函数
 * 统一管理状态类型判断和显示文本转换
 */

/**
 * 获取状态对应的标签类型
 * @param status 状态字符串
 * @returns Vant Tag 组件的 type 值
 */
export const getStatusType = (status: string): 'success' | 'danger' | 'warning' | 'default' => {
  switch (status) {
    case '已完成':
    case '已确认':
    case '已审批':
      return 'success'
    case '未进行':
    case '已退回':
      return 'danger'
    case '待确认':
      return 'warning'
    default:
      return 'default'
  }
}

/**
 * 获取状态的显示文本
 * @param status 状态字符串
 * @returns 用于显示的状态文本
 */
export const getDisplayStatus = (status: string): string => {
  if (status === '已确认' || status === '已完成' || status === '已审批') return '已完成'
  if (status === '待确认') return '待确认'
  if (status === '已退回') return '已退回'
  if (status === '未进行') return '待处理'
  return status
}

/**
 * 判断状态是否为完成状态
 * @param status 状态字符串
 * @returns 是否为完成状态
 */
export const isCompletedStatus = (status: string): boolean => {
  return ['已完成', '已确认', '已审批'].includes(status)
}

/**
 * 判断状态是否为待处理状态
 * @param status 状态字符串
 * @returns 是否为待处理状态
 */
export const isPendingStatus = (status: string): boolean => {
  return ['未进行', '已退回'].includes(status)
}

/**
 * 判断状态是否为待确认状态
 * @param status 状态字符串
 * @returns 是否为待确认状态
 */
export const isConfirmingStatus = (status: string): boolean => {
  return status === '待确认'
}

/**
 * 工单列表页面的基础 Tabs 配置
 */
export const BASE_WORK_TABS = [
  { key: '待处理', title: '待处理', statuses: ['未进行', '已退回'] as string[], color: '#ee0a24' },
  { key: '待确认', title: '待确认', statuses: ['待确认'] as string[], color: '#ff976a' },
  { key: '已完成', title: '已完成', statuses: ['已确认', '已完成', '已审批'] as string[], color: '#07c160' }
]

/**
 * 审批 Tab 配置
 */
export const APPROVAL_TAB = { key: '审批', title: '审批', statuses: ['待确认'] as string[], color: '#1989fa' }

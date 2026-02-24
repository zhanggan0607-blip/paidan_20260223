/**
 * 格式化相关工具函数
 * 统一管理日期、工单编号等格式化逻辑
 */

/**
 * 格式化日期为 YYYY-MM-DD 格式
 * @param dateStr 日期字符串或Date对象
 * @returns 格式化后的日期字符串，无效日期返回 '-'
 */
export const formatDate = (dateStr: string | Date | null | undefined): string => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  if (isNaN(date.getTime())) return '-'
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

/**
 * 格式化日期时间为 YYYY-MM-DD HH:mm 格式
 * @param dateStr 日期字符串或Date对象
 * @returns 格式化后的日期时间字符串，无效日期返回 '-'
 */
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

/**
 * 格式化日期用于输入框 (YYYY-MM-DD)
 * @param dateStr 日期字符串或Date对象
 * @returns 格式化后的日期字符串，无效日期返回空字符串
 */
export const formatDateForInput = (dateStr: string | Date | null | undefined): string => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  if (isNaN(date.getTime())) return ''
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

/**
 * 根据工单编号长度计算字体大小
 * @param workId 工单编号
 * @returns 字体大小(px)
 */
export const getWorkIdFontSize = (workId: string): number => {
  if (!workId) return 14
  const len = workId.length
  if (len <= 18) return 14
  if (len <= 22) return 12
  if (len <= 26) return 11
  if (len <= 30) return 10
  if (len <= 35) return 9
  if (len <= 40) return 8
  return 7
}

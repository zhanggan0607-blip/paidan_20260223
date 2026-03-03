/**
 * 日期时间格式化工具函数
 * 统一管理日期格式化，确保PC端和H5端一致
 */

/**
 * 格式化日期为 YYYY-MM-DD 格式
 * @param date 日期对象或字符串
 * @returns 格式化后的日期字符串
 */
export const formatDate = (date: Date | string | null | undefined): string => {
  if (!date) return ''
  const d = typeof date === 'string' ? new Date(date) : date
  if (isNaN(d.getTime())) return ''
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

/**
 * 格式化日期时间为 YYYY-MM-DD HH:mm:ss 格式
 * @param date 日期对象或字符串
 * @returns 格式化后的日期时间字符串
 */
export const formatDateTime = (date: Date | string | null | undefined): string => {
  if (!date) return ''
  const d = typeof date === 'string' ? new Date(date) : date
  if (isNaN(d.getTime())) return ''
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const hours = String(d.getHours()).padStart(2, '0')
  const minutes = String(d.getMinutes()).padStart(2, '0')
  const seconds = String(d.getSeconds()).padStart(2, '0')
  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
}

/**
 * 格式化时间为 HH:mm:ss 格式
 * @param date 日期对象或字符串
 * @returns 格式化后的时间字符串
 */
export const formatTime = (date: Date | string | null | undefined): string => {
  if (!date) return ''
  const d = typeof date === 'string' ? new Date(date) : date
  if (isNaN(d.getTime())) return ''
  const hours = String(d.getHours()).padStart(2, '0')
  const minutes = String(d.getMinutes()).padStart(2, '0')
  const seconds = String(d.getSeconds()).padStart(2, '0')
  return `${hours}:${minutes}:${seconds}`
}

/**
 * 格式化日期用于输入框 (YYYY-MM-DD)
 * @param date 日期对象或字符串
 * @returns 格式化后的日期字符串
 */
export const formatDateForInput = (date: Date | string | null | undefined): string => {
  return formatDate(date)
}

/**
 * 获取当前格式化日期时间
 * @returns 当前日期时间字符串
 */
export const getCurrentDateTime = (): string => {
  return formatDateTime(new Date())
}

/**
 * 获取当前格式化日期
 * @returns 当前日期字符串
 */
export const getCurrentDate = (): string => {
  return formatDate(new Date())
}

/**
 * 解析日期字符串为Date对象
 * @param dateStr 日期字符串
 * @returns Date对象或null
 */
export const parseDate = (dateStr: string | null | undefined): Date | null => {
  if (!dateStr) return null
  const d = new Date(dateStr)
  return isNaN(d.getTime()) ? null : d
}

/**
 * 计算两个日期之间的天数差
 * @param startDate 开始日期
 * @param endDate 结束日期
 * @returns 天数差
 */
export const getDaysDiff = (startDate: Date | string, endDate: Date | string): number => {
  const start = typeof startDate === 'string' ? new Date(startDate) : startDate
  const end = typeof endDate === 'string' ? new Date(endDate) : endDate
  const diffTime = end.getTime() - start.getTime()
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24))
}

/**
 * 判断日期是否过期
 * @param date 日期
 * @returns 是否过期
 */
export const isOverdue = (date: Date | string | null | undefined): boolean => {
  if (!date) return false
  const d = typeof date === 'string' ? new Date(date) : date
  return d < new Date()
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

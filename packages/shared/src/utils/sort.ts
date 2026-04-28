/**
 * 数据排序工具函数
 * 提供统一的降序排序逻辑，基于最新操作时间戳
 * 适用于 PC 端和 H5 端
 */

/**
 * 从数据对象中提取排序时间戳
 * 优先级：updated_at > created_at > 其他时间字段 > id
 * @param item 数据对象
 * @returns 时间戳（毫秒），如果无法提取则返回 0
 */
export function getSortTimestamp(item: any): number {
  if (!item) return 0
  
  // 尝试多个可能的时间字段，按优先级排序
  const timeFields = [
    'updated_at',      // 最后更新时间
    'created_at',      // 创建时间
    'last_activity',   // 最后活动时间
    'actual_completion_date',  // 实际完成时间
    'plan_end_date',   // 计划结束时间
    'plan_start_date', // 计划开始时间
    'execution_date',  // 执行时间
    'deleted_at',      // 删除时间
  ]
  
  for (const field of timeFields) {
    if (item[field]) {
      const timestamp = new Date(item[field]).getTime()
      if (!isNaN(timestamp)) {
        return timestamp
      }
    }
  }
  
  // 如果所有时间字段都无效，使用 id 作为后备排序依据
  return 0
}

/**
 * 按时间戳降序排序（最新的在前）
 * @param items 待排序的数据数组
 * @param options 排序选项
 * @returns 排序后的新数组
 */
export function sortByTimestampDesc<T extends Record<string, any>>(
  items: T[],
  options?: {
    // 自定义获取时间戳的函数
    getTimestamp?: (item: T) => number
    // 次要排序键（当时间戳相同时使用）
    secondarySortKey?: keyof T
    // 是否升序（默认降序）
    ascending?: boolean
  }
): T[] {
  if (!Array.isArray(items)) {
    console.warn('sortByTimestampDesc: input is not an array')
    return []
  }
  
  const {
    getTimestamp = getSortTimestamp,
    secondarySortKey = 'id',
    ascending = false
  } = options || {}
  
  return [...items].sort((a, b) => {
    const timeA = getTimestamp(a)
    const timeB = getTimestamp(b)
    
    // 首先按时间戳排序
    if (timeB !== timeA) {
      return ascending ? timeA - timeB : timeB - timeA
    }
    
    // 时间戳相同时，按次要键排序（默认按 id 降序）
    const valueA = a[secondarySortKey] || 0
    const valueB = b[secondarySortKey] || 0
    
    if (typeof valueA === 'number' && typeof valueB === 'number') {
      return ascending ? valueA - valueB : valueB - valueA
    }
    
    // 如果不是数字，转为字符串比较
    const strA = String(valueA)
    const strB = String(valueB)
    return ascending ? strA.localeCompare(strB) : strB.localeCompare(strA)
  })
}

/**
 * 按时间戳升序排序（最旧的在前）
 * @param items 待排序的数据数组
 * @param options 排序选项
 * @returns 排序后的新数组
 */
export function sortByTimestampAsc<T extends Record<string, any>>(
  items: T[],
  options?: {
    getTimestamp?: (item: T) => number
    secondarySortKey?: keyof T
  }
): T[] {
  return sortByTimestampDesc(items, { ...options, ascending: true })
}

/**
 * 批量排序多个数组
 * @param arrays 包含多个数组的对象
 * @param options 排序选项
 * @returns 包含排序后数组的对象
 */
export function sortMultipleArrays<T extends Record<string, any>>(
  arrays: Record<string, T[]>,
  options?: {
    getTimestamp?: (item: T) => number
    secondarySortKey?: keyof T
  }
): Record<string, T[]> {
  const result: Record<string, T[]> = {}
  
  for (const [key, array] of Object.entries(arrays)) {
    result[key] = sortByTimestampDesc(array, options)
  }
  
  return result
}

/**
 * 创建带有排序功能的响应数据处理器
 * @param responseData API 响应数据
 * @param options 排序选项
 * @returns 排序后的数据
 */
export function processSortedResponse<T extends Record<string, any>>(
  responseData: { data?: T[] | Record<string, T[]> },
  options?: {
    getTimestamp?: (item: T) => number
    secondarySortKey?: keyof T
  }
): T[] | Record<string, T[]> {
  if (!responseData?.data) {
    return []
  }
  
  if (Array.isArray(responseData.data)) {
    return sortByTimestampDesc(responseData.data, options)
  }
  
  return sortMultipleArrays(responseData.data as Record<string, T[]>, options)
}

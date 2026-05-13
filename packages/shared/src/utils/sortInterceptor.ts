/**
 * 全局排序拦截器
 * 自动对所有 API 响应数据进行统一排序
 * 实现跨平台（PC 和 H5）的排序一致性
 */

import type { AxiosResponse } from 'axios'
import { getSortTimestamp, sortByTimestampDesc as _sortByTimestampDesc } from './sort'

/**
 * 排序配置接口
 */
export interface SortConfig {
  // 是否启用自动排序
  enabled: boolean
  // 默认排序字段
  secondarySortKey: string
  // 是否升序（默认降序）
  ascending: boolean
  // 需要跳过的 API 路径（不需要排序的接口）
  skipPaths: string[]
  // 自定义排序映射（针对特定 API 路径）
  customSorters: Record<string, (data: any) => any>
}

/**
 * 全局排序配置
 */
const defaultSortConfig: SortConfig = {
  enabled: true,
  secondarySortKey: 'id',
  ascending: false,
  skipPaths: [
    '/auth/',
    '/user/',
    '/statistics',
    '/config/',
    '/upload/',
    '/ocr/',
  ],
  customSorters: {},
}

let sortConfig = { ...defaultSortConfig }

/**
 * 获取排序配置
 */
export function getSortConfig(): SortConfig {
  return { ...sortConfig }
}

/**
 * 更新排序配置
 */
export function updateSortConfig(config: Partial<SortConfig>): void {
  sortConfig = { ...sortConfig, ...config }
}

/**
 * 重置为默认配置
 */
export function resetSortConfig(): void {
  sortConfig = { ...defaultSortConfig }
}

/**
 * 按时间戳降序排序
 */
function sortByTimestampDesc<T extends Record<string, any>>(
  items: T[],
  secondarySortKey: string = 'id',
  ascending: boolean = false
): T[] {
  return _sortByTimestampDesc(items, { secondarySortKey: secondarySortKey as keyof T, ascending })
}

/**
 * 判断是否需要跳过排序
 */
function shouldSkipSort(url: string): boolean {
  return sortConfig.skipPaths.some(path => url.includes(path))
}

/**
 * 获取自定义排序器
 */
function getCustomSorter(url: string): ((data: any) => any) | undefined {
  return sortConfig.customSorters[url]
}

/**
 * 处理响应数据
 */
function processResponseData(response: AxiosResponse): AxiosResponse {
  // 如果未启用排序或需要跳过，直接返回
  const url = response?.config?.url || ''
  if (!sortConfig.enabled || shouldSkipSort(url)) {
    return response
  }

  // 检查是否有自定义排序器
  const customSorter = getCustomSorter(url)
  if (customSorter) {
    if (response.data?.data) {
      response.data.data = customSorter(response.data.data)
    }
    return response
  }

  // 处理标准响应格式
  if (response.data?.data) {
    if (Array.isArray(response.data.data)) {
      // 直接数组
      response.data.data = sortByTimestampDesc(
        response.data.data,
        sortConfig.secondarySortKey,
        sortConfig.ascending
      )
    } else if (typeof response.data.data === 'object') {
      // 对象中包含多个数组（如 { content: [], total: 0 }）
      const dataObj = response.data.data
      for (const key in dataObj) {
        if (Array.isArray(dataObj[key])) {
          dataObj[key] = sortByTimestampDesc(
            dataObj[key],
            sortConfig.secondarySortKey,
            sortConfig.ascending
          )
        }
      }
      response.data.data = dataObj
    }
  }

  return response
}

/**
 * 创建排序拦截器
 * @param axiosInstance axios 实例
 */
export function createSortInterceptor(axiosInstance: any): void {
  if (!axiosInstance?.interceptors?.response) {
    console.warn('createSortInterceptor: invalid axios instance')
    return
  }
  
  // 响应拦截器
  axiosInstance.interceptors.response.use(
    (response: any) => {
      return processResponseData(response)
    },
    (error: any) => {
      return Promise.reject(error)
    }
  )
}

/**
 * 注册自定义排序器
 * @param path API 路径
 * @param sorter 排序函数
 */
export function registerCustomSorter(
  path: string,
  sorter: (data: any) => any
): void {
  sortConfig.customSorters[path] = sorter
}

/**
 * 移除自定义排序器
 * @param path API 路径
 */
export function unregisterCustomSorter(path: string): void {
  delete sortConfig.customSorters[path]
}

/**
 * 临时禁用自动排序
 */
export function disableAutoSort(): void {
  sortConfig.enabled = false
}

/**
 * 启用自动排序
 */
export function enableAutoSort(): void {
  sortConfig.enabled = true
}

/**
 * 添加需要跳过的 API 路径
 * @param path API 路径
 */
export function addSkipPath(path: string): void {
  if (!sortConfig.skipPaths.includes(path)) {
    sortConfig.skipPaths.push(path)
  }
}

/**
 * 移除需要跳过的 API 路径
 * @param path API 路径
 */
export function removeSkipPath(path: string): void {
  sortConfig.skipPaths = sortConfig.skipPaths.filter(p => p !== path)
}

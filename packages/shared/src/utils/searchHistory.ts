/**
 * 搜索历史管理工具
 * 统一管理搜索历史记录，支持PC端和H5端
 */

const SEARCH_HISTORY_KEY = 'search_history'
const MAX_HISTORY_SIZE = 20

export interface SearchHistoryItem {
  keyword: string
  timestamp: number
  type?: string
}

/**
 * 获取搜索历史
 * @param type 可选的类型过滤
 * @returns 搜索历史列表
 */
export const getSearchHistory = (type?: string): SearchHistoryItem[] => {
  try {
    const historyStr = localStorage.getItem(SEARCH_HISTORY_KEY)
    if (!historyStr) return []
    const history: SearchHistoryItem[] = JSON.parse(historyStr)
    if (type) {
      return history.filter(item => item.type === type)
    }
    return history
  } catch {
    return []
  }
}

/**
 * 添加搜索历史
 * @param keyword 搜索关键词
 * @param type 可选的类型
 */
export const addSearchHistory = (keyword: string, type?: string): void => {
  if (!keyword.trim()) return
  
  try {
    const history = getSearchHistory()
    const existingIndex = history.findIndex(
      item => item.keyword === keyword && (type ? item.type === type : true)
    )
    
    if (existingIndex !== -1) {
      history.splice(existingIndex, 1)
    }
    
    history.unshift({
      keyword: keyword.trim(),
      timestamp: Date.now(),
      type
    })
    
    if (history.length > MAX_HISTORY_SIZE) {
      history.splice(MAX_HISTORY_SIZE)
    }
    
    localStorage.setItem(SEARCH_HISTORY_KEY, JSON.stringify(history))
  } catch {
    console.error('保存搜索历史失败')
  }
}

/**
 * 删除单条搜索历史
 * @param keyword 搜索关键词
 * @param type 可选的类型
 */
export const removeSearchHistory = (keyword: string, type?: string): void => {
  try {
    let history = getSearchHistory()
    history = history.filter(
      item => !(item.keyword === keyword && (type ? item.type === type : true))
    )
    localStorage.setItem(SEARCH_HISTORY_KEY, JSON.stringify(history))
  } catch {
    console.error('删除搜索历史失败')
  }
}

/**
 * 清空搜索历史
 * @param type 可选的类型，不传则清空全部
 */
export const clearSearchHistory = (type?: string): void => {
  try {
    if (type) {
      let history = getSearchHistory()
      history = history.filter(item => item.type !== type)
      localStorage.setItem(SEARCH_HISTORY_KEY, JSON.stringify(history))
    } else {
      localStorage.removeItem(SEARCH_HISTORY_KEY)
    }
  } catch {
    console.error('清空搜索历史失败')
  }
}

/**
 * 获取最近搜索关键词列表
 * @param limit 限制数量
 * @param type 可选的类型过滤
 * @returns 关键词列表
 */
export const getRecentKeywords = (limit: number = 10, type?: string): string[] => {
  const history = getSearchHistory(type)
  return history.slice(0, limit).map(item => item.keyword)
}

/**
 * 搜索历史配置接口（兼容PC/H5端）
 */
export interface SearchHistoryConfig {
  fieldKey: string
  maxItems?: number
}

const SEARCH_HISTORY_PREFIX = 'search_history_'
const MAX_HISTORY_ITEMS = 10

/**
 * 保存搜索历史（按字段键）
 * @param fieldKey 字段键
 * @param value 搜索值
 */
export function saveSearchHistory(fieldKey: string, value: string): void {
  if (!value || !value.trim()) return
  
  try {
    const key = SEARCH_HISTORY_PREFIX + fieldKey
    const stored = localStorage.getItem(key)
    let history: string[] = stored ? JSON.parse(stored) : []
    
    history = history.filter(item => item !== value)
    history.unshift(value)
    
    if (history.length > MAX_HISTORY_ITEMS) {
      history = history.slice(0, MAX_HISTORY_ITEMS)
    }
    
    localStorage.setItem(key, JSON.stringify(history))
  } catch (error) {
    console.error('保存搜索历史失败:', error)
  }
}

/**
 * 加载搜索历史（按字段键）
 * @param fieldKey 字段键
 * @returns 搜索历史列表
 */
export function loadSearchHistory(fieldKey: string): string[] {
  try {
    const key = SEARCH_HISTORY_PREFIX + fieldKey
    const stored = localStorage.getItem(key)
    return stored ? JSON.parse(stored) : []
  } catch (error) {
    console.error('加载搜索历史失败:', error)
    return []
  }
}

/**
 * 清除指定字段的搜索历史
 * @param fieldKey 字段键
 */
export function clearFieldSearchHistory(fieldKey: string): void {
  try {
    const key = SEARCH_HISTORY_PREFIX + fieldKey
    localStorage.removeItem(key)
  } catch (error) {
    console.error('清除搜索历史失败:', error)
  }
}

/**
 * 过滤搜索历史
 * @param history 搜索历史列表
 * @param keyword 关键词
 * @returns 过滤后的列表
 */
export function filterHistoryByKeyword(history: string[], keyword: string): string[] {
  if (!keyword || !keyword.trim()) return history
  const lowerKeyword = keyword.toLowerCase()
  return history.filter(item => item.toLowerCase().includes(lowerKeyword))
}

/**
 * 搜索历史组合式函数
 * @param config 配置
 * @returns 搜索历史操作方法
 */
export function useSearchHistory(config: SearchHistoryConfig) {
  const { fieldKey } = config

  const save = (value: string) => {
    saveSearchHistory(fieldKey, value)
  }

  const load = (): string[] => {
    return loadSearchHistory(fieldKey)
  }

  const clear = () => {
    clearFieldSearchHistory(fieldKey)
  }

  const filter = (keyword: string): string[] => {
    const history = load()
    return filterHistoryByKeyword(history, keyword)
  }

  return {
    save,
    load,
    clear,
    filter
  }
}

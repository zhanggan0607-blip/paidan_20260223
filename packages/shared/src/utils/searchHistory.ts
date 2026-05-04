/**
 * 搜索历史管理工具
 * 统一管理搜索历史记录，支持PC端和H5端
 */

const SEARCH_HISTORY_PREFIX = 'search_history_'
const GLOBAL_HISTORY_KEY = 'search_history'
const DEFAULT_MAX_ITEMS = 20

export interface SearchHistoryItem {
  keyword: string
  timestamp: number
  type?: string
}

export interface SearchHistoryConfig {
  fieldKey: string
  maxItems?: number
}

function _loadItems(key: string): SearchHistoryItem[] {
  try {
    const stored = localStorage.getItem(key)
    if (!stored) return []
    return JSON.parse(stored)
  } catch {
    return []
  }
}

function _saveItems(key: string, items: SearchHistoryItem[], maxItems: number): void {
  try {
    if (items.length > maxItems) {
      items = items.slice(0, maxItems)
    }
    localStorage.setItem(key, JSON.stringify(items))
  } catch {
    console.error('保存搜索历史失败')
  }
}

function _addFieldItem(fieldKey: string, keyword: string, maxItems: number = DEFAULT_MAX_ITEMS): void {
  if (!keyword.trim()) return
  const key = SEARCH_HISTORY_PREFIX + fieldKey
  const items = _loadItems(key)
  const idx = items.findIndex(i => i.keyword === keyword)
  if (idx !== -1) items.splice(idx, 1)
  items.unshift({ keyword: keyword.trim(), timestamp: Date.now() })
  _saveItems(key, items, maxItems)
}

function _getFieldItems(fieldKey: string): SearchHistoryItem[] {
  return _loadItems(SEARCH_HISTORY_PREFIX + fieldKey)
}

function _removeFieldItem(fieldKey: string, keyword: string): void {
  const key = SEARCH_HISTORY_PREFIX + fieldKey
  const items = _loadItems(key)
  const filtered = items.filter(i => i.keyword !== keyword)
  _saveItems(key, filtered, DEFAULT_MAX_ITEMS)
}

function _clearFieldItems(fieldKey: string): void {
  try {
    localStorage.removeItem(SEARCH_HISTORY_PREFIX + fieldKey)
  } catch {
    console.error('清除搜索历史失败')
  }
}

export function getSearchHistory(type?: string): SearchHistoryItem[] {
  const items = _loadItems(GLOBAL_HISTORY_KEY)
  if (type) return items.filter(i => i.type === type)
  return items
}

export function addSearchHistory(keyword: string, type?: string): void {
  if (!keyword.trim()) return
  const items = _loadItems(GLOBAL_HISTORY_KEY)
  const idx = items.findIndex(i => i.keyword === keyword && (type ? i.type === type : true))
  if (idx !== -1) items.splice(idx, 1)
  items.unshift({ keyword: keyword.trim(), timestamp: Date.now(), type })
  _saveItems(GLOBAL_HISTORY_KEY, items, DEFAULT_MAX_ITEMS)
}

export function removeSearchHistory(keyword: string, type?: string): void {
  const items = _loadItems(GLOBAL_HISTORY_KEY)
  const filtered = items.filter(i => !(i.keyword === keyword && (type ? i.type === type : true)))
  _saveItems(GLOBAL_HISTORY_KEY, filtered, DEFAULT_MAX_ITEMS)
}

export function clearSearchHistory(type?: string): void {
  if (type) {
    const items = _loadItems(GLOBAL_HISTORY_KEY)
    const filtered = items.filter(i => i.type !== type)
    _saveItems(GLOBAL_HISTORY_KEY, filtered, DEFAULT_MAX_ITEMS)
  } else {
    try { localStorage.removeItem(GLOBAL_HISTORY_KEY) } catch { /* noop */ }
  }
}

export function getRecentKeywords(limit: number = 10, type?: string): string[] {
  return getSearchHistory(type).slice(0, limit).map(i => i.keyword)
}

export function saveSearchHistory(fieldKey: string, value: string): void {
  _addFieldItem(fieldKey, value)
}

export function loadSearchHistory(fieldKey: string): string[] {
  return _getFieldItems(fieldKey).map(i => i.keyword)
}

export function clearFieldSearchHistory(fieldKey: string): void {
  _clearFieldItems(fieldKey)
}

export function filterHistoryByKeyword(history: string[], keyword: string): string[] {
  if (!keyword || !keyword.trim()) return history
  const lower = keyword.toLowerCase()
  return history.filter(item => item.toLowerCase().includes(lower))
}

export function useSearchHistory(config: SearchHistoryConfig) {
  const { fieldKey, maxItems = DEFAULT_MAX_ITEMS } = config

  return {
    save: (value: string) => _addFieldItem(fieldKey, value, maxItems),
    load: (): string[] => _getFieldItems(fieldKey).map(i => i.keyword),
    clear: () => _clearFieldItems(fieldKey),
    filter: (keyword: string): string[] => {
      const history = _getFieldItems(fieldKey).map(i => i.keyword)
      return filterHistoryByKeyword(history, keyword)
    },
  }
}

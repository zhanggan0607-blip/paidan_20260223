const SEARCH_HISTORY_PREFIX = 'search_history_'
const MAX_HISTORY_ITEMS = 10

export interface SearchHistoryConfig {
  fieldKey: string
  maxItems?: number
}

export function saveSearchHistory(fieldKey: string, value: string) {
  if (!value || !value.trim()) {
    return
  }
  
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

export function clearSearchHistory(fieldKey: string) {
  try {
    const key = SEARCH_HISTORY_PREFIX + fieldKey
    localStorage.removeItem(key)
  } catch (error) {
    console.error('清除搜索历史失败:', error)
  }
}

export function clearAllSearchHistory() {
  try {
    const keys = Object.keys(localStorage)
    keys.forEach(key => {
      if (key.startsWith(SEARCH_HISTORY_PREFIX)) {
        localStorage.removeItem(key)
      }
    })
  } catch (error) {
    console.error('清除所有搜索历史失败:', error)
  }
}

export function filterHistoryByKeyword(history: string[], keyword: string): string[] {
  if (!keyword || !keyword.trim()) {
    return history
  }
  const lowerKeyword = keyword.toLowerCase()
  return history.filter(item => 
    item.toLowerCase().includes(lowerKeyword)
  )
}

export function useSearchHistory(config: SearchHistoryConfig) {
  const { fieldKey, maxItems = MAX_HISTORY_ITEMS } = config

  const save = (value: string) => {
    saveSearchHistory(fieldKey, value)
  }

  const load = (): string[] => {
    return loadSearchHistory(fieldKey)
  }

  const clear = () => {
    clearSearchHistory(fieldKey)
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

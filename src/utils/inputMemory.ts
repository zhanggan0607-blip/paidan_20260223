const STORAGE_PREFIX = 'input_memory_'

export interface MemoryConfig {
  pageName: string
  fields: string[]
  onRestore?: (data: Record<string, any>) => void
}

export function saveInputMemory(pageName: string, data: Record<string, any>) {
  try {
    const key = STORAGE_PREFIX + pageName
    localStorage.setItem(key, JSON.stringify(data))
  } catch (error) {
    console.error('保存输入记忆失败:', error)
  }
}

export function loadInputMemory(pageName: string): Record<string, any> | null {
  try {
    const key = STORAGE_PREFIX + pageName
    const stored = localStorage.getItem(key)
    return stored ? JSON.parse(stored) : null
  } catch (error) {
    console.error('加载输入记忆失败:', error)
    return null
  }
}

export function clearInputMemory(pageName: string) {
  try {
    const key = STORAGE_PREFIX + pageName
    localStorage.removeItem(key)
  } catch (error) {
    console.error('清除输入记忆失败:', error)
  }
}

export function clearAllInputMemory() {
  try {
    const keys = Object.keys(localStorage)
    keys.forEach(key => {
      if (key.startsWith(STORAGE_PREFIX)) {
        localStorage.removeItem(key)
      }
    })
  } catch (error) {
    console.error('清除所有输入记忆失败:', error)
  }
}

export function useInputMemory(config: MemoryConfig) {
  const { pageName, fields, onRestore } = config

  const saveMemory = (formData: Record<string, any>) => {
    const dataToSave: Record<string, any> = {}
    fields.forEach(field => {
      if (formData[field] !== undefined) {
        dataToSave[field] = formData[field]
      }
    })
    saveInputMemory(pageName, dataToSave)
  }

  const loadMemory = (): Record<string, any> | null => {
    const stored = loadInputMemory(pageName)
    if (stored && onRestore) {
      onRestore(stored)
    }
    return stored
  }

  const clearMemory = () => {
    clearInputMemory(pageName)
  }

  return {
    saveMemory,
    loadMemory,
    clearMemory
  }
}

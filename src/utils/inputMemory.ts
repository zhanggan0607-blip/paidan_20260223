// TODO: 输入记忆工具 - 考虑加入过期时间设置
// FIXME: localStorage 有容量限制，大数据量时可能失败
// TODO: 考虑加入加密存储敏感信息

/**
 * 输入记忆工具模块
 * 用于保存和恢复表单输入数据，提升用户体验
 */

const STORAGE_PREFIX = 'input_memory_'

/**
 * 记忆配置接口
 */
export interface MemoryConfig {
  /** 页面名称，作为存储键名的一部分 */
  pageName: string
  /** 需要记忆的字段列表 */
  fields: string[]
  /** 恢复数据时的回调函数 */
  onRestore?: (data: Record<string, any>) => void
}

/**
 * 保存输入记忆到本地存储
 * @param pageName 页面名称
 * @param data 要保存的数据对象
 */
export function saveInputMemory(pageName: string, data: Record<string, any>) {
  try {
    const key = STORAGE_PREFIX + pageName
    localStorage.setItem(key, JSON.stringify(data))
  } catch (error) {
    console.error('保存输入记忆失败:', error)
  }
}

/**
 * 从本地存储加载输入记忆
 * @param pageName 页面名称
 * @returns 保存的数据对象，不存在或解析失败返回null
 */
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

/**
 * 清除指定页面的输入记忆
 * @param pageName 页面名称
 */
export function clearInputMemory(pageName: string) {
  try {
    const key = STORAGE_PREFIX + pageName
    localStorage.removeItem(key)
  } catch (error) {
    console.error('清除输入记忆失败:', error)
  }
}

/**
 * 清除所有页面的输入记忆
 */
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

/**
 * 输入记忆组合式函数
 * 提供便捷的记忆保存、加载、清除方法
 * @param config 记忆配置对象
 * @returns 包含saveMemory、loadMemory、clearMemory方法的对象
 */
export function useInputMemory(config: MemoryConfig) {
  const { pageName, fields, onRestore } = config

  /**
   * 保存表单数据到记忆存储
   * @param formData 表单数据对象
   */
  const saveMemory = (formData: Record<string, any>) => {
    const dataToSave: Record<string, any> = {}
    fields.forEach(field => {
      if (formData[field] !== undefined) {
        dataToSave[field] = formData[field]
      }
    })
    saveInputMemory(pageName, dataToSave)
  }

  /**
   * 从记忆存储加载表单数据
   * @returns 保存的数据对象，不存在返回null
   */
  const loadMemory = (): Record<string, any> | null => {
    const stored = loadInputMemory(pageName)
    if (stored && onRestore) {
      onRestore(stored)
    }
    return stored
  }

  /**
   * 清除当前页面的记忆数据
   */
  const clearMemory = () => {
    clearInputMemory(pageName)
  }

  return {
    saveMemory,
    loadMemory,
    clearMemory
  }
}

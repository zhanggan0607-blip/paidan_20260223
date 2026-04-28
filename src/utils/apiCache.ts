/**
 * PC端API缓存工具
 * 缓存高频API响应，减少重复网络请求
 */
interface CacheItem<T> {
  data: T
  timestamp: number
  ttl: number
}

class ApiCache {
  private cache = new Map<string, CacheItem<any>>()

  get<T>(key: string): T | null {
    const item = this.cache.get(key)
    if (!item) return null

    if (Date.now() - item.timestamp > item.ttl) {
      this.cache.delete(key)
      return null
    }

    return item.data as T
  }

  set<T>(key: string, data: T, ttl: number = 60000): void {
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      ttl,
    })
  }

  delete(key: string): boolean {
    return this.cache.delete(key)
  }

  clear(): void {
    this.cache.clear()
  }

  has(key: string): boolean {
    const item = this.cache.get(key)
    if (!item) return false

    if (Date.now() - item.timestamp > item.ttl) {
      this.cache.delete(key)
      return false
    }

    return true
  }
}

export const apiCache = new ApiCache()

export const CACHE_KEYS = {
  PROJECT_INFO: 'project_info',
  PERSONNEL: 'personnel',
  CUSTOMER: 'customer',
  DICTIONARY: 'dictionary',
  INSPECTION_ITEMS: 'inspection_items',
  STATISTICS: 'statistics',
}

export const CACHE_TTL = {
  SHORT: 60000,
  MEDIUM: 180000,
  LONG: 600000,
}

export default apiCache

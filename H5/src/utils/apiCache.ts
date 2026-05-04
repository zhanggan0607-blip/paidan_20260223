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
  WORK_ORDER_COMPLETED: 'work_order_completed',
  OVERDUE_ALERT: 'overdue_alert',
  EXPIRING_SOON: 'expiring_soon',
  PROJECT_INFO: 'project_info',
  PERSONNEL: 'personnel',
  CUSTOMER: 'customer',
  STATISTICS: 'statistics',
  TEMPORARY_REPAIR_PENDING: 'temporary_repair_pending',
  SPOT_WORK_PENDING: 'spot_work_pending',
  PERIODIC_INSPECTION_PENDING: 'periodic_inspection_pending',
}

export const CACHE_TTL = {
  SHORT: 60000,
  MEDIUM: 180000,
  LONG: 600000,
}

export default apiCache

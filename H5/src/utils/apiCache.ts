export type CacheEntry<T> = {
  data: T
  timestamp: number
  ttl: number
}

export type CacheOptions = {
  ttl: number
  maxSize: number
  enabled: boolean
}

export const DEFAULT_CACHE_OPTIONS: CacheOptions = {
  ttl: 5 * 60 * 1000,
  maxSize: 100,
  enabled: true,
}

export class ApiCache {
  private cache: Map<string, CacheEntry<unknown>> = new Map()
  private options: CacheOptions
  private cleanupTimer: ReturnType<typeof setInterval> | null = null

  constructor(options: CacheOptions = DEFAULT_CACHE_OPTIONS) {
    this.options = { ...options }
    this.cleanupTimer = setInterval(() => { this.cleanup() }, 60 * 1000)
  }

  private cleanup(): void {
    const now = Date.now()
    for (const [key, entry] of this.cache.entries()) {
      if (now - entry.timestamp > entry.ttl) { this.cache.delete(key) }
    }
  }

  get<T>(key: string): T | null {
    const entry = this.cache.get(key) as CacheEntry<T> | undefined
    if (!entry) return null
    if (Date.now() - entry.timestamp > entry.ttl) { this.cache.delete(key); return null }
    return entry.data
  }

  set<T>(key: string, data: T, ttl?: number): void {
    if (!this.options.enabled) return
    if (this.cache.size >= this.options.maxSize) {
      const firstKey = this.cache.keys().next().value
      if (firstKey) this.cache.delete(firstKey)
    }
    this.cache.set(key, { data, timestamp: Date.now(), ttl: ttl ?? this.options.ttl })
  }

  clear(): void { this.cache.clear() }
  has(key: string): boolean { return this.cache.has(key) }
  delete(key: string): boolean { return this.cache.delete(key) }
  getStats(): { size: number; maxSize: number } { return { size: this.cache.size, maxSize: this.options.maxSize } }
  keys(): IterableIterator<string> { return this.cache.keys() }
  destroy(): void { if (this.cleanupTimer) { clearInterval(this.cleanupTimer); this.cleanupTimer = null }; this.cache.clear() }
}

let globalCache: ApiCache | null = null

export function getCache(): ApiCache {
  if (!globalCache) globalCache = new ApiCache()
  return globalCache
}

export const apiCache = getCache()

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

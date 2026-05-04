import { ref } from 'vue'
import type { ApiResponse } from '@sstcp/shared'

type CacheEntry<T> = {
  data: T
  timestamp: number
  ttl: number
}

type CacheOptions = {
  ttl: number
  maxSize: number
  enabled: boolean
}

const defaultOptions: CacheOptions = {
  ttl: 5 * 60 * 1000,
  maxSize: 100,
  enabled: true,
}

let globalCache: ApiCache | null = null

class ApiCache {
  private cache: Map<string, CacheEntry<unknown>> = new Map()
  private options: CacheOptions

  constructor(options: CacheOptions = defaultOptions) {
    this.options = { ...options }
    
    setInterval(() => {
      this.cleanup()
    }, 60 * 1000)
  }

  private cleanup(): void {
    const now = Date.now()
    for (const [key, entry] of this.cache.entries()) {
      if (now - entry.timestamp > entry.ttl) {
        this.cache.delete(key)
      }
    }
  }

  get<T>(key: string): T | null {
    const entry = this.cache.get(key) as CacheEntry<T> | undefined
    if (!entry) return null
    
    const now = Date.now()
    if (now - entry.timestamp > entry.ttl) {
      this.cache.delete(key)
      return null
    }
    
    return entry.data
  }

  set<T>(key: string, data: T, ttl?: number): void {
    if (!this.options.enabled) return
    
    if (this.cache.size >= this.options.maxSize) {
      const firstKey = this.cache.keys().next().value
      if (firstKey) {
        this.cache.delete(firstKey)
      }
    }
    
    const entry: CacheEntry<T> = {
      data,
      timestamp: Date.now(),
      ttl: ttl ?? this.options.ttl,
    }
    this.cache.set(key, entry)
  }

  clear(): void {
    this.cache.clear()
  }

  has(key: string): boolean {
    return this.cache.has(key)
  }

  delete(key: string): boolean {
    return this.cache.delete(key)
  }

  getStats(): { size: number; maxSize: number } {
    return {
      size: this.cache.size,
      maxSize: this.options.maxSize,
    }
  }

  keys(): IterableIterator<string> {
    return this.cache.keys()
  }
}

export function getCache(): ApiCache {
  if (!globalCache) {
    globalCache = new ApiCache()
  }
  return globalCache
}

export function useApiCache(_options?: Partial<CacheOptions>) {
  const cache = ref<ApiCache>(getCache())
  
  const getCacheData = <T>(key: string): T | null => {
    return cache.value.get<T>(key)
  }
  
  const setCacheData = <T>(key: string, data: T, ttl?: number): void => {
    cache.value.set(key, data, ttl)
  }
  
  const clearAllCache = (): void => {
    cache.value.clear()
  }
  
  const hasCacheKey = (key: string): boolean => {
    return cache.value.has(key)
  }
  
  const deleteCacheKey = (key: string): boolean => {
    return cache.value.delete(key)
  }
  
  const getStats = (): { size: number; maxSize: number } => {
    return cache.value.getStats()
  }
  
  return {
    getCache: getCacheData,
    setCache: setCacheData,
    clearCache: clearAllCache,
    hasCache: hasCacheKey,
    deleteCache: deleteCacheKey,
    getStats,
  }
}

export async function withCache<T>(
  key: string,
  fetcher: () => Promise<T>,
  ttl?: number
): Promise<T> {
  const cache = getCache()
  
  const cached = cache.get<T>(key)
  if (cached !== null) {
    return cached
  }
  
  const data = await fetcher()
  cache.set(key, data, ttl)
  return data
}

export function createCacheKey(
  endpoint: string,
  params?: Record<string, unknown>
): string {
  if (!params || Object.keys(params).length === 0) {
    return endpoint
  }
  
  const sortedParams = Object.entries(params)
    .filter(([, v]) => v !== undefined && v !== null && v !== '')
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([k, v]) => `${k}=${encodeURIComponent(String(v))}`)
    .join('&')
  
  return sortedParams ? `${endpoint}?${sortedParams}` : endpoint
}

export function clearApiCache(): void {
  getCache().clear()
}

export function invalidateCache(pattern: string): void {
  const cache = getCache()
  const keysToDelete: string[] = []
  
  for (const key of cache.keys()) {
    if (key.startsWith(pattern)) {
      keysToDelete.push(key)
    }
  }
  
  keysToDelete.forEach(key => cache.delete(key))
}


const pendingRequests = new Map<string, Promise<any>>()

export function deduplicateRequest<T>(
  key: string,
  requestFn: () => Promise<T>
): Promise<T> {
  if (pendingRequests.has(key)) {
    return pendingRequests.get(key)!
  }

  const promise = requestFn().finally(() => {
    pendingRequests.delete(key)
  })

  pendingRequests.set(key, promise)
  return promise
}

export function clearPendingRequests(): void {
  pendingRequests.clear()
}

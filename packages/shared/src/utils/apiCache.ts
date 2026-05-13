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

    this.cleanupTimer = setInterval(() => {
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

  destroy(): void {
    if (this.cleanupTimer) {
      clearInterval(this.cleanupTimer)
      this.cleanupTimer = null
    }
    this.cache.clear()
  }
}

let globalCache: ApiCache | null = null

export function getCache(): ApiCache {
  if (!globalCache) {
    globalCache = new ApiCache()
  }
  return globalCache
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

const pendingRequests = new Map<string, Promise<unknown>>()

export function deduplicateRequest<T>(
  key: string,
  requestFn: () => Promise<T>
): Promise<T> {
  if (pendingRequests.has(key)) {
    return pendingRequests.get(key)! as Promise<T>
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

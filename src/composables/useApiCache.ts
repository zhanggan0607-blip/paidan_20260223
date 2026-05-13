import { ref } from 'vue'
import {
  ApiCache,
  getCache,
  withCache,
  createCacheKey,
  clearApiCache,
  invalidateCache,
  deduplicateRequest,
  clearPendingRequests,
} from '@sstcp/shared'
import type { CacheOptions } from '@sstcp/shared'

export type { CacheOptions }

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

export {
  getCache,
  withCache,
  createCacheKey,
  clearApiCache,
  invalidateCache,
  deduplicateRequest,
  clearPendingRequests,
}

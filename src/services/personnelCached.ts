import { useApiCache, withCache, createCacheKey, invalidateCache } from '@/composables/useApiCache'
import type { ApiResponse } from '@sstcp/shared'
import request from '@/api/request'

const CACHE_PREFIX = '/api/v1/personnel'
const CACHE_TTL = 3 * 60 * 1000

export interface Personnel {
  id: number
  name: string
  role: string
  department: string
  phone: string
  email: string
  status: string
  created_at: string
  updated_at: string
}

export interface PersonnelQuery {
  page?: number
  size?: number
  name?: string
  department?: string
}

interface PersonnelListData {
  content: Personnel[]
  items: Personnel[]
  totalElements: number
  total: number
  totalPages: number
  size: number
  number: number
  first: boolean
  last: boolean
}

export const personnelCachedService = {
  async getList(params: PersonnelQuery = {}): Promise<ApiResponse<PersonnelListData>> {
    const cacheKey = createCacheKey(`${CACHE_PREFIX}/list`, params as Record<string, unknown>)
    
    return withCache(
      cacheKey,
      async () => {
        const response = await request.get<ApiResponse<PersonnelListData>>(
          '/api/v1/personnel',
          { params }
        )
        return response.data
      },
      CACHE_TTL
    )
  },

  async getById(id: number): Promise<Personnel> {
    const cacheKey = `${CACHE_PREFIX}/${id}`
    
    return withCache(
      cacheKey,
      async () => {
        const response = await request.get<ApiResponse<Personnel>>(
          `/api/v1/personnel/${id}`
        )
        return response.data.data!
      },
      CACHE_TTL
    )
  },

  async create(data: Partial<Personnel>): Promise<Personnel> {
    const response = await request.post<ApiResponse<Personnel>>(
      '/api/v1/personnel',
      data
    )
    
    invalidateCache(CACHE_PREFIX)
    
    return response.data.data!
  },

  async update(id: number, data: Partial<Personnel>): Promise<Personnel> {
    const response = await request.put<ApiResponse<Personnel>>(
      `/api/v1/personnel/${id}`,
      data
    )
    
    invalidateCache(CACHE_PREFIX)
    
    return response.data.data!
  },

  async delete(id: number): Promise<void> {
    await request.delete(`/api/v1/personnel/${id}`)
    
    invalidateCache(CACHE_PREFIX)
  },

  invalidateAll(): void {
    invalidateCache(CACHE_PREFIX)
  }
}

export function usePersonnelCache() {
  const { getCache, setCache, clearCache, hasCache, deleteCache, getStats } = useApiCache()
  
  const getCachedList = (params: PersonnelQuery): ApiResponse<PersonnelListData> | null => {
    const cacheKey = createCacheKey(`${CACHE_PREFIX}/list`, params as Record<string, unknown>)
    return getCache<ApiResponse<PersonnelListData>>(cacheKey)
  }
  
  const setCachedList = (params: PersonnelQuery, data: ApiResponse<PersonnelListData>): void => {
    const cacheKey = createCacheKey(`${CACHE_PREFIX}/list`, params as Record<string, unknown>)
    setCache(cacheKey, data, CACHE_TTL)
  }
  
  const getCachedItem = (id: number): Personnel | null => {
    const cacheKey = `${CACHE_PREFIX}/${id}`
    return getCache<Personnel>(cacheKey)
  }
  
  const setCachedItem = (id: number, data: Personnel): void => {
    const cacheKey = `${CACHE_PREFIX}/${id}`
    setCache(cacheKey, data, CACHE_TTL)
  }
  
  const clearPersonnelCache = (): void => {
    invalidateCache(CACHE_PREFIX)
  }
  
  return {
    getCachedList,
    setCachedList,
    getCachedItem,
    setCachedItem,
    clearPersonnelCache,
    getCacheStats: getStats,
  }
}

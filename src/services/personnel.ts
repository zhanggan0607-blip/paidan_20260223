/**
 * 人员管理服务模块
 * 提供人员数据的增删改查接口
 */
import request from '../api/request'
import { API_ENDPOINTS } from '../api/endpoints'
import type { ApiResponse, PaginatedData, Personnel, PersonnelCreate, PersonnelUpdate } from '@sstcp/shared'
import { withCache, createCacheKey, deduplicateRequest, clearApiCache, invalidateCache } from '@/composables/useApiCache'

export type { Personnel } from '@sstcp/shared'
export type { PersonnelCreate } from '@sstcp/shared'
export type { PersonnelUpdate } from '@sstcp/shared'

export const personnelService = {
  async getList(
    params?: {
      page?: number
      size?: number
      name?: string
      employee_id?: string
      department?: string
      status?: string
      current_user_role?: string
      current_user_department?: string
    },
    signal?: AbortSignal
  ): Promise<ApiResponse<PaginatedData<Personnel>>> {
    const cacheKey = createCacheKey('personnel_list', params as Record<string, unknown>)
    
    return deduplicateRequest<ApiResponse<PaginatedData<Personnel>>>(cacheKey, async () => {
      return withCache<ApiResponse<PaginatedData<Personnel>>>(
        cacheKey,
        async () => {
          const response = await request.get<PaginatedData<Personnel>>(API_ENDPOINTS.PERSONNEL.LIST, { params, signal })
          return response
        },
        300000
      )
    })
  },

  async getById(id: number, signal?: AbortSignal): Promise<ApiResponse<Personnel>> {
    return await request.get(API_ENDPOINTS.PERSONNEL.DETAIL(id), { signal })
  },

  async create(data: PersonnelCreate): Promise<ApiResponse<Personnel>> {
    const response = await request.post<Personnel>(API_ENDPOINTS.PERSONNEL.LIST, data)
    
    if (response.code === 200) {
      invalidateCache('personnel_')
    }
    
    return response
  },

  async update(id: number, data: PersonnelUpdate): Promise<ApiResponse<Personnel>> {
    const response = await request.put<Personnel>(API_ENDPOINTS.PERSONNEL.DETAIL(id), data)
    
    if (response.code === 200) {
      invalidateCache('personnel_')
    }
    
    return response
  },

  async delete(id: number): Promise<ApiResponse<null>> {
    const response = await request.delete<null>(API_ENDPOINTS.PERSONNEL.DETAIL(id))
    
    if (response.code === 200) {
      invalidateCache('personnel_')
    }
    
    return response
  },

  async getAll(signal?: AbortSignal): Promise<ApiResponse<Personnel[]>> {
    const cacheKey = 'personnel_all'
    
    return deduplicateRequest<ApiResponse<Personnel[]>>(cacheKey, async () => {
      return withCache<ApiResponse<Personnel[]>>(
        cacheKey,
        async () => {
          const response = await request.get<Personnel[]>(API_ENDPOINTS.PERSONNEL.ALL, { signal })
          return response
        },
        300000
      )
    })
  },
}

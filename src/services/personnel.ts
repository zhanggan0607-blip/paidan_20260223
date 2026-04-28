/**
 * 人员管理服务模块
 * 提供人员数据的增删改查接口
 */
import request from '../api/request'
import { API_ENDPOINTS } from '../api/endpoints'
import type { ApiResponse, PaginatedData, Personnel, PersonnelCreate, PersonnelUpdate } from '@sstcp/shared'
import { dataCache, deduplicateRequest } from '../utils/cache'

export type { Personnel } from '@sstcp/shared'
export type { PersonnelCreate } from '@sstcp/shared'
export type { PersonnelUpdate } from '@sstcp/shared'

export const personnelService = {
  /**
   * 获取人员列表（分页）
   */
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
    const cacheKey = `personnel_list_${JSON.stringify(params || {})}`
    
    const cached = dataCache.get<ApiResponse<PaginatedData<Personnel>>>(cacheKey)
    if (cached) {
      return cached
    }
    
    return deduplicateRequest<ApiResponse<PaginatedData<Personnel>>>(cacheKey, async () => {
      const response = await request.get<PaginatedData<Personnel>>(API_ENDPOINTS.PERSONNEL.LIST, { params, signal })
      
      if (response.code === 200) {
        dataCache.set(cacheKey, response, 300000)
      }
      
      return response
    })
  },

  /**
   * 获取人员详情
   */
  async getById(id: number, signal?: AbortSignal): Promise<ApiResponse<Personnel>> {
    return await request.get(API_ENDPOINTS.PERSONNEL.DETAIL(id), { signal })
  },

  /**
   * 创建人员
   */
  async create(data: PersonnelCreate): Promise<ApiResponse<Personnel>> {
    const response = await request.post<Personnel>(API_ENDPOINTS.PERSONNEL.LIST, data)
    
    if (response.code === 200) {
      dataCache.clear()
    }
    
    return response
  },

  /**
   * 更新人员
   */
  async update(id: number, data: PersonnelUpdate): Promise<ApiResponse<Personnel>> {
    const response = await request.put<Personnel>(API_ENDPOINTS.PERSONNEL.DETAIL(id), data)
    
    if (response.code === 200) {
      dataCache.clear()
    }
    
    return response
  },

  /**
   * 删除人员
   */
  async delete(id: number): Promise<ApiResponse<null>> {
    const response = await request.delete<null>(API_ENDPOINTS.PERSONNEL.DETAIL(id))
    
    if (response.code === 200) {
      dataCache.clear()
    }
    
    return response
  },

  /**
   * 获取所有人员（不分页）
   */
  async getAll(signal?: AbortSignal): Promise<ApiResponse<Personnel[]>> {
    const cacheKey = 'personnel_all'
    
    const cached = dataCache.get<ApiResponse<Personnel[]>>(cacheKey)
    if (cached) {
      return cached
    }
    
    return deduplicateRequest<ApiResponse<Personnel[]>>(cacheKey, async () => {
      const response = await request.get<Personnel[]>(API_ENDPOINTS.PERSONNEL.ALL, { signal })
      
      if (response.code === 200) {
        dataCache.set(cacheKey, response, 300000)
      }
      
      return response
    })
  },
}

/**
 * 数据字典服务
 * 提供数据字典的增删改查等功能
 */
import request from '../api/request'
import { API_ENDPOINTS } from '../api/endpoints'

export interface Dictionary {
  id: number
  dict_type: string
  dict_key: string
  dict_value: string
  dict_label: string
  sort_order: number
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface ApiResponse<T = unknown> {
  code: number
  message: string
  data: T
}

export interface PaginatedResponse {
  code: number
  message: string
  data: {
    content: Dictionary[]
    totalElements: number
    totalPages: number
    size: number
    number: number
    first: boolean
    last: boolean
  }
}

export const dictionaryService = {
  /**
   * 获取字典列表（分页）
   */
  async getList(params?: {
    page?: number
    size?: number
    dict_type?: string
  }): Promise<PaginatedResponse> {
    return await request.get(API_ENDPOINTS.DICTIONARY.LIST, { params })
  },

  /**
   * 根据类型获取字典
   */
  async getByType(dictType: string): Promise<ApiResponse<Dictionary[]>> {
    return await request.get(API_ENDPOINTS.DICTIONARY.BY_TYPE(dictType))
  },

  /**
   * 获取所有字典
   */
  async getAll(dictType?: string): Promise<ApiResponse<Dictionary[]>> {
    return await request.get('/dictionary/all/list', { params: { dict_type: dictType } })
  },

  /**
   * 获取字典详情
   */
  async getById(id: number): Promise<ApiResponse<Dictionary>> {
    return await request.get(API_ENDPOINTS.DICTIONARY.DETAIL(id))
  },

  /**
   * 创建字典
   */
  async create(data: {
    dict_type: string
    dict_key: string
    dict_value: string
    dict_label: string
    sort_order?: number
    is_active?: boolean
  }): Promise<ApiResponse<Dictionary>> {
    return await request.post(API_ENDPOINTS.DICTIONARY.LIST, data)
  },

  /**
   * 更新字典
   */
  async update(
    id: number,
    data: {
      dict_type?: string
      dict_key?: string
      dict_value?: string
      dict_label?: string
      sort_order?: number
      is_active?: boolean
    }
  ): Promise<ApiResponse<Dictionary>> {
    return await request.put(API_ENDPOINTS.DICTIONARY.DETAIL(id), data)
  },

  /**
   * 删除字典
   */
  async delete(id: number): Promise<ApiResponse<null>> {
    return await request.delete(API_ENDPOINTS.DICTIONARY.DETAIL(id))
  },
}

export const dictionaryTypes = {
  TEMPORARY_REPAIR_STATUS: 'temporary_repair_status',
  SPOT_WORK_STATUS: 'spot_work_status',
  PERIODIC_INSPECTION_STATUS: 'periodic_inspection_status',
  MAINTENANCE_PLAN_STATUS: 'maintenance_plan_status',
  MAINTENANCE_EXECUTION_STATUS: 'maintenance_execution_status',
  MAINTENANCE_PLAN_TYPE: 'maintenance_plan_type',
  SPARE_PARTS_STATUS: 'spare_parts_status',
} as const

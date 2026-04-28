import request from '../api/request'
import { API_ENDPOINTS } from '../api/endpoints'
import type { ApiResponse } from '@sstcp/shared'

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
  async getList(params?: {
    page?: number
    size?: number
    dict_type?: string
  }): Promise<PaginatedResponse> {
    return await request.get(API_ENDPOINTS.DICTIONARY.LIST, { params })
  },

  async getByType(dictType: string): Promise<ApiResponse<Dictionary[]>> {
    return await request.get(API_ENDPOINTS.DICTIONARY.BY_TYPE(dictType))
  },

  async getAll(dictType?: string): Promise<ApiResponse<Dictionary[]>> {
    return await request.get('/dictionary/all/list', { params: { dict_type: dictType } })
  },

  async getById(id: number): Promise<ApiResponse<Dictionary>> {
    return await request.get(API_ENDPOINTS.DICTIONARY.DETAIL(id))
  },

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

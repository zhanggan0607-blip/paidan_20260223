import request from '../api/request'
import { API_ENDPOINTS } from '../api/endpoints'
import type { ApiResponse, InspectionItem as BaseInspectionItem } from '@sstcp/shared'

export interface InspectionItem extends BaseInspectionItem {
  children?: InspectionItem[]
}

export interface InspectionItemCreate {
  item_code: string
  item_name: string
  item_type: string
  level?: number
  parent_id?: number | null
  check_content?: string
  check_standard?: string
  sort_order?: number
}

export interface InspectionItemUpdate {
  item_code?: string
  item_name?: string
  item_type?: string
  level?: number
  parent_id?: number | null
  check_content?: string
  check_standard?: string
  sort_order?: number
}

export interface PaginatedResponse {
  code: number
  message: string
  data: {
    content: InspectionItem[]
    totalElements: number
    totalPages: number
    size: number
    number: number
    first: boolean
    last: boolean
  }
}

export const inspectionItemService = {
  async getTree(): Promise<ApiResponse<InspectionItem[]>> {
    return await request.get(API_ENDPOINTS.INSPECTION_ITEM.TREE)
  },

  async getAll(): Promise<ApiResponse<InspectionItem[]>> {
    return await request.get(API_ENDPOINTS.INSPECTION_ITEM.ALL)
  },

  async getList(params?: {
    page?: number
    size?: number
    keyword?: string
  }): Promise<PaginatedResponse> {
    return await request.get(API_ENDPOINTS.INSPECTION_ITEM.LIST, { params })
  },

  async getById(id: number): Promise<ApiResponse<InspectionItem>> {
    return await request.get(API_ENDPOINTS.INSPECTION_ITEM.DETAIL(id))
  },

  async create(data: InspectionItemCreate): Promise<ApiResponse<InspectionItem>> {
    return await request.post(API_ENDPOINTS.INSPECTION_ITEM.LIST, data)
  },

  async update(id: number, data: InspectionItemUpdate): Promise<ApiResponse<InspectionItem>> {
    return await request.put(API_ENDPOINTS.INSPECTION_ITEM.DETAIL(id), data)
  },

  async delete(id: number): Promise<ApiResponse<null>> {
    return await request.delete(API_ENDPOINTS.INSPECTION_ITEM.DETAIL(id))
  },
}

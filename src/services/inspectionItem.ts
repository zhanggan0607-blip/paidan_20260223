/**
 * 巡检项服务
 * 提供巡检项的增删改查等功能
 */
import request from '../api/request'
import { API_ENDPOINTS } from '../api/endpoints'

export interface InspectionItem {
  id: number
  item_code: string
  item_name: string
  item_type: string
  level: number
  parent_id: number | null
  check_content: string | null
  check_standard: string | null
  sort_order: number
  children?: InspectionItem[]
  created_at: string
  updated_at: string
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

export interface ApiResponse<T = unknown> {
  code: number
  message: string
  data: T
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
  /**
   * 获取巡检项树形结构
   */
  async getTree(): Promise<ApiResponse<InspectionItem[]>> {
    return await request.get(API_ENDPOINTS.INSPECTION_ITEM.TREE)
  },

  /**
   * 获取所有巡检项
   */
  async getAll(): Promise<ApiResponse<InspectionItem[]>> {
    return await request.get(API_ENDPOINTS.INSPECTION_ITEM.ALL)
  },

  /**
   * 获取巡检项列表（分页）
   */
  async getList(params?: {
    page?: number
    size?: number
    keyword?: string
  }): Promise<PaginatedResponse> {
    return await request.get(API_ENDPOINTS.INSPECTION_ITEM.LIST, { params })
  },

  /**
   * 获取巡检项详情
   */
  async getById(id: number): Promise<ApiResponse<InspectionItem>> {
    return await request.get(API_ENDPOINTS.INSPECTION_ITEM.DETAIL(id))
  },

  /**
   * 创建巡检项
   */
  async create(data: InspectionItemCreate): Promise<ApiResponse<InspectionItem>> {
    return await request.post(API_ENDPOINTS.INSPECTION_ITEM.LIST, data)
  },

  /**
   * 更新巡检项
   */
  async update(id: number, data: InspectionItemUpdate): Promise<ApiResponse<InspectionItem>> {
    return await request.put(API_ENDPOINTS.INSPECTION_ITEM.DETAIL(id), data)
  },

  /**
   * 删除巡检项
   */
  async delete(id: number): Promise<ApiResponse<null>> {
    return await request.delete(API_ENDPOINTS.INSPECTION_ITEM.DETAIL(id))
  }
}

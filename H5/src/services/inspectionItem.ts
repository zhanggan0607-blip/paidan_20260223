/**
 * 巡检事项服务
 * 提供巡检事项的增删改查功能
 */
import request from '../api/request'
import { API_ENDPOINTS } from '../api/endpoints'
import type { ApiResponse, PaginatedResponse } from '../types/api'
import type { InspectionItem } from '../types/models'

export interface InspectionItemQueryParams {
  page?: number
  size?: number
  item_name?: string
  item_type?: string
}

export interface InspectionItemCreate {
  item_code: string
  item_name: string
  item_type?: string
  level: number
  parent_id?: number
  check_content?: string
  check_standard?: string
  sort_order?: number
}

export interface InspectionItemUpdate extends InspectionItemCreate {}

export const inspectionItemService = {
  /**
   * 获取巡检事项列表（分页）
   */
  async getList(params?: InspectionItemQueryParams): Promise<PaginatedResponse<InspectionItem>> {
    return request.get(API_ENDPOINTS.INSPECTION_ITEM.LIST, { params })
  },

  /**
   * 获取巡检事项详情
   */
  async getById(id: number): Promise<ApiResponse<InspectionItem>> {
    return request.get(API_ENDPOINTS.INSPECTION_ITEM.DETAIL(id))
  },

  /**
   * 获取所有巡检事项（不分页）
   */
  async getAll(): Promise<ApiResponse<InspectionItem[]>> {
    return request.get(API_ENDPOINTS.INSPECTION_ITEM.ALL)
  },

  /**
   * 获取巡检事项树形结构
   */
  async getTree(): Promise<ApiResponse<InspectionItem[]>> {
    return request.get(API_ENDPOINTS.INSPECTION_ITEM.TREE)
  },

  /**
   * 创建巡检事项
   */
  async create(data: InspectionItemCreate): Promise<ApiResponse<InspectionItem>> {
    return request.post(API_ENDPOINTS.INSPECTION_ITEM.LIST, data)
  },

  /**
   * 更新巡检事项
   */
  async update(id: number, data: InspectionItemUpdate): Promise<ApiResponse<InspectionItem>> {
    return request.put(API_ENDPOINTS.INSPECTION_ITEM.DETAIL(id), data)
  },

  /**
   * 删除巡检事项
   */
  async delete(id: number): Promise<ApiResponse<null>> {
    return request.delete(API_ENDPOINTS.INSPECTION_ITEM.DETAIL(id))
  },
}

export default inspectionItemService

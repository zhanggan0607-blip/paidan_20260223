/**
 * 备件使用服务
 * 提供备件使用记录查询功能
 */
import request from '../api/request'
import { API_ENDPOINTS } from '../api/endpoints'
import type { SparePartsUsage as SparePartsUsageType, ApiResponse } from '../types/api'

export type SparePartsUsage = SparePartsUsageType

export interface SparePartsUsageListResponse {
  items: SparePartsUsage[]
  total: number
}

export const sparePartsUsageService = {
  /**
   * 获取备件使用列表
   */
  async getList(params?: {
    page?: number
    pageSize?: number
    user?: string
    product?: string
    project?: string
  }): Promise<ApiResponse<SparePartsUsageListResponse>> {
    return await request.get(API_ENDPOINTS.SPARE_PARTS_USAGE.LIST, { params })
  },
}

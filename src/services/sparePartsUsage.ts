import apiClient from '../utils/api'
import type { SparePartsUsage as SparePartsUsageType, ApiResponse } from '../types/api'

export type SparePartsUsage = SparePartsUsageType

export interface SparePartsUsageListResponse {
  items: SparePartsUsage[]
  total: number
}

export const sparePartsUsageService = {
  async getList(params?: {
    page?: number
    pageSize?: number
    user?: string
    product?: string
    project?: string
  }): Promise<ApiResponse<SparePartsUsageListResponse>> {
    return await apiClient.get('/spare-parts/usage', { params })
  }
}

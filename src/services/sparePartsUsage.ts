import apiClient from '../utils/api'

export interface SparePartsUsage {
  id: number
  project_id: string
  projectName: string
  productName: string
  brand: string
  model: string
  quantity: number
  userName: string
  issueTime: string
  unit: string
}

export interface SparePartsUsageListResponse {
  items: SparePartsUsage[]
  total: number
}

export interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
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

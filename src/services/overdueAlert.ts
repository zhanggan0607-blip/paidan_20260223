import request from '../api/request'
import { API_ENDPOINTS } from '../api/endpoints'
import type { ApiResponse, OverdueAlertItem } from '@sstcp/shared'

export type OverdueItem = OverdueAlertItem

export interface OverdueAlertResponse {
  items: OverdueItem[]
  total: number
}

export const overdueAlertService = {
  async getOverdueAlerts(params?: {
    project_name?: string
    client_name?: string
    work_order_type?: string
    page?: number
    size?: number
  }): Promise<ApiResponse<OverdueAlertResponse>> {
    const queryParams = {
      page: 0,
      size: 1000,
      ...params,
    }
    return await request.get(API_ENDPOINTS.OVERDUE_ALERT.LIST, { params: queryParams })
  },
}

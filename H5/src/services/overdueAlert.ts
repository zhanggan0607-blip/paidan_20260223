/**
 * 超期提醒服务
 * 提供超期工单查询功能
 */
import request from '../api/request'
import { API_ENDPOINTS } from '../api/endpoints'
import type { ApiResponse } from '../types/api'
import type { OverdueAlertItem } from '../types/models'

export interface OverdueAlertResponse {
  items: OverdueAlertItem[]
  total: number
}

export interface OverdueAlertQueryParams {
  page?: number
  size?: number
  project_name?: string
  client_name?: string
  work_order_type?: string
}

export const overdueAlertService = {
  /**
   * 获取超期提醒列表
   */
  async getList(params?: OverdueAlertQueryParams): Promise<ApiResponse<OverdueAlertResponse>> {
    const queryParams = {
      page: 0,
      size: 1000,
      ...params
    }
    return request.get(API_ENDPOINTS.OVERDUE_ALERT.LIST, { params: queryParams })
  },
}

export default overdueAlertService

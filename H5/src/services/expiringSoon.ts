/**
 * 临期提醒服务
 * 提供临期工单查询功能
 */
import request from '../api/request'
import { API_ENDPOINTS } from '../api/endpoints'
import type { ApiResponse } from '../types/api'
import type { OverdueAlertItem } from '../types/models'

export interface ExpiringSoonResponse {
  items: OverdueAlertItem[]
  total: number
}

export interface ExpiringSoonQueryParams {
  page?: number
  size?: number
  project_name?: string
  client_name?: string
  work_order_type?: string
}

export const expiringSoonService = {
  /**
   * 获取临期提醒列表
   */
  async getList(params?: ExpiringSoonQueryParams): Promise<ApiResponse<ExpiringSoonResponse>> {
    const queryParams = {
      page: 0,
      size: 1000,
      ...params
    }
    return request.get(API_ENDPOINTS.EXPIRING_SOON.LIST, { params: queryParams })
  },
}

export default expiringSoonService

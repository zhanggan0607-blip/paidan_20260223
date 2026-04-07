/**
 * 工单服务
 * 提供工单聚合查询功能
 */
import request from '../api/request'
import { API_ENDPOINTS } from '../api/endpoints'
import type { ApiResponse } from '../types/api'

export interface CompletedWorkOrderItem {
  id: number
  order_id: string
  order_type: string
  order_type_code: string
  plan_type: string
  project_id: number | null
  project_name: string
  client_name: string | null
  plan_start_date: string | null
  plan_end_date: string | null
  actual_completion_date: string | null
  maintenance_personnel: string | null
  status: string
  remarks: string | null
  created_at: string | null
  updated_at: string | null
}

export interface CompletedWorkOrderResponse {
  items: CompletedWorkOrderItem[]
  total: number
  page: number
  size: number
}

export interface CompletedWorkOrderQueryParams {
  page?: number
  size?: number
}

export const workOrderService = {
  /**
   * 获取本年已完成的工单列表
   * 优化：后端直接过滤，减少数据传输量
   */
  async getCompletedThisYear(params?: CompletedWorkOrderQueryParams): Promise<ApiResponse<CompletedWorkOrderResponse>> {
    const queryParams = {
      page: 0,
      size: 20,
      ...params,
    }
    return request.get(API_ENDPOINTS.WORK_ORDER.COMPLETED_THIS_YEAR, { params: queryParams })
  },
}

export default workOrderService

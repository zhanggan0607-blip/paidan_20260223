/**
 * 工单服务
 * 提供工单统一查询功能
 */
import request from '../api/request'
import { API_ENDPOINTS } from '../api/endpoints'
import type { ApiResponse, PaginatedResponse } from '../types/api'
import type { WorkOrderItem, WorkOrderQueryParams } from '../types/models'

export const workOrderService = {
  /**
   * 获取工单列表（统一查询所有类型）
   */
  async getList(params?: WorkOrderQueryParams): Promise<PaginatedResponse<WorkOrderItem>> {
    return request.get(API_ENDPOINTS.WORK_ORDER.LIST, { params })
  },

  /**
   * 获取工单详情
   */
  async getById(id: number, type: string): Promise<ApiResponse<WorkOrderItem>> {
    return request.get(API_ENDPOINTS.WORK_ORDER.DETAIL(id, type))
  },
}

export default workOrderService

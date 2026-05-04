/**
 * 工单服务
 * 提供工单聚合查询功能
 */
import request from '../api/request'
import { API_ENDPOINTS } from '../api/endpoints'
import type { ApiResponse, PaginatedData, WorkOrderItem, WorkOrderQueryParams } from '../types/api'

export const workOrderService = {
  async getCompletedThisYear(params?: WorkOrderQueryParams): Promise<ApiResponse<PaginatedData<WorkOrderItem>>> {
    const queryParams = {
      page: 0,
      size: 20,
      ...params,
    }
    return request.get(API_ENDPOINTS.WORK_ORDER.COMPLETED_THIS_YEAR, { params: queryParams })
  },
}

export default workOrderService

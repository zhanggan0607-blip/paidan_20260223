/**
 * 操作日志服务
 * 提供工单操作日志查询功能
 */
import request from '@/api/request'
import { API_ENDPOINTS } from '@sstcp/shared'
import type { ApiResponse, OperationLog } from '@/types/api'

/**
 * 操作日志查询参数
 */
export interface OperationLogQueryParams {
  work_order_type: string
  work_order_id: number
}

/**
 * 操作日志服务对象
 */
export const operationLogService = {
  /**
   * 根据工单类型和ID获取操作日志列表
   * @param params 查询参数
   * @returns 操作日志列表
   */
  async getByWorkOrder(params: OperationLogQueryParams): Promise<ApiResponse<OperationLog[]>> {
    return request.get(API_ENDPOINTS.WORK_ORDER_OPERATION_LOG.LIST, { params })
  },
}

export default operationLogService

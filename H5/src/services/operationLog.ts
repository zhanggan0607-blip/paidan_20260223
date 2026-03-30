/**
 * 操作日志服务
 * 提供工单操作日志查询功能
 */
import request from '../api/request'
import { API_ENDPOINTS } from '../api/endpoints'
import type { ApiResponse } from '../types/api'
import type { OperationLog } from '../types/models'

/**
 * 操作日志查询参数
 */
export interface OperationLogQueryParams {
  work_order_type: string
  work_order_id: number
}

/**
 * 创建操作日志请求
 */
export interface OperationLogCreate {
  work_order_type: string
  work_order_id: number
  work_order_no: string
  operator_name: string
  operator_id: number
  operation_type_code: string
  operation_remark?: string
}

export const operationLogService = {
  /**
   * 根据工单类型和ID获取操作日志列表
   */
  async getByWorkOrder(params: OperationLogQueryParams): Promise<ApiResponse<OperationLog[]>> {
    return request.get(API_ENDPOINTS.WORK_ORDER_OPERATION_LOG.LIST, { params })
  },

  /**
   * 创建操作日志
   */
  async create(data: OperationLogCreate): Promise<ApiResponse<OperationLog>> {
    return request.post(API_ENDPOINTS.WORK_ORDER_OPERATION_LOG.CREATE, data)
  },
}

export default operationLogService

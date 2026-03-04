/**
 * 操作类型服务
 * 提供操作类型的查询功能
 */
import request from '../api/request'
import { API_ENDPOINTS } from '../api/endpoints'
import type { ApiResponse } from '../types/api'

export interface OperationType {
  id: number
  code: string
  name: string
  description?: string
  created_at: string
  updated_at: string
}

export const operationTypeService = {
  /**
   * 获取操作类型列表
   */
  async getList(): Promise<ApiResponse<OperationType[]>> {
    return request.get(API_ENDPOINTS.OPERATION_TYPE.LIST)
  },

  /**
   * 获取操作类型详情
   */
  async getById(id: number): Promise<ApiResponse<OperationType>> {
    return request.get(API_ENDPOINTS.OPERATION_TYPE.DETAIL(id))
  },

  /**
   * 根据编码获取操作类型
   */
  async getByCode(code: string): Promise<ApiResponse<OperationType>> {
    return request.get(API_ENDPOINTS.OPERATION_TYPE.BY_CODE(code))
  },
}

export default operationTypeService

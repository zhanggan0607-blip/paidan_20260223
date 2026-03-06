/**
 * 定期巡检服务
 * 提供定期巡检工单的增删改查等功能
 */
import request from '../api/request'
import { API_ENDPOINTS } from '../api/endpoints'
import type { PeriodicInspection as PeriodicInspectionType, ApiResponse } from '../types/api'

export type PeriodicInspection = PeriodicInspectionType

export interface PeriodicInspectionCreate {
  inspection_id: string
  plan_id?: string
  project_id: string
  project_name: string
  plan_start_date: string
  plan_end_date: string
  client_name?: string
  maintenance_personnel?: string
  status?: string
  filled_count?: number
  total_count?: number
  execution_result?: string
  remarks?: string
  signature?: string
}

export interface PeriodicInspectionUpdate {
  inspection_id: string
  plan_id?: string
  project_id: string
  project_name: string
  plan_start_date: string
  plan_end_date: string
  client_name?: string
  maintenance_personnel?: string
  status: string
  filled_count?: number
  total_count?: number
  execution_result?: string
  remarks?: string
  signature?: string
}

export interface PeriodicInspectionPaginatedResponse {
  code: number
  message: string
  data: {
    content: PeriodicInspection[]
    totalElements: number
    totalPages: number
    size: number
    number: number
    first: boolean
    last: boolean
  }
}

export const periodicInspectionService = {
  /**
   * 获取定期巡检列表（分页）
   */
  async getList(params?: {
    page?: number
    size?: number
    project_name?: string
    client_name?: string
    inspection_id?: string
    status?: string
  }): Promise<PeriodicInspectionPaginatedResponse> {
    return await request.get(API_ENDPOINTS.PERIODIC_INSPECTION.LIST, { params })
  },

  /**
   * 获取定期巡检详情
   */
  async getById(id: number): Promise<ApiResponse<PeriodicInspection>> {
    return await request.get(API_ENDPOINTS.PERIODIC_INSPECTION.DETAIL(id))
  },

  /**
   * 创建定期巡检
   */
  async create(data: PeriodicInspectionCreate): Promise<ApiResponse<PeriodicInspection>> {
    return await request.post(API_ENDPOINTS.PERIODIC_INSPECTION.LIST, data)
  },

  /**
   * 更新定期巡检
   */
  async update(
    id: number,
    data: PeriodicInspectionUpdate
  ): Promise<ApiResponse<PeriodicInspection>> {
    return await request.put(API_ENDPOINTS.PERIODIC_INSPECTION.DETAIL(id), data)
  },

  /**
   * 删除定期巡检
   */
  async delete(id: number): Promise<ApiResponse<null>> {
    return await request.delete(API_ENDPOINTS.PERIODIC_INSPECTION.DETAIL(id))
  },

  /**
   * 获取所有定期巡检（不分页）
   */
  async getAll(): Promise<ApiResponse<PeriodicInspection[]>> {
    return await request.get(API_ENDPOINTS.PERIODIC_INSPECTION.ALL)
  },
}

/**
 * 定期巡检服务
 * 提供定期巡检工单的增删改查等功能
 */
import request from '../api/request'
import { API_ENDPOINTS } from '../api/endpoints'
import type { ApiResponse, PaginatedData } from '@sstcp/shared'

export interface PeriodicInspection {
  id: number
  inspection_id: string
  plan_id?: string
  project_id: string
  project_name: string
  plan_start_date: string
  plan_end_date: string
  client_name?: string
  client_contact?: string
  client_contact_info?: string
  client_contact_position?: string
  address?: string
  maintenance_personnel?: string
  status: string
  filled_count?: number
  total_count?: number
  execution_result?: string
  remarks?: string
  signature?: string
  photos?: string
  created_at: string
  updated_at: string
}

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

export const periodicInspectionService = {
  /**
   * 获取定期巡检列表（分页）
   */
  async getList(
    params?: {
      page?: number
      size?: number
      project_name?: string
      client_name?: string
      inspection_id?: string
      status?: string
    },
    signal?: AbortSignal
  ): Promise<ApiResponse<PaginatedData<PeriodicInspection>>> {
    return await request.get(API_ENDPOINTS.PERIODIC_INSPECTION.LIST, { params, signal })
  },

  /**
   * 获取定期巡检详情
   */
  async getById(id: number, signal?: AbortSignal): Promise<ApiResponse<PeriodicInspection>> {
    return await request.get(API_ENDPOINTS.PERIODIC_INSPECTION.DETAIL(id), { signal })
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
  async getAll(signal?: AbortSignal): Promise<ApiResponse<PeriodicInspection[]>> {
    return await request.get(API_ENDPOINTS.PERIODIC_INSPECTION.ALL, { signal })
  },
}

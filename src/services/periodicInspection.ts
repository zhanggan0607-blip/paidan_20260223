/**
 * 定期巡检服务
 * 提供定期巡检工单的增删改查等功能
 */
import request from '../api/request'
import { API_ENDPOINTS } from '../api/endpoints'
import type { ApiResponse, PaginatedData, PeriodicInspection, PeriodicInspectionCreate, PeriodicInspectionUpdate } from '@sstcp/shared'

export type { PeriodicInspection } from '@sstcp/shared'
export type { PeriodicInspectionCreate } from '@sstcp/shared'
export type { PeriodicInspectionUpdate } from '@sstcp/shared'

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
   * 部分更新定期巡检
   */
  async patch(
    id: number,
    data: Partial<PeriodicInspectionUpdate>
  ): Promise<ApiResponse<PeriodicInspection>> {
    return await request.patch(API_ENDPOINTS.PERIODIC_INSPECTION.DETAIL(id), data)
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

  async submit(id: number): Promise<ApiResponse<PeriodicInspection>> {
    return await request.post(API_ENDPOINTS.PERIODIC_INSPECTION.SUBMIT(id))
  },

  async recall(id: number): Promise<ApiResponse<PeriodicInspection>> {
    return await request.post(API_ENDPOINTS.PERIODIC_INSPECTION.RECALL(id))
  },
}

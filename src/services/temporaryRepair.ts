/**
 * 临时维修服务
 * 提供临时维修工单的增删改查等功能
 */
import request from '../api/request'
import { API_ENDPOINTS } from '../api/endpoints'
import type { ApiResponse, PaginatedData, TemporaryRepair, TemporaryRepairCreate, TemporaryRepairUpdate } from '@sstcp/shared'

export type { TemporaryRepair } from '@sstcp/shared'
export type { TemporaryRepairCreate } from '@sstcp/shared'
export type { TemporaryRepairUpdate } from '@sstcp/shared'

export const temporaryRepairService = {
  /**
   * 获取临时维修列表（分页）
   */
  async getList(params?: {
    page?: number
    size?: number
    project_name?: string
    repair_id?: string
    status?: string
  }): Promise<ApiResponse<PaginatedData<TemporaryRepair>>> {
    return await request.get(API_ENDPOINTS.TEMPORARY_REPAIR.LIST, { params })
  },

  /**
   * 获取所有临时维修（不分页）
   */
  async getAll(): Promise<ApiResponse<TemporaryRepair[]>> {
    return await request.get(API_ENDPOINTS.TEMPORARY_REPAIR.ALL)
  },

  async generateId(projectId: string): Promise<ApiResponse<{ repair_id: string }>> {
    return await request.get(API_ENDPOINTS.TEMPORARY_REPAIR.GENERATE_ID, { params: { project_id: projectId } })
  },

  /**
   * 获取临时维修详情
   */
  async getById(id: number): Promise<ApiResponse<TemporaryRepair>> {
    return await request.get(API_ENDPOINTS.TEMPORARY_REPAIR.DETAIL(id))
  },

  /**
   * 创建临时维修
   */
  async create(data: TemporaryRepairCreate): Promise<ApiResponse<TemporaryRepair>> {
    return await request.post(API_ENDPOINTS.TEMPORARY_REPAIR.LIST, data)
  },

  /**
   * 更新临时维修
   */
  async update(id: number, data: TemporaryRepairUpdate): Promise<ApiResponse<TemporaryRepair>> {
    return await request.put(API_ENDPOINTS.TEMPORARY_REPAIR.DETAIL(id), data)
  },

  /**
   * 部分更新临时维修
   */
  async patch(
    id: number,
    data: Partial<TemporaryRepairUpdate>
  ): Promise<ApiResponse<TemporaryRepair>> {
    return await request.patch(API_ENDPOINTS.TEMPORARY_REPAIR.DETAIL(id), data)
  },

  /**
   * 删除临时维修
   */
  async delete(id: number): Promise<ApiResponse<null>> {
    return await request.delete(API_ENDPOINTS.TEMPORARY_REPAIR.DETAIL(id))
  },

  async submit(id: number): Promise<ApiResponse<TemporaryRepair>> {
    return await request.post(API_ENDPOINTS.TEMPORARY_REPAIR.SUBMIT(id))
  },

  async recall(id: number): Promise<ApiResponse<TemporaryRepair>> {
    return await request.post(API_ENDPOINTS.TEMPORARY_REPAIR.RECALL(id))
  },
}
